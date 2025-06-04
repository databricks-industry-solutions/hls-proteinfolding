from databricks.sdk import WorkspaceClient
from structure_utils import select_and_align
from typing import Tuple, Optional
import logging
import tempfile

from structure_utils import _cif_to_pdb_str
import os
from Bio.PDB import PDBParser

workspace_client = WorkspaceClient()


def pull_alphafold_run(run_name : str ='run') -> str:
    response = workspace_client.files.download(
        f'/Volumes/protein_folding/alphafold/results/{run_name}/ranked_0.pdb'
    )
    pdb_str = str(response.contents.read(), encoding='utf-8')
    return pdb_str

def pull_pdbmmcif(pdb_code : str ='4ykk') -> str:
    pdb_code = pdb_code.lower()
    response = workspace_client.files.download(
        f'/Volumes/protein_folding/alphafold/datasets/pdb_mmcif/mmcif_files/{pdb_code}.cif'
    )
    cif_str = str(response.contents.read(), encoding='utf-8')
    return _cif_to_pdb_str(cif_str)
  
def apply_pdb_header(pdb_str: str, name: str) -> str:
    header = f"""HEADER    "{name}"                           00-JAN-00   0XXX 
    TITLE     "{name}"                         
    COMPND    MOL_ID: 1;                                                            
    COMPND   2 MOLECULE: {name};                          
    COMPND   3 CHAIN: A;""" 
    return header + pdb_str
  
def af_collect_and_align(run_name : str, pdb_code : Optional[str] = None, include_pdb : bool = False) -> Tuple[str]:
    logging.info("collect run")
    pdb_run = pull_alphafold_run(run_name)
    logging.info("add header")
    pdb_run = apply_pdb_header(pdb_run, run_name)
    true_structure_str = ""
    af_structure_str = pdb_run
    if include_pdb:
      logging.info("collect PDB entry")
      pdb_mmcif = pull_pdbmmcif(pdb_code)
      # strings to biopdb structures
      with tempfile.TemporaryDirectory() as tmpdir:
          true_pdb_path = os.path.join(tmpdir, 'true_pdb.pdb')
          af_pdb_path = os.path.join(tmpdir, 'af_pdb.pdb') 
          with open(true_pdb_path, 'w') as f:
              f.write(pdb_mmcif)
          with open(af_pdb_path, 'w') as f:
              f.write(pdb_run)
          
          true_structure = PDBParser().get_structure('true',true_pdb_path)
          af_structure = PDBParser().get_structure('af',af_pdb_path)

          logging.info("do slect and align")
          true_structure_str, af_structure_str = select_and_align(
              true_structure, af_structure
          )

          logging.info("more headers")          
          true_structure_str = apply_pdb_header(true_structure_str, run_name)
          af_structure_str = apply_pdb_header(af_structure_str, "alphafold2 prediction")
    return pdb_run, true_structure_str, af_structure_str

def get_job_id(job_name : str ='alphafold'):
    """ get the job_id of job with name job_name """
    job_iter = workspace_client.jobs.list()
    found_jobs = [j for j in job_iter if j.as_dict()['settings'].get('name')==job_name]
    if len(found_jobs)==0:
        logging.error("No job with name "+job_name+" found")
    if not len(found_jobs)==1:
        logging.error("Multiple jobs with the same name found")
    found_job = found_jobs[0]
    return found_job.job_id

