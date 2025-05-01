# Databricks notebook source
# MAGIC %run ./download_setup

# COMMAND ----------

# MAGIC %sh
# MAGIC if [ ! -d "/Volumes/protein_folding/alphafold/datasets/uniref90" ]; then
# MAGIC   echo "Downloading Uniref90"
# MAGIC   cd /app/alphafold/scripts
# MAGIC   ./download_uniref90.sh /local_disk0/downloads
# MAGIC   cd /
# MAGIC   cp -r /local_disk0/downloads/uniref90 /Volumes/protein_folding/alphafold/datasets/
# MAGIC fi

# COMMAND ----------

# MAGIC %sh
# MAGIC if [ ! -d "/Volumes/protein_folding/alphafold/datasets/uniref30" ]; then
# MAGIC   echo "Downloading Uniref30"
# MAGIC   cd /app/alphafold/scripts
# MAGIC   ./download_uniref30.sh /local_disk0/downloads
# MAGIC   cd /
# MAGIC   cp -r /local_disk0/downloads/uniref30 /Volumes/protein_folding/alphafold/datasets/
# MAGIC fi
