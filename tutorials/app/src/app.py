""" Run and view protein structure predictions

 - gradio app
 - Use molstar for viewing 
"""
import gradio as gr
import logging
from databricks.sdk import WorkspaceClient
import os
from typing import Optional,List,Union

from Bio.PDB.MMCIFParser import MMCIFParser
from Bio.PDB.PDBParser import PDBParser
from Bio.PDB.PDBIO import PDBIO
import tempfile
import base64 
import json
import requests
import time

from structure_utils import select_and_align
from protein_design import make_designs
from molstar_tools import molstar_html_multibody
from endpoint_queries import hit_esmfold, hit_boltz
from alphafold import get_job_id, af_collect_and_align

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize the Databricks Workspace Client
workspace_client = WorkspaceClient()


ASTEXT = False #True #False # useful for html debug if set to True
# -------------- button definitions -------------------------------------------------
      
def esmfold_btn_fn(protein : str) -> str:
    pdb = hit_esmfold(protein)
    html =  molstar_html_multibody(pdb)
    return html


def boltz_btn_fn(protein : str) -> str:
    pdb_run = hit_boltz(protein)
    html =  molstar_html_multibody(pdb_run)
    return html

def af_btn_fn(run_name : str, pdb_code : Optional[str] = None, include_pdb : bool = False) -> str: 
    logging.info('running alphafold viewer')
    pdb_run, true_structure_str, af_structure_str = af_collect_and_align(
      run_name=run_name, pdb_code=pdb_code, include_pdb=include_pdb
    )
    if include_pdb:
        logging.info('sending two pdb str to html')
        html = molstar_html_multibody([af_structure_str, true_structure_str])
    else:
        html = molstar_html_multibody(pdb_run)
    return html

def af_run_btn_fn(run_name : str, protein : str) -> str:
    run_id = workspace_client.jobs.run_now(
        job_id=get_job_id(job_name='alphafold'),
        job_parameters = {
            'protein':protein,
            'run_name':run_name
        }
    )
    return f"started run: {run_id}"

def design_btn_fn(sequence: str) -> str:
    n_rf_diffusion: int = 1
    designed_pdbs = make_designs(sequence)
    aligned_structures = align_designed_pdbs(designed_pdbs)           
    html =  molstar_html_multibody(aligned_structures)
    return html

# -------------------------------------------------------------------------------------
# -------------- set theming - make dark ----------------------------------------------

theme = gr.themes.Soft(
    primary_hue="lime",
    secondary_hue="violet",
    neutral_hue="zinc",
)
js_func = """
function refresh() {
    const url = new URL(window.location);

    if (url.searchParams.get('__theme') !== 'dark') {
        url.searchParams.set('__theme', 'dark');
        window.location.href = url.href;
    }
}
"""

# -------------------------------------------------------------------------------------
# -------------- construct the app  ---------------------------------------------------

af_job_id = get_job_id(job_name='alphafold')

