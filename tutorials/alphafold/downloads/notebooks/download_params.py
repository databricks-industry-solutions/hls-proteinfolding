# Databricks notebook source
# MAGIC %run ./download_setup

# COMMAND ----------

# MAGIC %sh
# MAGIC if [ ! -d "/Volumes/protein_folding/alphafold/datasets/params" ]; then
# MAGIC   cd /app/alphafold/scripts
# MAGIC   ./download_alphafold_params.sh /local_disk0/downloads
# MAGIC   cd /
# MAGIC   cp -r /local_disk0/downloads/params /Volumes/protein_folding/alphafold/datasets/
# MAGIC fi

# COMMAND ----------


