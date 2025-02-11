## Log, register, use and serve ESMfold

1. Run ESMfold_log notebook
   - this will download and log ESMfold into an mlflow experiment
   - the model will register to Unity Catalog in "protein_folding.esmfold.esmfold"
   - the model will be served on a small GPU serving endpoint

Some tests for ease of use:
a. Run ESMfold_from_load.py
   - you'll need to make a cluster with T4 GPU on DBR15.4 LTS_ML runtime
   - this allows you to check the model runs as expected
   - note in this case you download and run the model on the compute

b. Run ESMfold_endpoint_query notebook to test model serving endpoint
