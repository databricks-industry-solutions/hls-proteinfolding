# Databricks notebook source
# MAGIC %md
# MAGIC ## Place queries against ESMfold served model endpoint and make structure predictions
# MAGIC
# MAGIC #### The code below can run anywhere - just need the URL of your Databricks instance and a token
# MAGIC

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

# MAGIC %md
# MAGIC This function could be used from anywhere as long as you have a URL/TOKEN

# COMMAND ----------

def hit_api(protein):
    url = f'{DATABRICKS_URL}/serving-endpoints/esmfold/invocations'
    headers = {'Authorization': f'Bearer {DATABRICKS_TOKEN}', 'Content-Type': 'application/json'}
    ds_dict = {'inputs':protein}
    data_json = json.dumps(ds_dict, allow_nan=True)
    response = requests.request(method='POST', headers=headers, url=url, data=data_json)
    if response.status_code != 200:
        raise Exception(f'Request failed with status {response.status_code}, {response.text}')
    return response.json()

# COMMAND ----------

hit_api(['CASRSYS'])

# COMMAND ----------

proteins = [
    'XVQLQESGGGLVQAGDSLKLSCEASGDSIGTYVIGWFRQAPGKERIYLATIGRNLVGPSDFYTRYADSVKGRFAVSRDNAKNTVNLQMNSLKPEDTAVYYCAAKTTTWGGNDPNNWNYWGQGTQVTV',
    'QVKLEESGGGLVQAGGSLRLSCAASGSTFSIYTMGWFRQAPGKEREFVADISWNGGSTYYADSVKGRFTIYRDNYKNTVYLQMNSLKPEDTAVYYCNADDLMIDRDYWGQGTQVTVSSGSEQKLISEEDLNHHHHHH',
]
output = hit_api(proteins)
print(output)

# COMMAND ----------

# MAGIC %md
# MAGIC ### We can take a look at the inference logs on the endpoint to see what queries have been run on the endpoint

# COMMAND ----------

# this may take some minutes for the table to populate after queries are made
sdf = spark.table('protein_folding.esmfold.esmfold_serving_payload')
sdf.display()

# COMMAND ----------


