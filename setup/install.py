# Databricks notebook source
# MAGIC %md
# MAGIC # Install protein folding models
# MAGIC Runs on serverless

# COMMAND ----------

# MAGIC %pip install pyyaml
# MAGIC %restart_python

# COMMAND ----------

# MAGIC %md
# MAGIC # Set a few choices for install: 
# MAGIC  - email (for updates on install)
# MAGIC  - cloud (azure and aws currently supported)
# MAGIC  - download_af2_datasets
# MAGIC    - these are large, but are required for AF2
# MAGIC    - If true, download all datasets required - but, we do not include download 
# MAGIC      of the full BFD even if set to True, opting to use bfd_small only for that
# MAGIC      dataset expecting only very minor performance degradation with much faster inference.

# COMMAND ----------

email = ""
cloud = 'azure' # can also be aws
download_af2_datasets = False

# COMMAND ----------

# spark.sql("CREATE CATALOG IF NOT EXISTS protein_folding")
for model in ['alphafold','proteinmpnn','boltz','esmfold','rfdiffusion']:
    spark.sql(f"CREATE SCHEMA IF NOT EXISTS protein_folding.{model}")
spark.sql("CREATE VOLUME IF NOT EXISTS protein_folding.alphafold.datasets")
spark.sql("CREATE VOLUME IF NOT EXISTS protein_folding.alphafold.results")

# COMMAND ----------

compute_mapping = {
    'azure': {
        'Standard_NC4as_T4_v3': 'Standard_NC4as_T4_v3',
        'Standard_D4ds_v5': 'Standard_D4ds_v5'
    },
    'aws': {
        'Standard_NC4as_T4_v3': 'g4dn.2xlarge',
        'Standard_D4ds_v5': 'm5.xlarge'
    },
}

af2_compute_mapping = {
  'azure': {
      'fold_compute' : "Standard_NC4as_T4_v3",
      'featurize_compute' : "Standard_F8"
  },
  'aws': {
      'fold_compute' : "g4dn.2xlarge",
      'featurize_compute' : "c4.2xlarge"
  }
}

# COMMAND ----------

# MAGIC %md
# MAGIC ### Make the AF2 workflow ready to be run as needed later

# COMMAND ----------

import re
from pathlib import Path

notebook_path = dbutils.notebook.entry_point.getDbutils().notebook().getContext().notebookPath().get()
directory_path = '/'.join(notebook_path.split('/')[:-1])

# COMMAND ----------

from databricks.sdk import WorkspaceClient
from databricks.sdk.service.jobs import JobSettings
from typing import Optional
import yaml

def create_job_from_yaml(yaml_path: Optional[str] = None, yaml_str: Optional[str] = None):
    if yaml_path is not None:
        with open(yaml_path) as f:
            config = yaml.safe_load(f)
    elif yaml_str is not None:
        config = yaml.safe_load(yaml_str)
    else:
        raise ValueError("Either yaml_path or yaml_str must be provided")
    
    outer_name = [k for k in config['resources']['jobs'].keys()][0]
  
    # Full job settings deserialization
    job_settings = JobSettings.from_dict(config['resources']['jobs'][outer_name])
    
    # instantiate the client
    w = WorkspaceClient()
    
    # create a job just with name
    creation_info = w.jobs.create(name='new created job')
    # now use job settings object to populate
    w.jobs.reset(
        job_id=creation_info.job_id,
        new_settings=job_settings,
    )
    return creation_info.job_id

# COMMAND ----------


default_yaml_path = "/Workspace"+directory_path+"/../tutorials/alphafold"+"/workflow/resources/example_workflow_setup.yaml"
af_notebooks_path = str(Path("/Workspace"+directory_path+"/../tutorials/alphafold"+"/workflow/notebooks").resolve())


fold_compute = af2_compute_mapping[cloud]['fold_compute']
featurize_compute = af2_compute_mapping[cloud]['featurize_compute']

with open(default_yaml_path, 'r') as file:
    yaml_content = file.read()

updated_yaml_content = re.sub(r'<email>', email, yaml_content)
updated_yaml_content = re.sub(r'<notebooks_path>', af_notebooks_path, updated_yaml_content)
updated_yaml_content = re.sub(r'<fold_compute>', fold_compute, updated_yaml_content)
updated_yaml_content = re.sub(r'<featurize_compute>', featurize_compute, updated_yaml_content)

try:
    job_id = create_job_from_yaml(yaml_str = updated_yaml_content)
    print(f"Created job {job_id}")
except Exception as e:
    print(f"Job creation failed: {e}")

# COMMAND ----------

# MAGIC %md
# MAGIC # Now install all the models for serving and make the App

# COMMAND ----------

default_yaml_path = "/Workspace"+directory_path+"/install.yaml"

base_path = str(Path("/Workspace"+directory_path+"/../tutorials").resolve())

print(default_yaml_path)
print(base_path)

# COMMAND ----------


with open(default_yaml_path, 'r') as file:
    yaml_content = file.read()

updated_yaml_content = re.sub(r'<email>', email, yaml_content)
updated_yaml_content = re.sub(r'<root_path>', base_path, updated_yaml_content)
for c0,c1 in compute_mapping[cloud].items():
  updated_yaml_content = re.sub(c0, c1, updated_yaml_content)

# COMMAND ----------

try:
    job_id = create_job_from_yaml(yaml_str = updated_yaml_content)
    print(f"Created job {job_id}")
except Exception as e:
    print(f"Job creation failed: {e}")

# COMMAND ----------

# MAGIC %md
# MAGIC #### Run the workflow we just made
# MAGIC  - this will actually download model weights, create registered models and serve them
# MAGIC  - this will timeout in notebook (but the actual workflow job will not)

# COMMAND ----------

w = WorkspaceClient()
try:
  # run_by_id = w.jobs.run_now(job_id=job_id).result()
  w.jobs.run_now(job_id=job_id)
except TimeoutError:
  # expect 20min timeout on notebook call - the actual workflow will still run fine
  pass

# could use and_wait on run_now_and_wait but may just timeout due to taking a while, consider...
# clean up the no longer needed job once complete
# w.jobs.delete(job_id=job_id)

# COMMAND ----------

# MAGIC %md
# MAGIC ### Lastly, if requested, create and run workflow to download datasets for alpahfold2

# COMMAND ----------

default_yaml_path = str(Path("/Workspace"+directory_path+"/../tutorials/alphafold"+"/downloads/resources/downloads_workflow.yaml").resolve())
afdl_notebooks_path = str(Path("/Workspace"+directory_path+"/../tutorials/alphafold"+"/downloads/notebooks").resolve())
with open(default_yaml_path, 'r') as file:
    yaml_content = file.read()

updated_yaml_content = re.sub(r'<email>', email, yaml_content)
updated_yaml_content = re.sub(r'<notebooks_path>', afdl_notebooks_path, updated_yaml_content)
for c0,c1 in compute_mapping[cloud].items():
  updated_yaml_content = re.sub(c0, c1, updated_yaml_content)
  
try:
    job_id = create_job_from_yaml(yaml_str = updated_yaml_content)
    print(f"Created job {job_id}")
except Exception as e:
    print(f"Job creation failed: {e}")

if download_af2_datasets:
  w = WorkspaceClient()
  try:
    # run_by_id = w.jobs.run_now(job_id=job_id).result()
    w.jobs.run_now(job_id=job_id)
  except TimeoutError:
    # expect 20min timeout on notebook call - the actual workflow will still run fine
    pass

# COMMAND ----------


