## Running Boltz-1 on Databricks

To install follow install instructions in the repo README.

#### What's in this tutorial:

**dbboltz:** A small package wrapper around Boltz-1 that allows us to use Boltz-1 with other MSA options including JackHMMer, and to make wrapping this in mlflow easier for scalable model serving on Databricks

**envs**: environment specification for model serving

**notebooks**:
 - prep_model_weights: Downloads model weights to unity catalog volumes
 - make_pyfunc: registers Boltz-1 model as a Unity catalog model
 - run_in_notebook_as_fn: Shows how you can use Boltz-1 using the function definition from dbboltz, including:
      - rendering outputs in the notebook using py3dmol
      - performing multimer, small molecule, and RNA inference
- serve_boltz: take the registered model made in "make_pyfunc" and serve it up on GPUs (we use T4 by default but you can alter this)


