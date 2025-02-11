# Databricks notebook source
# MAGIC %md
# MAGIC ### Searching workflow runs via Databricks SDK
# MAGIC
# MAGIC  - docs: [sdk](https://databricks-sdk-py.readthedocs.io/en/latest/workspace/jobs/jobs.html), [api](https://docs.databricks.com/api/workspace/jobs/listruns)
# MAGIC
# MAGIC  - can easily profile active, queued, runs using SDK (or the API)
# MAGIC  - Workflows page provides most of this info and ability to set alerts, but could make niche alerts etc via SDK 
# MAGIC  - Could replicate HPC commands to check queue, eg qstat etc
# MAGIC
# MAGIC ### Submission
# MAGIC
# MAGIC  - job runs can also be submitted by:
# MAGIC    1. Python SDK ; or,
# MAGIC    2. API ; or,
# MAGIC    3. In the workflows UI page (for those who are less code familiar) ; or, 
# MAGIC    4. In a Databricks app (that uses the SDK under the hood)
# MAGIC
# MAGIC  - This setuo allows power users and bench scientist to both get to interact with the model in the way most approprate for them.

# COMMAND ----------

import os
import time
from databricks.sdk import WorkspaceClient
from databricks.sdk.service import jobs
from collections import Counter

w = WorkspaceClient()

# COMMAND ----------

def get_job_id(job_name : str ='alphafold'):
    """ get the job_id of job with name job_name """
    job_iter = w.jobs.list()
    found_jobs = [j for j in job_iter if j.as_dict()['settings'].get('name')==job_name]
    if len(found_jobs)==1:
        found_job = found_jobs[0]
    if len(found_jobs)==0:
            raise ValueError("No job with name", job_name)
        else:
            raise NotImplementedError("Multiple jobs with the same name found", [j.job_id for j in found_jobs])
    return found_job.job_id

def count_active_runs(job_id):
    """ count the number of active runs of the job 
    Active includes: QUEUED, PENDING, RUNNING, or TERMINATING
    """
    runs_iter = w.jobs.list_runs(job_id=job_id, active_only=True)
    return sum(1 for r in runs_iter)

def run_status_counts(job_id):
    """ count the number of runs in each state 
    For terminated runs, instead count by the final state
    """
    runs_iter = w.jobs.list_runs(job_id=job_id)
    states = Counter()
    for r in runs_iter:
        state_ = r.state.life_cycle_state._name_
        if state_=='TERMINATED':
            final_state_ = r.state.result_state._name_
            states[final_state_] += 1 
        else:
            states[state_] += 1 
    return states

def run_alphafold(protein_name, protein_sequence):
    job_id = get_job_id()
    run_id = w.jobs.run_now(
        job_id=job_id,
        job_parameters = {
            'protein':'CASNYT',
            'run_name':'my_small_protein'
        }
    )
    return run_id

def get_run_status(run_id):
    run = w.jobs.get_run(run_id = run_id)
    print(run.state.life_cycle_state)
    return run

job_id = get_job_id()

# COMMAND ----------

# MAGIC %md
# MAGIC ### Start alphafold run
# MAGIC
# MAGIC  - can be incorporated into scripts, apps etc
# MAGIC  - use like qsub 

# COMMAND ----------

run_id = run_alphafold(protein_name, protein_sequence)

# use run_id to check run status etc
run = get_run_status(run_id)

# COMMAND ----------

# MAGIC %md
# MAGIC ### Check how many active jobs, how many prior successes etc

# COMMAND ----------

run_status_counts(job_id)

# COMMAND ----------

count_active_runs(job_id)
