## RFDiffusion

Artifacts to create RFDiffusion model in an mlflow wrapper, to be registered in Unity Catalog, and served on a model serving endpoint.

Two versions of the model are resgistered and served:
 - unconditional: generate proteins of a given length without any other constraints
 - inpainting: generate backbone based on an initial backbone with a region masked

#### install
We suggest install using the install instructions as per the README of the full repo.

#### What's inside
 - **envs/**: requirements and conda environment specifications for environments
 - notebooks:
   - fetch_repo_and_weights: place repo and model weights into a volume in Unity Catalog
   - rfdiffusion_log: log and register the models to Unity Catalog
   - serve_rfdiffusion: use the Databricks SDK to serve the registered models in model serving
   - rfdiffusion_from_load: Shows how you can use the model using GPU compute on notebook by laoding model
   - query_rfdiffusion_endpoint: Shows how you can query rfdiffusion model serving endpoint
