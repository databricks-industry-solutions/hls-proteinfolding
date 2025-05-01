# Databricks notebook source
# MAGIC %run ./download_setup

# COMMAND ----------

# MAGIC %sh
# MAGIC if [ ! -d "/Volumes/protein_folding/alphafold/datasets/mgnify" ]; then
# MAGIC     echo "Downloading mgnify"
# MAGIC     cd /app/alphafold/scripts
# MAGIC     ./download_mgnify.sh /local_disk0/downloads
# MAGIC     cd /
# MAGIC     cp -r /local_disk0/downloads/mgnify /Volumes/protein_folding/alphafold/datasets/
# MAGIC fi

# COMMAND ----------

# MAGIC %sh
# MAGIC if [ ! -d "/Volumes/protein_folding/alphafold/datasets/small_bfd" ]; then
# MAGIC     echo "Downloading small_bfd"
# MAGIC     cd /app/alphafold/scripts
# MAGIC     ./download_small_bfd.sh /local_disk0/downloads
# MAGIC     cd /
# MAGIC     cp -r /local_disk0/downloads/small_bfd /Volumes/protein_folding/alphafold/datasets/
# MAGIC fi

# COMMAND ----------

# MAGIC %sh
# MAGIC if [ ! -d "/Volumes/protein_folding/alphafold/datasets/pdb70" ]; then
# MAGIC   echo "Downloading pdb70"
# MAGIC     cd /app/alphafold/scripts
# MAGIC     ./download_pdb70.sh /local_disk0/downloads
# MAGIC     cd /
# MAGIC     cp -r /local_disk0/downloads/pdb70 /Volumes/protein_folding/alphafold/datasets/
# MAGIC fi

# COMMAND ----------

# MAGIC %sh
# MAGIC if [ ! -d "/Volumes/protein_folding/alphafold/datasets/pdb_seqres" ]; then
# MAGIC     echo "Downloading pdb_seqres"
# MAGIC     cd /app/alphafold/scripts
# MAGIC     ./download_pdb_seqres.sh /local_disk0/downloads
# MAGIC     cd /
# MAGIC     cp -r /local_disk0/downloads/pdb_seqres /Volumes/protein_folding/alphafold/datasets/
# MAGIC fi
