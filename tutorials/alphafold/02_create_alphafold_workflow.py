# Databricks notebook source
# MAGIC %md
# MAGIC ### Create the specification of a workflow job for alphafold
# MAGIC  - put your email below to recieve notifications in the workflow (you can add more emails later in the UI if desired)
# MAGIC  - run this notebook
# MAGIC  - copy the yaml output in the last cell
# MAGIC  - navigate to "workflows" on the left panel
# MAGIC  - click "create job"
# MAGIC  - In the top right click the kebab menu (three vertical dots) and select "switch to code version (YAML)"
# MAGIC  - paste the yaml below, then hit save
# MAGIC  - in the upper right, hit "switch to visual mode"
# MAGIC  - your alphafold pipeline is now ready - you cna make submissions
# MAGIC    - you can click the arrow next to run and select "run now with different parameters"
# MAGIC    - or run programatically as shown in the next notebook
# MAGIC

# COMMAND ----------

# MAGIC %pip install pyyaml
# MAGIC %restart_python

# COMMAND ----------

email = "me@org.com"

# For Azure
fold_compute = "Standard_NC4as_T4_v3"
featurize_compute = "Standard_F8"


notebook_path = dbutils.notebook.entry_point.getDbutils().notebook().getContext().notebookPath().get()
directory_path = '/'.join(notebook_path.split('/')[:-1])
default_yaml_path = "/Workspace"+directory_path+"/workflow/resources/example_workflow_setup.yaml"
af_notebooks_path = "/Workspace"+directory_path+"/workflow/notebooks"

# COMMAND ----------

import re
with open(default_yaml_path, 'r') as file:
    yaml_content = file.read()

updated_yaml_content = re.sub(r'<email>', email, yaml_content)
updated_yaml_content = re.sub(r'<notebooks_path>', af_notebooks_path, updated_yaml_content)
updated_yaml_content = re.sub(r'<fold_compute>', fold_compute, updated_yaml_content)
updated_yaml_content = re.sub(r'<featurize_compute>', featurize_compute, updated_yaml_content)

print(updated_yaml_content)

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

try:
    job_id = create_job_from_yaml(yaml_str = updated_yaml_content)
    print(f"Created job {job_id}")
except Exception as e:
    print(f"Job creation failed: {e}")

# COMMAND ----------


