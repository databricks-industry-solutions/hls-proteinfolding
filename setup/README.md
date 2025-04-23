# Setup Protein folding on Databricks

Simple single notebook install of all models, provisioning model serving endpoints (with scale to zero on so they do not cost while idle), and an application for hosting the models in a UI. Optionally download alphafold2 datasets with flag in the install notebooks.

### Install
- Run install notebook (must be workspace admin)
  - don't forget to set your email in the notebook (for alerts etc)
  - you can set download alphafold datasets to True if you wish to download them
    - if you already have a copy elsewhere you can copy them over 
    - or create an external volume, though you'll need to modify the paths in the alphafold running notebook to change where to look for the databases.

## Uninstall
- Cleanup notebook will delete models, workflows, catalog objects, and the app