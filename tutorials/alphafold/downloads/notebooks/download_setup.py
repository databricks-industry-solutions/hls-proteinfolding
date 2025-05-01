# Databricks notebook source
# MAGIC %md
# MAGIC This can be called with a %run command for other download scripts as this process is required for seperate download tasks

# COMMAND ----------

# MAGIC %sql
# MAGIC CREATE CATALOG IF NOT EXISTS protein_folding;
# MAGIC USE CATALOG protein_folding;
# MAGIC CREATE SCHEMA IF NOT EXISTS alphafold;
# MAGIC USE SCHEMA alphafold;
# MAGIC CREATE volume IF NOT EXISTS datasets;

# COMMAND ----------

# MAGIC %sh
# MAGIC apt-get update
# MAGIC apt-get --no-install-recommends -y install aria2

# COMMAND ----------

# MAGIC %sh 
# MAGIC mkdir -p /app
# MAGIC cd /app
# MAGIC git clone https://github.com/google-deepmind/alphafold.git
# MAGIC cd alphafold
# MAGIC git checkout v2.3.2

# COMMAND ----------

# MAGIC %sh
# MAGIC cd /local_disk0
# MAGIC mkdir -p downloads
