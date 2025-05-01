# Databricks notebook source
# MAGIC %md
# MAGIC This will:
# MAGIC  - delete AF2 workflow (get id by name) (install workflow will be deleted following successful run)
# MAGIC  - delete model serving endpoints by name
# MAGIC  - delete the catalog

# COMMAND ----------

# delete the catalog "protein folding" and schemas in it etc too
# CAREFUL - all downloaded datasets and logs are in here...
# spark.sql("DROP CATALOG `protein_folding` CASCADE")

# more minimal deletes by schema, e.g :
spark.sql("DROP SCHEMA IF EXISTS `protein_folding`.`esmfold` CASCADE")
spark.sql("DROP SCHEMA IF EXISTS `protein_folding`.`rfdiffusion` CASCADE")
spark.sql("DROP SCHEMA IF EXISTS `protein_folding`.`proteinmpnn` CASCADE")
spark.sql("DROP SCHEMA IF EXISTS `protein_folding`.`boltz` CASCADE")

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

# delete the app
w.apps.delete('protein-folding')

# COMMAND ----------


