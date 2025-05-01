# Databricks notebook source
# MAGIC %run ./download_setup

# COMMAND ----------

# MAGIC %sh
# MAGIC if [ ! -d "/Volumes/protein_folding/alphafold/datasets/pdb_mmcif" ]; then
# MAGIC     echo "Downloading pdb_mmcif"
# MAGIC     cd /app/alphafold/scripts
# MAGIC     ./download_pdb_mmcif.sh /local_disk0/downloads
# MAGIC     cd /
# MAGIC     cp -r /local_disk0/downloads/pdb_mmcif /Volumes/protein_folding/alphafold/datasets/
# MAGIC fi

# COMMAND ----------


