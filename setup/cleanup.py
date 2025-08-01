# Databricks notebook source
# MAGIC %md
# MAGIC ## Clear an existing install
# MAGIC  - Note, this will delete entire schemas including generated results in the alphafold schema
# MAGIC  - If you wish to remove assets associated with the acceperator but retain your results, either modify this notebook or first copy the data you wish to retain to another location.

# COMMAND ----------

# MAGIC %md
# MAGIC This will:
# MAGIC  - delete AF2 workflow (get id by name) (install workflow will be deleted following successful run)
# MAGIC  - delete model serving endpoints by name
# MAGIC  - delete the protein_folding catalog and all contents
# MAGIC    - you could instead do per schema deletions (see commented code)

# COMMAND ----------

# delete the catalog "protein folding" and schemas in it etc too
# CAREFUL - all downloaded datasets and logs are in here...

spark.sql("DROP CATALOG `protein_folding` CASCADE")

# more minimal deletes by schema, e.g :
# spark.sql("DROP SCHEMA IF EXISTS `protein_folding`.`esmfold` CASCADE")
# spark.sql("DROP SCHEMA IF EXISTS `protein_folding`.`rfdiffusion` CASCADE")
# spark.sql("DROP SCHEMA IF EXISTS `protein_folding`.`proteinmpnn` CASCADE")
# spark.sql("DROP SCHEMA IF EXISTS `protein_folding`.`boltz` CASCADE")

# COMMAND ----------

# MAGIC %md
# MAGIC ### Now remove model serving endpoints

# COMMAND ----------

from databricks.sdk import WorkspaceClient
w = WorkspaceClient()

models = [
  'esmfold',
  'proteinmpnn',
  'rfdiffusion_unconditional',
  'rfdiffusion_inpainting',
  'boltz',
]
# now delete the endpoint using sdk for each model name (= endpoint_name)
for m in models:
    # Assuming `client` is an instance of the SDK client
    try:
      w.serving_endpoints.delete(name=m)
    except Exception as e:
      print(f"Error deleting endpoint {m}: {e}")
      pass


# COMMAND ----------

# MAGIC %md
# MAGIC ### Now remove the alphafold job

# COMMAND ----------

job_name='alphafold'
job_iter = w.jobs.list()
found_jobs = [j for j in job_iter if j.as_dict()['settings'].get('name')==job_name]
if len(found_jobs)==0:
    print("WARNIG: No job with name "+job_name+" found")
if not len(found_jobs)==1:
    print("WARNING: Multiple jobs with the same name found")

if len(found_jobs)>0:
  found_job = found_jobs[0]
  print(found_job)
  w.jobs.delete(found_job.job_id)

# COMMAND ----------

# MAGIC %md
# MAGIC ### Now remove the app

# COMMAND ----------

# delete the app
w.apps.delete('protein-folding')

# COMMAND ----------


