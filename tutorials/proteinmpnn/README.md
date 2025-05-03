## ProteinMPNN

Artifacts to create ProteinMPNN model in an mlflow wrapper, to be registered in Unity Catalog, and served on a model serving endpoint.

#### install
We suggest install using the install instructions as per the README of the full repo.

#### What's inside

 - **envs:** pip and conda requirements for packaging
 - **example_data**: example data that is used to set input_examples and model signatures during registration
 - **protienmpnn**: proteinmpnn [library](https://github.com/dauparas/ProteinMPNN) re-packaged to essential running tools and with pyproject.toml to allow for easier install in containers, such as for model serving. see README within for further details.
 - **notebooks**:
   - 00_download_model_weights: download proteinmpnn model weights to Unity Catalog volume
   - 01_prep_input_examples: download and prep input examples (ie proteins with backbone only etc)
   - 02_log_protienmpnn: wrap proteinmpnn inside mlflow model and register to Unity Catalog
   - 03_serve_protein_mpnn: use Databricks python SDK to serve the registered model

   

