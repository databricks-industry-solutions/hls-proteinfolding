# Databricks notebook source
# MAGIC %run ./download_setup

# COMMAND ----------

# MAGIC %sh
# MAGIC if [ ! -d "/Volumes/protein_folding/alphafold/datasets/uniprot" ]; then
# MAGIC   echo "Downloading uniprot"
# MAGIC   cd /app/alphafold/scripts
# MAGIC   ./download_uniprot.sh /local_disk0/downloads
# MAGIC   cd /
# MAGIC   cp -r /local_disk0/downloads/uniprot /Volumes/protein_folding/alphafold/datasets/
# MAGIC fi
