# Databricks notebook source
# MAGIC %sql
# MAGIC CREATE CATALOG IF NOT EXISTS protein_folding;
# MAGIC USE CATALOG protein_folding;
# MAGIC CREATE SCHEMA IF NOT EXISTS alphafold;
# MAGIC USE SCHEMA alphafold;
# MAGIC CREATE VOLUME IF NOT EXISTS datasets;
# MAGIC CREATE VOLUME IF NOT EXISTS results;

# COMMAND ----------

# MAGIC %sh
# MAGIC mkdir -p /local_disk0/common/
# MAGIC wget -q -P /local_disk0/common/ \
# MAGIC   https://git.scicore.unibas.ch/schwede/openstructure/-/raw/7102c63615b64735c4941278d92b554ec94415f8/modules/mol/alg/src/stereo_chemical_props.txt
# MAGIC
# MAGIC mkdir -p /Volumes/protein_folding/alphafold/datasets/common
# MAGIC cp /local_disk0/common/stereo_chemical_props.txt /Volumes/protein_folding/alphafold/datasets/common

# COMMAND ----------


