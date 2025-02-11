## Running alphafold

Because Alphafold runs both expensive CPU and GPU jobs, we split up the two sets of tasks (featurization and folding).

The python module at workflow/scripts/run\_alphafold\_split.py has flags to allow you to run jsut the featurization (do on a CPU machine), 
or to fold (using GPU) after loading up precomputed feature pickle. 

This set up means featurization and folding can be set as two tasks in a Databricks job, with each task running on appropriate compute.

Note that we suggest here manually placing yaml description (auto generated for you) of the job in the workflows UI to create the job - with the yaml one can also set up a Databricks Asset Bundle instead to build these resources.

### To setup alphafold:

 1. If not already downloaded in your workspace - download datasets
    - Use 00_create_downloads_workflow to create a yaml that can be used to make a new workflows job
      - In the workflows UI, click "create job", then in the upper right click the kebab menu and select "switch to code version (yaml)"
    - Create the job using the yaml, and run it
    - This runs, in parallel, the downloads (will take ~12 hours for longest download, most are in the few hours range) 

 2. Use 01_create_alphafold_workflow to build a workflow to actually run alphafold
    - creates a yaml you can use to make a new job
    - create the workflows job
    - Note, we set concurrency to 5, meaning 5 users can have jobs running at once and otherwise a queue is formed
       -  you can change this behaviour at any time in the UI
 
 3. Use the 02_run_alphafold_workflow here to set of a new run 
    - or, in the workflows UI page, hit arrow next to "run", and select run with different parameters

#### Optionally, you can use the notebooks to run alphafold ad-hoc:

 - Run nb_run_af_featurize notebook on a CPU cluster
   - Make sure you use conda with the licensing terms of Anaconda (here we do not use defaults)
   - enter the protein and name the run as widgets in the notebook.

 -  Run nb_run_af_fold notebook
   - Do this on a GPU cluster (will work on CPU but GPU is much faster)
   - re-enter your protein and run_name in widgets


