# Databricks notebook source
# MAGIC %md
# MAGIC
# MAGIC # RFDiffusion - logging the with mlflow for generative protein design
# MAGIC
# MAGIC Tested on DBRML 14.3 on T4 (Standard_NC4as_T4_v3)
# MAGIC  - note that 14.3 is required for RFdiffusion due to strong dependencies on Python 3.10 or lower wihtin RFdiffusion and its dependencies

# COMMAND ----------

# MAGIC %pip install -r scripts/rfd_requirements.txt
# MAGIC # identical pip reqs to the conda env will use to log the model (but without cudatoolkit)
# MAGIC # allows to test in 14.3ML, and serve on serving with correct CUDA version
# MAGIC dbutils.library.restartPython()

# COMMAND ----------

import subprocess
import os
import tempfile
import mlflow
from mlflow.types.schema import ColSpec, Schema
from typing import Any, Dict, List, Optional

import logging
# logging.basicConfig()
# logging.getLogger().setLevel(logging.INFO)

# COMMAND ----------

# MAGIC %md
# MAGIC ##### consider : initialize_config_dir()
# MAGIC  - use absolute not relative path...

# COMMAND ----------

class RFDiffusionUnconditional(mlflow.pyfunc.PythonModel):
    def load_context(self, context):
        self.model_path = context.artifacts['model_path']
        self.script_path = context.artifacts['script_path']
        self.example_path = context.artifacts['example_path']
        
        import sys
        import os
        self.config_path = context.artifacts['config_path']
        self.rel_config_path = os.path.relpath("/", sys.argv[0])[:-3] + self.config_path

    def _validate_input(self,plen):
        if not isinstance(plen,int):
            try:
                plen = int(plen)
            except:
                raise TypeError("plen should be an int (and less than 180)")
        if plen>180:
            raise ValueError("plen must be less than 180, {plen} was passed")
        if plen==0:
            raise ValueError("protein length must be greater than 0")
        return plen
    
    def _make_config(self,plen:int,outpath:str='out'):
        """ creates a hydra config file for the run script"""
        import hydra
        # with hydra.initialize(version_base=None, config_path=self.rel_config_path):
        cfg = hydra.compose(
            config_name="base", 
            overrides=[
                f'contigmap.contigs=[{plen}-{plen}]',
                f'inference.output_prefix={outpath}/output',
                'inference.num_designs=1',
                f'inference.model_directory_path={self.model_path}',
                f'inference.input_pdb={self.example_path}/input_pdbs/1qys.pdb',
                f'diffuser.T=20'
            ],
            return_hydra_config=True,
            )
        return cfg
    
    def _dummy_hydra(self):
        import os
        from omegaconf import OmegaConf
        hydra_runtime = OmegaConf.create({
            "runtime": {
                "output_dir": "/path/to/outputs",  
                "cwd": os.getcwd()
            },
            "job": {
                "name": "manual_job",
                "num": 0
            }
        })
        return hydra_runtime

    def _run_inference(self,plen:int):
        """ runs inference script with fixed environment 
        
        parameters
        -----------
        plen:
            The length of protein to generate
        """
        import sys
        sys.path.append(self.script_path)
        import hydra
        from run_inference import main as mn
        from omegaconf import OmegaConf
        from hydra.core.hydra_config import HydraConfig

        plen = self._validate_input(plen)
        
        with tempfile.TemporaryDirectory() as tmpdirname:
            with hydra.initialize(version_base=None, config_path=self.rel_config_path):
                cfg = self._make_config(plen=plen,outpath=tmpdirname)
                # add dummy hydra pieces and Merge with existing config
                cfg = OmegaConf.merge(
                    {"hydra": self._dummy_hydra()},
                    cfg
                )
                HydraConfig.instance().set_config(cfg)
                mn(cfg)
            with open('{}/output_0.pdb'.format(tmpdirname),'r') as f:
                pdbtext = f.read()
        return pdbtext
    
    def predict(self, context, model_input : List[str], params=None) -> List[str]:
        """ Generate structure of protein of given length
        parameters
        --------

        context:
            The mlflow context of the model. Gathered by load_context()
        
        model_input:
            A list of strings of protein lengths. Should only contain one entry in the list.
            The string of protein length, e.g "10" will internally be converted to int.

        params: Optional[Dict[str, Any]]
            Additional parameters
        """
        if len(model_input)>1:
            raise ValueError("input must be a list with a single integer as string")

        # convert to int (str input is easier to manage on server side)
        plen = int(model_input[0])
        pdb = self._run_inference(plen)
        return pdb

# COMMAND ----------