with gr.Blocks(theme=theme, js=js_func) as demo:
    gr.Markdown(
        """
        # Protein Folding and Design on Databricks

        """)
    with gr.Tab('ESMfold'):
        gr.Markdown(
        """
        # Protein Structure Prediction with ESMfold
        Enter a protein sequence and view the structure.

        """)
        with gr.Accordion("Details", open=False) as accordion:
            gr.Markdown(f"""
                #### Details
                Use the ESMfold model serving [endpoint](https://{os.environ['DATABRICKS_HOST']}/ml/endpoints/esmfold) to get pdb structure for a protein sequence of interest.
            """)
        with gr.Row():
            protein = gr.Textbox(label="Protein",scale=4)
            btn = gr.Button("Predict", scale=1)

        if not ASTEXT:
            html_structure = gr.HTML(label="Structure")
        else:
            html_structure = gr.Textbox(label="Structure")
        btn.click(
            fn=esmfold_btn_fn, 
            inputs=protein, 
            outputs=html_structure
        )
        
        gr.Examples(
            examples=["MTYKLILNGKTLKGETTTEAVDAATAEKVFKQYANDNGVDGEWTYDAATKTFTVTE"],
            inputs=protein
        )
    with gr.Tab('alphafold'):
        gr.Markdown(
        """
        # Protein Structure Prediction with alphafold
        You can start a run of structure prediction or view previous runs

        """)
        with gr.Tab('Run'):
            with gr.Accordion("Details", open=False) as accordion:
                gr.Markdown(f"""
                    #### Run Details
                    Submits a job run on [this workflow](https://{os.environ['DATABRICKS_HOST']}/jobs/{af_job_id}). run_name can be any anme you like. For multimers use ":" to split chains. Runs can be picked up in Unity catalog [here](https://{os.environ['DATABRICKS_HOST']}/explore/data/volumes/protein_folding/alphafold/results). 
                """)
            with gr.Row():
                run_name_submit = gr.Textbox(label="run name",scale=1)
                protein_submit = gr.Textbox(label="protein",scale=3)
                af_run_btn = gr.Button("submit run", scale=1)
            
            af_run_id = gr.Textbox(label="run message")
            af_run_btn.click(
                fn=af_run_btn_fn, 
                inputs=[run_name_submit,protein_submit], 
                outputs=af_run_id
            )
        with gr.Tab('View'):
            with gr.Row():
                run_name = gr.Textbox(label="run name",scale=2)
                include_pdb = gr.Checkbox(label='Compare to PDB entry?',scale=1)
                pdb_code = gr.Textbox(label="PDB for comparison",scale=2)
                af_btn = gr.Button("view", scale=1)
            
            if not ASTEXT:
                af_html_structure = gr.HTML(label="Structure")
            else:
                af_html_structure = gr.Textbox(label="Structure")
            
            af_btn.click(
                fn=af_btn_fn, 
                inputs=[run_name,pdb_code,include_pdb], 
                outputs=af_html_structure
            )

            gr.Examples(
                examples=[["PD1",True,"3bik"]],
                inputs=[run_name,include_pdb,pdb_code],
            )
    with gr.Tab('Design'):
        with gr.Accordion("Details", open=False) as accordion:
            gr.Markdown("""
                ## Use RFdiffusion, ESMfold and ProteinMPNNN to inpaint and design proteins - eg for loop design
                 - input sequence in format: "CASRRSG[FTYPGF]FFEQYF" where the region between square braces is to be replaced/in-painted by new designs
            """)
        with gr.Row():
            protein_for_design = gr.Textbox(label="Protein",scale=4)
            # n_designs = gr.Textbox(label="number of designs",scale=4)
            design_btn = gr.Button("Predict", scale=1)

        if not ASTEXT:
            d_html_structures = gr.HTML(label="Structure")
        else:
            d_html_structures = gr.Textbox(label="Structure")
        
        design_btn.click(
            fn=design_btn_fn, 
            inputs=[protein_for_design], 
            outputs=d_html_structures
        )

        gr.Examples(
            examples=["CASRRSG[FTYPGF]FFEQYF"],
            inputs=protein_for_design,
        )
    with gr.Tab('Boltz-1'):
        gr.Markdown(
        """
        # Protein Structure Prediction with Boltz-1

        """)
        with gr.Accordion("Details", open=False) as accordion:
            gr.Markdown("""
                #### Details
                Enter a protein sequence and view the structure. 
                Use format: protein_A:sequence;protein_B,C:sequence
                 - this input UX will be improved soon
                 - types are protein, dna, rna, ligand
                 - chain ids should be comma separated if more than one

                options for other MSA fields etc and easy add of non protein objects to be added.

            """)
        with gr.Row():
            protein_boltz = gr.Textbox(label="Protein",scale=4)
            btn_boltz = gr.Button("Predict", scale=1)

        if not ASTEXT:
            html_structure_boltz = gr.HTML(label="Structure")
        else:
            html_structure_boltz = gr.Textbox(label="Structure")
        btn_boltz.click(
            fn=boltz_btn_fn, 
            inputs=protein_boltz, 
            outputs=html_structure_boltz
        )
        gr.Examples(
            examples=[
                "protein_A:SRALEEGRERLLWRLEPARGLEPPVVLVQTLTEPDWSVLDEGYAQVFPPKPFHPALKPGQRLRFRLRANPAKRLAATGKRVALKTPAEKVAWLERRLEEGGFRLLEGERGPWVQ;rna_B:UCCCCACGCGUGUGGGGAU"
            ],
            inputs=protein_boltz
        )
            

if __name__ == "__main__":
    demo.launch()