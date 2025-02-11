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


