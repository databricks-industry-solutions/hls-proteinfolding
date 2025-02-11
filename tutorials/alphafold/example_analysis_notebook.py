# Databricks notebook source
# MAGIC %md
# MAGIC ## If you have performed an alpahfold inference - let's see how you can plot it in a notebook
# MAGIC  - You can also do this all within a databricks app - see the example app code in this repo

# COMMAND ----------

# DBTITLE 1,installs
# MAGIC %pip install py3Dmol
# MAGIC %pip install biopython
# MAGIC dbutils.library.restartPython()

# COMMAND ----------

# DBTITLE 1,imports
import py3Dmol
import Bio.PDB as bp
from Bio import pairwise2
from Bio.pairwise2 import format_alignment
import numpy as np
import os
import tempfile
from typing import Optional

# COMMAND ----------

# DBTITLE 1,options
TRUE_PDB : Optional[str] = '3bik'
AF_RUN : str = 'PD1' 

# COMMAND ----------

# DBTITLE 1,helper functions

class ChainSelect(bp.Select):
    def __init__(self, chain):
        self.chain = chain

    def accept_residue(self, residue):
        """ remove hetatm """
        return 1 if residue.id[0] == " " else 0

    def accept_chain(self, chain):
        if chain.get_id() == self.chain:
            return 1
        else:          
            return 0
        

def get_seq_alignment(structure1, structure2):
    """ structures can be biopy.PDB.Structures, Models, or Chains """
    seq1 = ""
    seq2 = ""
    for residue in structure1.get_residues():
        seq1 += residue.get_resname()[0]
    for residue in structure2.get_residues():
        seq2 += residue.get_resname()[0]

    alignment = pairwise2.align.localxx(seq1, seq2)
    return alignment

def get_backbone_atoms(structure):
    backbone_atoms = []
    for atom in structure.get_atoms():
        if atom.get_name() in ['N', 'CA', 'C']:
            backbone_atoms.append(atom)
    return backbone_atoms

def get_overlapping_backbone(structure1, structure2):
    """ structures can be biopy.PDB.Structures, Models, or Chains """
    alignment = get_seq_alignment(structure1,structure2)

    seq=""
    a_count=0
    b_count=0
    a_residues=[r for r in structure1.get_residues()]
    b_residues=[r for r in structure2.get_residues()]
    a_backbone = []
    b_backbone = []

    for idx,(i,j) in enumerate(zip(alignment[0].seqA,alignment[0].seqB)):
        if i!='-' and j!='-':
            if i==j:
                seq+=i
            # print(a_residues[a_count].resname,b_residues[b_count].resname)
            a_backbone.extend(get_backbone_atoms(a_residues[a_count]))
            b_backbone.extend(get_backbone_atoms(b_residues[b_count]))
        if i!='-':
            a_count+=1
        if j!='-':
            b_count+=1
    return {'atoms1':a_backbone, 'atoms2':b_backbone, 'seq':seq} 
        

# COMMAND ----------

# DBTITLE 1,load structures
# load requested files
mmcif_parser = bp.MMCIFParser()
pdb_parser = bp.PDBParser()
af_structure = pdb_parser.get_structure('AF2', f'/Volumes/protein_folding/alphafold/results/{AF_RUN}/ranked_0.pdb')

if TRUE_PDB is not None:
    true_structure = mmcif_parser.get_structure('true', f'/Volumes/protein_folding/alphafold/datasets/pdb_mmcif/mmcif_files/{TRUE_PDB}.cif')

    # get the chain from true PDB that has most similar sequence to the AF run
    alignment_scores = dict()
    for chain in true_structure.get_chains():
        ali = get_seq_alignment(af_structure, chain)[0]
        alignment_scores[chain.id] = ali.score
    max_overlapping_chain = max(alignment_scores, key=alignment_scores.get)

    # get Bio.PDB structure of just the chain of interest
    with tempfile.TemporaryDirectory() as tmp: 
        io = bp.PDBIO()
        io.set_structure(true_structure)
        new_name = os.path.join(tmp,"true_structure_singlechain.pdb")
        io.save(
            new_name,
            ChainSelect(max_overlapping_chain)
        )
        true_structure = pdb_parser.get_structure('true', new_name)

    # structurally align the af and true structures based on backbone atoms
    alignment_dict = get_overlapping_backbone(true_structure, af_structure)
    ref_backbone_atoms = alignment_dict['atoms1']
    af_backbone_atoms = alignment_dict['atoms2']

    imposer = bp.Superimposer()
    imposer.set_atoms(
        ref_backbone_atoms,
        af_backbone_atoms 
    )
    imposer.apply(af_structure.get_atoms())

# COMMAND ----------

# DBTITLE 1,create 3D viz html
with tempfile.TemporaryDirectory() as tmp:

    view = py3Dmol.view(width=800, height=300)

    # create temp files of aligned structures
    io = bp.PDBIO()
    io.set_structure(af_structure)
    io.save(os.path.join(tmp,"af_s.pdb"))

    view.addModel(
        open(os.path.join(tmp,"af_s.pdb"),'r').read(),
        'pdb'
    )
    view.setStyle(
        {'model':0},
        {'cartoon': 
            {'colorscheme': 
            {'prop':'b','gradient':'roygb','min':50,'max':90}
        }}
    )

    if TRUE_PDB is not None:
        io.set_structure(true_structure)
        io.save(os.path.join(tmp,"tr_s.pdb"))
        view.addModel(open(os.path.join(tmp,"tr_s.pdb"),'r').read(),'pdb')
        view.setStyle(
            {'model':1},
            {'cartoon': {'color': 'white', 'opacity': 0.9}}
        )
    
    view.zoomTo()
    html = view._make_html()

# COMMAND ----------

# MAGIC %md
# MAGIC ### Visuzalize 
# MAGIC AF2.3.2 predicted structure (colored by predicted accuracy, red:low,  blue:high) (coloring same as UniProt)
# MAGIC ##### if selected, vs:
# MAGIC  vs 
# MAGIC  true 3BIK:C (white, transulcent) 
# MAGIC

# COMMAND ----------

# DBTITLE 1,plot
displayHTML(html)

# COMMAND ----------

# MAGIC %md
# MAGIC ## did display HTML stop working? is it a DBR thing? something else?
# MAGIC  - fails on serverless and 14.3 as tested currently... and now 15.4 also fails.

# COMMAND ----------


