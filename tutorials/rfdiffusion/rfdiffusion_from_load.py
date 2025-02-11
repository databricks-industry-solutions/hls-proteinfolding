# Databricks notebook source
# MAGIC %md
# MAGIC #### Load in the model from Unity Catalog
# MAGIC - load includes doing all model setup - takes some minutes
# MAGIC - We have some unusual dependencies - we must therefore find from teh model what it's expected dependencies are ans install them
# MAGIC - note that because this model has a strong requirement on CUDA 11 - **run this in DBRML14.3 ML** as changing CUDA is not trivial within notebook
# MAGIC - For model serving we take care of the cuda depencies by logging it with the model

# COMMAND ----------

import mlflow
mlflow.set_registry_uri("databricks-uc")
logged_model = "models:/protein_folding.rfdiffusion.rfdiffusion_unconditional/1"

#get our model requirements
req_path = mlflow.artifacts.download_artifacts("{}/requirements.txt".format(logged_model))
print(req_path)

# COMMAND ----------

# COPY the output from the last cell here...
%pip install -r /local_disk0/repl_tmp_data/ReplId-793c0-e0012-b1fd4-c/tmpy8r0fu98/requirements.txt
dbutils.library.restartPython()

# COMMAND ----------

import mlflow
mlflow.set_registry_uri("databricks-uc")
logged_model = "models:/protein_folding.rfdiffusion.rfdiffusion_unconditional/1"
loaded_model = mlflow.pyfunc.load_model(logged_model)
loaded_model.predict(["30"])

# COMMAND ----------


