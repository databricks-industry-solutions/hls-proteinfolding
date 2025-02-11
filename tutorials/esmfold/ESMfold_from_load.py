# Databricks notebook source
# MAGIC %md
# MAGIC ### Pull in our model from Unity Catalog
# MAGIC  - Any user with execute **permissions on the model** can load it in from **Unity Catalog** use it like this
# MAGIC  - The users don't need to know about internals of the model, or have permsissions to pull the model from the web (we pre-downlaoded the weights and store with the model)
# MAGIC  - If you want to ensure users' usage of a model is tracked - you can allow them to use only a serving endpoint of the model
# MAGIC    - with **inference tables** model inputs and outputs can be automatically tracked. 

# COMMAND ----------

import mlflow
import pandas as pd
from databricks.sdk import WorkspaceClient

# COMMAND ----------

CATALOG = 'protein_folding'
SCHEMA = 'esmfold'
MODEL_NAME = 'esmfold'

w = WorkspaceClient()
mlflow.set_registry_uri("databricks-uc")


uc_model_name = f"{CATALOG}.{SCHEMA}.{MODEL_NAME}"
versions = w.model_versions.list(uc_model_name)
v = max(versions, key=lambda v: v.version).version

# expects GPU (T4 is fine)
loaded_model = mlflow.pyfunc.load_model("models:/{uc_model_name}/{v}")

# COMMAND ----------

proteins = [
    'XVQLQESGGGLVQAGDSLKLSCEASGDSIGTYVIGWFRQAPGKERIYLATIGRNLVGPSDFYTRYADSVKGRFAVSRDNAKNTVNLQMNSLKPEDTAVYYCAAKTTTWGGNDPNNWNYWGQGTQVTV',
    'QVKLEESGGGLVQAGGSLRLSCAASGSTFSIYTMGWFRQAPGKEREFVADISWNGGSTYYADSVKGRFTIYRDNYKNTVYLQMNSLKPEDTAVYYCNADDLMIDRDYWGQGTQVTVSSGSEQKLISEEDLNHHHHHH',
]
loaded_model.predict(proteins)

# COMMAND ----------