class RFDiffusionInpainting(mlflow.pyfunc.PythonModel):
    def load_context(self, context):
        self.model_path = context.artifacts['model_path']
        self.script_path = context.artifacts['script_path']
        
        import sys
        import os
        self.config_path = context.artifacts['config_path']
        self.rel_config_path = os.path.relpath("/", sys.argv[0])[:-3] + self.config_path

        # more than this is too slow for serving...
        self.num_designs=1
        self.steps=20 # rfdiffusion repo suggests 20steps is usually sufficient

    def _validate_input(self,pdb_str):
        return True
    
    def _make_config(self,contig_statement:str,pdb_path:str,outpath:str='out'):
        """ creates a hydra config file for the run script"""
        import hydra
        # with hydra.initialize(version_base=None, config_path=self.rel_config_path):
        cfg = hydra.compose(
            config_name="base", 
            overrides=[
                f'contigmap.contigs=[{contig_statement}]',
                f'inference.output_prefix={outpath}/output',
                f'inference.num_designs={self.num_designs}',
                f'inference.model_directory_path={self.model_path}',
                f'inference.input_pdb={pdb_path}',
                f'diffuser.T={self.steps}'
            ],
            return_hydra_config=True,
        )
        return cfg
    
    def _dummy_hydra(self):
        import os
        from omegaconf import OmegaConf
        hydra_runtime = OmegaConf.create({
            "runtime": {
                "output_dir": "/path/to/outputs",  
                "cwd": os.getcwd()
            },
            "job": {
                "name": "manual_job",
                "num": 0
            }
        })
        return hydra_runtime

    def _run_inference(self,input_pdb:str, start_idx:int, end_idx:int):
        """ runs inference script with fixed environment 
        
        parameters
        -----------
        input_pdb:
            the pdb string to generate backbone for

        idxs are inclusive (of mask) and based on indexing in the pdb file
        ie idx for start and end will both be generated
        """
        import sys
        sys.path.append(self.script_path)
        from run_inference import main as mn
        from Bio.PDB.Polypeptide import d3_to_index, dindex_to_1
        from Bio.PDB import PDBParser
        import hydra
        from omegaconf import OmegaConf
        from hydra.core.hydra_config import HydraConfig
        
        with (
            tempfile.TemporaryDirectory() as tmpdirname,
            tempfile.TemporaryDirectory() as in_tmpdirname):

            input_pdb_path = os.path.join(in_tmpdirname, 'input.pdb')
            with open(input_pdb_path, 'w') as f:
                f.write(input_pdb)

            x_len = end_idx - start_idx + 1

            mysplit = input_pdb.split('\n')[:-1]
            idxs = set()
            for i,v in enumerate(mysplit):
                if v.startswith('ATOM'):
                    idxs.add(int(v[22:26].strip()))
            seq_final_pos = max(idxs)

            contigmap = f"A1-{start_idx-1}/{x_len}-{x_len}/A{end_idx+1}-{seq_final_pos}"
            print(contigmap)
                
            with hydra.initialize(version_base=None, config_path=self.rel_config_path):
                cfg = self._make_config(contigmap, input_pdb_path, outpath=tmpdirname)
                cfg = OmegaConf.merge(
                        {"hydra": self._dummy_hydra()},
                        cfg
                    )
                HydraConfig.instance().set_config(cfg)
                mn(cfg)
            texts = []
            for i in range(self.num_designs):
                with open(f'{tmpdirname}/output_{i}.pdb','r') as f:
                    pdbtext = f.read()
                    texts.append(pdbtext)
        return texts
    
    def predict(self, context, model_input : List[Dict[str,str]], params=None) -> List[str]:
        """ Generate structure of protein of given length
        parameters
        --------

        context:
            The mlflow context of the model. Gathered by load_context()
        
        model_input:
            A list of dicts (pdb, start_idx, end_idx). Should only contain one entry in the list.
            start_idx and end_idx positions are 1-indexed and are includive to the mask for inpaint
            the pdb string should be of a pdb file that is 1-indexed for residues, no hetatm, single A chain

        params: Optional[Dict[str, Any]]
            Additional parameters
        """
        if len(model_input)>1:
            raise ValueError("input must be a list with a single entry")

        # pdb_texts = self._run_inference(model_input[0])
        pdb_texts = self._run_inference(model_input[0]['pdb'], int(model_input[0]['start_idx']), int(model_input[0]['end_idx']))
        return pdb_texts

# COMMAND ----------

model = RFDiffusionUnconditional()
repo_path = '/Volumes/protein_folding/rfdiffusion/repo_w_models/RFdiffusion/'
artifacts={
    "script_path" : os.path.join(repo_path,"scripts"),
    "model_path" : os.path.join(repo_path,"models"),
    "example_path" : os.path.join(repo_path,"examples"),
    "config_path" : os.path.join(repo_path,"config/inference"),
}

