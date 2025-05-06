# Databricks notebook source
# MAGIC %md
# MAGIC ### Place queries against RFdiffusion served model endpoint and generate proteins
# MAGIC
# MAGIC #### The code below can run anywhere - just need the URL of your Databricks instance and a token

# COMMAND ----------

import os
import requests
import numpy as np
import pandas as pd
import json

# COMMAND ----------

DATABRICKS_TOKEN = dbutils.notebook.entry_point.getDbutils().notebook().getContext().apiToken().get()
DATABRICKS_URL = dbutils.notebook.entry_point.getDbutils().notebook().getContext().apiUrl().get()

# COMMAND ----------

def hit_api(protein_length):
    url = 'https://adb-830292400663869.9.azuredatabricks.net/serving-endpoints/rfdiffusion_unconditional/invocations'
    headers = {'Authorization': f'Bearer {os.environ.get("DATABRICKS_TOKEN")}', 'Content-Type': 'application/json'}
    ds_dict = {'inputs':protein_length}
    data_json = json.dumps(ds_dict, allow_nan=True)
    response = requests.request(method='POST', headers=headers, url=url, data=data_json)
    if response.status_code != 200:
        raise Exception(f'Request failed with status {response.status_code}, {response.text}')
    return response.json()

# COMMAND ----------

hit_api([["50"]])

# COMMAND ----------


