# Databricks notebook source
# MAGIC %md
# MAGIC ### Create an app for protein folding
# MAGIC  - the source code for the app is in the /src directory here.
# MAGIC  - the app needs permissions to run the alphafold workflow and esmfold serving endpoint
# MAGIC    - If you did not setup the ESMfold serving endpoint or alphafold job, parts of the app will not work
# MAGIC  - We use the python SDK to start up the app compute using the pre-made app code placed in src here

# COMMAND ----------

# MAGIC %pip install --upgrade databricks-sdk
# MAGIC dbutils.library.restartPython()

# COMMAND ----------

import shutil
import os
from databricks.sdk.service.apps import (
    App, 
    AppsAPI, 
    AppResource, 
    AppResourceJob,
    AppResourceJobJobPermission,
    AppResourceServingEndpoint,
    AppResourceServingEndpointServingEndpointPermission,
    AppDeployment,
    AppDeploymentArtifacts
)
from databricks.sdk import WorkspaceClient
w = WorkspaceClient()

# COMMAND ----------

# helper to get the id of the alphafold job
def get_job_id(job_name : str ='alphafold'):
    """ get the job_id of job with name job_name """
    job_iter = w.jobs.list()
    found_jobs = [j for j in job_iter if j.as_dict()['settings'].get('name')==job_name]
    if len(found_jobs)==1:
        found_job = found_jobs[0]
    else:
        if len(found_jobs)==0:
            raise ValueError("No job with name", job_name)
        else:
            raise NotImplementedError("Multiple jobs with the same name found", [j.job_id for j in found_jobs])
    return found_job.job_id

# make a resource that will allow the app to access the alphafold job
af2_resource = AppResource(
    name = 'job',
    job = AppResourceJob(
        id = get_job_id(),
        permission = AppResourceJobJobPermission["CAN_MANAGE_RUN"]
    )
)

# make a resource that will allow the app to access the esmfold serving endpoint
esmfold_resource = AppResource(
    name = 'serving-endpoint',
    serving_endpoint=AppResourceServingEndpoint(
        name = 'esmfold',
        permission = AppResourceServingEndpointServingEndpointPermission['CAN_QUERY']
    )
)
notebook_path = dbutils.notebook.entry_point.getDbutils().notebook().getContext().notebookPath().get()
src_dir = '/Workspace'+'/'.join(notebook_path.split('/')[:-1])+'/src'
# create the app object
my_app = App(
    name = 'protein-folding',
    default_source_code_path=src_dir,
    description = "protein folding app",
    resources = [
        af2_resource,
        esmfold_resource
    ],
)

# COMMAND ----------

w.apps.create_and_wait(app=my_app)
deployment = w.apps.deploy_and_wait(
    app_name=my_app.name,
    app_deployment=AppDeployment(
        source_code_path=src_dir, 
    )
)

# COMMAND ----------

a = w.apps.get(name=my_app.name)

# COMMAND ----------

a.service_principal_name

# COMMAND ----------

# MAGIC %md
# MAGIC # this errors out right now - I think the service principal is created at metastore not workspace and this can create issues?
# MAGIC  - it works to do it in UI (needs workspace admin?)

# COMMAND ----------

# assign read permissions on protein_folding.alphafold.datasets and protein_folding.alphafold.results with sql statements
spark.sql(f"GRANT USE CATALOG ON CATALOG protein_folding TO `{a.service_principal_name}`")
spark.sql(f"GRANT USE SCHEMA ON SCHEMA protein_folding.alphafold TO `{a.service_principal_name}`")
spark.sql(f"GRANT READ VOLUME ON VOLUME protein_folding.alphafold.datasets TO `{a.service_principal_name}`")
spark.sql(f"GRANT READ VOLUME ON VOLUME protein_folding.alphafold.results TO `{a.service_principal_name}`")

# COMMAND ----------


