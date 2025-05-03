## Building a gradio App and provisioning it with Databricks Apps

Tooling to build a gradio app for allowing users to query:
 - ESMfold
 - Alphafold (users start a workflow job from within the app)
 - Boltz-1
 - protein design (runs ESMFold, RFDiffusion and proteinMPNN)

## Install
 - the "01_create_app_with_sdk" notebook will provision the Databricks App
 - Does assume models will exist on serving endpoints
  - suggest running install per the repo README instructions to ensure all dependencies in place

  