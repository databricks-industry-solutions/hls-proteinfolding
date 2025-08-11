## Running Boltz-1 on Databricks

To install, follow the instructions in the repo README.

#### What's in this tutorial:

**dbboltz:** A small package wrapper around Boltz-1 that allows you to use Boltz-1 with other MSA options, including JackHMMer, and makes wrapping this in MLflow easier for scalable model serving on Databricks.

**envs:** Environment specifications for model serving.

**notebooks:**
 - prep_model_weights: Downloads model weights to Unity Catalog volumes.
 - make_pyfunc: Registers the Boltz-1 model as a Unity Catalog model.
 - run_in_notebook_as_fn: Shows how to use Boltz-1 with the function definition from dbboltz, including:
      - Rendering outputs in the notebook using py3dmol.
      - Performing multimer, small molecule, and RNA inference.
 - serve_boltz: Takes the registered model made in "make_pyfunc" and serves it on GPUs (T4 by default, but you can change this).