model.load_context(mlflow.pyfunc.PythonModelContext(artifacts=artifacts, model_config=dict()))
pdb = model._run_inference(100)
pdb

# COMMAND ----------

# MAGIC %md
# MAGIC #### test the inpainting version
# MAGIC  - first make a dummy pdb that's been formatted correctly 

# COMMAND ----------

from Bio.PDB import PDBList
from Bio.PDB import PDBParser
from Bio import PDB
parser = PDBParser()

import requests
with tempfile.TemporaryDirectory() as tmpdirname:
    response = requests.get("https://files.rcsb.org/download/8dgr.pdb")
    pdb_file_path = f"{tmpdirname}/8dgr.pdb"
    with open(pdb_file_path, 'wb') as file:
        file.write(response.content)
    structure = parser.get_structure("8DGR", pdb_file_path)

def extract_chain_reindex(structure, chain_id='A'):
    # Extract chain A
    chain = structure[0][chain_id]
    
    # Create a new structure with only chain A & 1-indexed
    new_structure = PDB.Structure.Structure('new_structure')
    new_model = PDB.Model.Model(0)
    new_chain = PDB.Chain.Chain(chain_id)
    
    # Reindex residues starting from 1
    for i, residue in enumerate(chain, start=1):
        if residue.id[0] == ' ':  # Ensure no HETATM
            residue.id = (' ', i, ' ')
            new_chain.add(residue)
    
    new_model.add(new_chain)
    new_structure.add(new_model)
    
    # Save the new structure to a PDB file
    io = PDB.PDBIO()
    io.set_structure(new_structure)
    with tempfile.NamedTemporaryFile(suffix='.pdb') as f:
        io.save(f.name)
        with open(f.name, 'r') as f_handle:
            pdb_text = f_handle.read()
    return pdb_text

# COMMAND ----------

model = RFDiffusionInpainting()
repo_path = '/Volumes/protein_folding/rfdiffusion/repo_w_models/RFdiffusion/'
artifacts={
    "script_path" : os.path.join(repo_path,"scripts"),
    "model_path" : os.path.join(repo_path,"models"),
    "example_path" : os.path.join(repo_path,"examples"),
    "config_path" : os.path.join(repo_path,"config/inference"),
}

model.load_context(mlflow.pyfunc.PythonModelContext(artifacts=artifacts, model_config=dict()))

# mask our pdb at residues 12-22 inclusive and generate new protein backbone
pdbs = model._run_inference( extract_chain_reindex(structure), 12, 22 )

# COMMAND ----------

pdbs[0].split('\n')[:10]

# COMMAND ----------

signature = mlflow.models.signature.ModelSignature(
    inputs = Schema([ColSpec(type="string")]),
    outputs = Schema([ColSpec(type="string")]),
    params = None
)


context = mlflow.pyfunc.PythonModelContext(artifacts=artifacts, model_config=dict())
input_example=[
    {
        'pdb':extract_chain_reindex(structure),
        'start_idx' : 12,
        'end_idx': 22 
    }
]
inpaint_signature = mlflow.models.infer_signature(
    input_example,
    model.predict(context, input_example)
)
print(inpaint_signature)

# COMMAND ----------

mlflow.set_registry_uri("databricks-uc")

repo_path = '/Volumes/protein_folding/rfdiffusion/repo_w_models/RFdiffusion/'

with mlflow.start_run(run_name='rfdiffusion_unconditional'):
    model_info = mlflow.pyfunc.log_model(
        artifact_path="rfdiffusion",
        python_model=RFDiffusionUnconditional(),
        artifacts={
            "script_path" : os.path.join(repo_path,"scripts"),
            "model_path" : os.path.join(repo_path,"models"),
            "example_path" : os.path.join(repo_path,"examples"),
            "config_path" : os.path.join(repo_path,"config/inference"),
        },
        input_example=["100"],
        signature=signature,
        conda_env='scripts/rfd_env.yml',
        registered_model_name="protein_folding.rfdiffusion.rfdiffusion_unconditional"
    )

with mlflow.start_run(run_name='rfdiffusion_inpainting'):
    model_info = mlflow.pyfunc.log_model(
        artifact_path="rfdiffusion",
        python_model=RFDiffusionInpainting(),
        artifacts={
            "script_path" : os.path.join(repo_path,"scripts"),
            "model_path" : os.path.join(repo_path,"models"),
            "example_path" : os.path.join(repo_path,"examples"),
            "config_path" : os.path.join(repo_path,"config/inference"),
        },
        input_example=input_example,
        signature=inpaint_signature,
        conda_env='scripts/rfd_env.yml',
        registered_model_name="protein_folding.rfdiffusion.rfdiffusion_inpainting"
    )

# COMMAND ----------


