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
from protein_design import make_designs, align_designed_pdbs
from molstar_tools import molstar_html_multibody
from endpoint_queries import hit_esmfold, hit_boltz
from alphafold import get_job_id, af_collect_and_align

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize the Databricks Workspace Client
workspace_client = WorkspaceClient()


ASTEXT = False # useful for html debug if set to True
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
        html = molstar_html_multibody(af_structure_str)
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
    logging.info("design: make designs")
    designed_pdbs = make_designs(sequence)
    logging.info("design: align")
    # logging.info([k for k in designed_pdbs.keys()])
    # logging.info([v[:10] for v in designed_pdbs.values()])
    aligned_structures = align_designed_pdbs(designed_pdbs)
    logging.info("design: get html for designs")           
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

# helper pieces for Boltz complicated inputs
boltz_dropdown_choices = ["protein","rna","dna","ligand"]
MAX_ROWS = 10

# def create_row(row_id, visible=True):
#     with gr.Row(visible=visible) as row:
#         dropdown = gr.Dropdown(boltz_dropdown_choices, label=f"Sequence Type {row_id}", scale=1)
#         chain_box = gr.Textbox(label=f"Chain {row_id}", scale=1)
#         seq_box = gr.Textbox(label=f"Sequence {row_id}", scale=5)
#     return row, dropdown, chain_box, seq_box

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
        gr.Markdown(
        """
        # Protein Structure Design with ESMfold, RFDiffusion and ProteinMPNN

        """)
        with gr.Accordion("Details", open=False) as accordion:
            gr.Markdown(f"""
                ## Use [RFdiffusion](https://{os.environ['DATABRICKS_HOST']}/ml/endpoints/rfdiffusion_inpainting), [ESMfold](https://{os.environ['DATABRICKS_HOST']}/ml/endpoints/esmfold) and [ProteinMPNNN](https://{os.environ['DATABRICKS_HOST']}/ml/endpoints/proteinmpnn) to inpaint and design proteins - eg for loop design

                 - input sequence in format: "CASRRSG[FTYPGF]FFEQYF" where the region between square braces is to be replaced/in-painted by new designs
                 - internally generates the original sequence's (including the region in braces) structure using ESMFold
                 - then uses RFdiffusion to generate a protein backbine with inpainting of the region between braces
                 - ProteinMPNN is use to infer sequences of the backbones
                 - the structures of these sequences are then inferred with ESMfold and aligned to the original
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
         - you can add multiple sequence elements (protein, DNA, RNA, ligand)
        """)
        with gr.Accordion("Details", open=False) as accordion:
            gr.Markdown(f"""
                #### Details
                [serving endpoint](https://{os.environ['DATABRICKS_HOST']}/ml/endpoints/boltz)

                Enter a protein sequence and view the structure. 

                - the chain option is preselected as the next letter, but if you wish to predict the structure with repeated element you can use comma seperated chains on a single input sequence.
                - The MSA stage is currently only supporting no MSA, but other options including mmseqs2 server can be supported on the endpoint

            """)

        def load_example(example_idx):
            dd_vals =  ["protein", "rna"] + [None] * (MAX_ROWS - 2)
            ch_vals = ["A", "B"]  + [None] * (MAX_ROWS - 2)
            se_vals = [
                "MSSGTPTPSNVVLIGKKPVMNYVLAALTLLNQGVSEIVIKARGRAISKAVDTVEIVRNRFLPDKIEIKEIRVGSQVVTSQDGRQSRVSTIEIAIRKK", 
                "GGUAAGAGCACCCGACUGCUCUUCC"
            ] +  [None] * (MAX_ROWS - 2)
            return [2] + dd_vals + ch_vals + se_vals
        
        load_btn = gr.Button("Load Example")

        rows_container = gr.Group()
    
        # Track visible rows and components
        visible_rows = gr.State(1)  # Start with 1 visible row
        
        dropdowns = []
        chain_boxes = []
        seq_boxes = []
        with rows_container:
            for i in range(MAX_ROWS):
                row_id = i
                with gr.Row(visible=(i == 0)) as row:
                    dropdown = gr.Dropdown(boltz_dropdown_choices, value="protein",label=f"Sequence Type", scale=1)
                    chain_box = gr.Textbox(label=f"Chain", value=chr(ord('A') + i), scale=1)
                    seq_box = gr.Textbox(label=f"Sequence", scale=5)

                    dropdowns.append(dropdown)
                    chain_boxes.append(chain_box)
                    seq_boxes.append(seq_box)

        if not ASTEXT:
            html_structure_boltz = gr.HTML(label="Structure")
        else:
            html_structure_boltz = gr.Textbox(label="Structure")
        
        add_btn = gr.Button("➕ Add Sequence (protein,ligand,D/RNA) ", size="sm")
        run_btn = gr.Button("Run", variant="primary")

        def add_row(visible_count):
            return min(visible_count + 1, MAX_ROWS)
        def update_row_visibility(visible_count):
            return [gr.update(visible=(i < visible_count)) for i in range(MAX_ROWS)]
        
        def process_all(visible_count, *all_inputs):
            logging.info("runnning process all of boltz-1")

            dropdowns_ = all_inputs[:MAX_ROWS]
            chain_boxes_ = all_inputs[MAX_ROWS:MAX_ROWS*2]
            seq_boxes_ = all_inputs[MAX_ROWS*2:MAX_ROWS*3]

            results = []
            for i in range(visible_count):
                dd_val = dropdowns_[i]
                ch_val = chain_boxes_[i]
                sq_val = seq_boxes_[i]
                results.append(f"{dd_val}_{ch_val}:{sq_val}")
            full_input =  ";".join(results)
            logging.info(full_input)
            return boltz_btn_fn(full_input)
        
        add_btn.click(
            add_row,
            inputs=visible_rows,
            outputs=visible_rows
        ).then(
            update_row_visibility,
            inputs=visible_rows,
            outputs=[row for row in rows_container.children if isinstance(row, gr.Row)]
        )
        run_btn.click(
            process_all,
            inputs=[visible_rows]+ dropdowns + chain_boxes + seq_boxes,
            outputs=html_structure_boltz
        )

        load_btn.click(
            load_example, 
            inputs=[], 
            outputs=[visible_rows]+ dropdowns + chain_boxes + seq_boxes,
        ).then(
            update_row_visibility,
            inputs=visible_rows,
            outputs=[row for row in rows_container.children if isinstance(row, gr.Row)]
        )
            

if __name__ == "__main__":
    demo.launch()