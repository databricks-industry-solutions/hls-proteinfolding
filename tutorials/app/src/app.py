""" Run and view protein structure predictions

 - gradio app
 - Use py3dMol for viewing 

notes
-----
used for setting up html for 3Dmol.js:
https://github.com/gradio-app/gradio/issues/791
https://huggingface.co/blog/spaces_3dmoljs
"""
import gradio as gr
import logging
from databricks.sdk import WorkspaceClient
# from databricks.sdk.service.serving import ChatMessage, ChatMessageRole
import os
from typing import Optional,List,Union

import py3Dmol
from Bio.PDB.MMCIFParser import MMCIFParser
from Bio.PDB.PDBParser import PDBParser
from Bio.PDB.PDBIO import PDBIO
import tempfile

from structure_utils import select_and_align
from protein_design import make_designs

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize the Databricks Workspace Client
workspace_client = WorkspaceClient()

# Ensure environment variable is set correctly
assert os.getenv('SERVING_ENDPOINT'), "SERVING_ENDPOINT must be set in app.yaml."

USE_DUMMY = False
ASTEXT = False

HTML_HEAD = """<head>    
    <meta http-equiv="content-type" content="text/html; charset=UTF-8" />
    <style>
    .mol-container {
    width: 100%;
    height: 500px;
    position: relative;
    }
    .mol-container select{
        background-image:None;
    }
    </style>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/jquery/3.6.3/jquery.min.js" integrity="sha512-STof4xm1wgkfm7heWqFJVn58Hm3EtS31XFaagaa8VMReCXAkQnJZ+jEy8PCC/iT18dFy95WcExNHFTqLyp72eQ==" crossorigin="anonymous" referrerpolicy="no-referrer"></script>
    <script src="https://3Dmol.org/build/3Dmol-min.js"></script>
    <script src="https://3Dmol.org/build/3Dmol.ui-min.js"></script>     
</head>"""
#     <script src="https://3Dmol.csb.pitt.edu/build/3Dmol-min.js"></script>

def dummy_pdb():
    fpath = "dummy_pdb.pdb"
    with open(fpath, 'r') as f:
        lines = f.readlines()
    return ''.join(lines)

def query_esmfold(protein : str) -> str:
    """
    Query ESMfold with input sequence
    """
    if not protein.strip():
        return "ERROR: The question should not be empty"

    try:
        logger.info(f"Sending request to model endpoint: {os.getenv('SERVING_ENDPOINT')}")
        response = workspace_client.serving_endpoints.query(
            name=os.getenv('SERVING_ENDPOINT'),
            inputs=[protein]
        )
        logger.info("Received response from model endpoint")
        return response.predictions[0]
    except Exception as e:
        logger.error(f"Error querying model: {str(e)}", exc_info=True)
        return f"Error: {str(e)}"

def _cif_to_pdb_str(cif_str:str)->str:
    with tempfile.TemporaryDirectory() as tmpdir:
        my_cif_path = os.path.join(tmpdir, 'my_cif.cif')
        my_pdb_path = os.path.join(tmpdir, 'my_pdb.cif')
        with open(my_cif_path, 'w') as f:
            f.write(cif_str)
        structure = MMCIFParser().get_structure('download',my_cif_path)
        io=PDBIO()
        io.set_structure(structure)
        io.save(my_pdb_path)
        with open(my_pdb_path,'r') as f:
            lines = f.readlines()
        pdb_str = ''.join(lines)
    return pdb_str

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

def html_as_iframe(html : str) -> str:
    return f"""<iframe style="width: 100%; height: 480px" name="result" allow="midi; geolocation; microphone; camera; 
    display-capture; encrypted-media;" sandbox="allow-modals allow-forms 
    allow-scripts allow-same-origin allow-popups 
    allow-top-navigation-by-user-activation allow-downloads" allowfullscreen="" 
    allowpaymentrequest="" frameborder="0" srcdoc='{html}'></iframe>"""

def _html_body(pdb : str) -> str:
    body = f"""<body>
        <div id="container" class="mol-container"></div>
        <script>
            let pdb = `{pdb}`"""
    body += """
            $(document).ready(function () {
                const element = $("#container");
                const config = { backgroundColor: "white" };
                const viewer = $3Dmol.createViewer(element, config);
                viewer.addModel(pdb, "pdb");
                viewer.getModel(0).setStyle({}, { cartoon: {
                     colorscheme:"blueCarbon" 
                     } 
                });
                viewer.zoomTo();
                viewer.render();
                })
        </script>
    </body>"""
    return body

# def _html_body(pdb: str) -> str:
#     body = f"""<!DOCTYPE html>
#         <html lang="en">
#         <head>
#             <meta charset="UTF-8">
#             <meta name="viewport" content="width=device-width, initial-scale=1.0">
#             <title>Mol* Viewer with Inline PDB Data</title>
#             <script src="https://cdn.jsdelivr.net/npm/molstar@latest/build/viewer/molstar.js"></script>
#             <link rel="stylesheet" type="text/css" href="https://cdn.jsdelivr.net/npm/molstar@latest/build/viewer/molstar.css" />
#             <style>
#                 #viewer {{
#                     position: relative;
#                     width: 800px;
#                     height: 600px;
#                 }}
#             </style>
#         </head>
#         <body>
#             <div id="viewer"></div>
#             <script>
#                 // PDB data as a string (this is a simplified example, you would include the full PDB data here)
#                 const pdbData = `{pdb}`;

#                 molstar.Viewer.create('viewer', {{
#                     layoutIsExpanded: false,
#                     layoutShowControls: true,
#                     layoutShowSequence: true,
#                     layoutShowLog: false,
#                     layoutShowLeftPanel: false,
#                     viewportShowExpand: true,
#                     viewportShowSelectionMode: false,
#                     viewportShowAnimation: false,
#                 }}).then(viewer => {{
#                     // Load the PDB data from the string
#                     viewer.loadStructureFromData(pdbData, 'pdb', false);
#                 }});
#             </script>
#         </body>
#         </html>"""
#     return body

# def _html_multipdb_body(pdbs : List[str]) -> str:
#     if len(pdbs)!=2:
#         logging.error('only support 2 proteins in multiviewer')
#     body = f"""<body>
#         <div id="container" class="mol-container"></div>
#         <script>
#             let pdb = `{pdbs[0]}`"""
#     body += f"""
#             let pdbtwo = `{pdbs[1]}`"""
#     body += """
#             $(document).ready(function () {
#                 const element = $("#container");
#                 const config = { backgroundColor: "white" };
#                 const viewer = $3Dmol.createViewer(element, config);
#                 viewer.addModel(pdb, "pdb");
#                 viewer.getModel(0).setStyle({}, { cartoon: {
#                      colorscheme:"blueCarbon" 
#                      } 
#                 });
#                 viewer.addModel(pdbtwo, "pdb");
#                 viewer.getModel(1).setStyle({}, { cartoon: {
#                      colorscheme:"greenCarbon" 
#                      } 
#                 });
#                 viewer.zoomTo();
#                 viewer.render();
#                 })
#         </script>
#     </body>"""
#     return body

def _html_multipdb_body(pdbs : List[str], colors=None) -> str:
    # if len(pdbs)!=2:
    #     logging.error('only support 2 proteins in multiviewer')
    
    if colors is None:
        colors = ['blueCarbon'] + ['greenCarbon']*(len(pdbs)-1)
    if isinstance(colors, str):
        colors = [colors]*len(pdbs)

    body = f"""<body>
        <div id="container" class="mol-container"></div>
        <script>"""
    for i in range(len(pdbs)):
        body += f"""
                let pdb_{i} = `{pdbs[i]}`"""
    body += """
            $(document).ready(function () {
                const element = $("#container");
                const config = { backgroundColor: "white" };
                const viewer = $3Dmol.createViewer(element, config);"""
    for i in range(len(pdbs)):
        body += f"""
            viewer.addModel(pdb_{i}, "pdb_{i}");
            viewer.getModel({i}).setStyle({{}}, {{ cartoon: {{colorscheme:"{colors[i]}"}} }});"""
    body += """
        viewer.zoomTo();
        viewer.render();
        })
        </script>
        </body>"""
    return body

def html_direct_from_protein_(pdb : str | List[str]) -> str:
    html = "<html>"
    html += HTML_HEAD
    # html = ""
    if isinstance(pdb, str):
        html += _html_body(pdb)
    else:
        logging.info('constructing html body from multiple pdbs')
        html += _html_multipdb_body(pdb)
    html += "</html>"
    return html 

def pdb_btn_fn(protein : str) -> str:
    if not USE_DUMMY:
        pdb = query_esmfold(protein)
    else:
        pdb = dummy_pdb()
    html = html_as_iframe(
        html_direct_from_protein_(pdb)
    )
    return html

def af_btn_fn(run_name : str, pdb_code : Optional[str] = None, include_pdb : bool = False) -> str:
    
    pdb_run = pull_alphafold_run(run_name)
    if include_pdb:
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
            true_structure_str, af_structure_str = select_and_align(
                true_structure, af_structure
            )
        logging.info('sending two pdb str to html')
        html = html_as_iframe(
            html_direct_from_protein_([af_structure_str, true_structure_str])
        )
    else:
        html = html_as_iframe(
            html_direct_from_protein_(pdb_run)
        )
        # html = html_direct_from_protein_(pdb_run)
    return html

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

def af_run_btn_fn(run_name : str, protein : str) -> str:
    run_id = workspace_client.jobs.run_now(
        job_id=get_job_id(job_name='alphafold'),
        job_parameters = {
            'protein':protein,
            'run_name':run_name
        }
    )
    return "started run"

def design_btn_fn(sequence: str) -> str:
    n_rf_diffusion: int = 1
    designed_pdbs = make_designs(sequence)

    with tempfile.TemporaryDirectory() as tmpdir:
        for i in range(len(designed_pdbs['designed'])):
            with open(os.path.join(tmpdir,f"d_{i}_structure.pdb"), 'w') as f:
                f.write(designed_pdbs['designed'][i])
        with open(os.path.join(tmpdir,"init_structure.pdb"), 'w') as f:
            f.write(designed_pdbs['initial'])

        init_structure = PDBParser().get_structure("esmfold_initial", os.path.join(tmpdir,"init_structure.pdb"))
        unaligned_structures = []
        for i in range(len(designed_pdbs['designed'])):
            unaligned_structures.append( PDBParser().get_structure("designed", os.path.join(tmpdir,f"d_{i}_structure.pdb")) )

    aligned_structures = []
    for i, ua in enumerate(unaligned_structures):
        init_structure_str, true_structure_str = select_and_align(
            init_structure, ua
        )
        if i==0:
            aligned_structures.append(init_structure_str)  
        aligned_structures.append(true_structure_str)               

    html = html_as_iframe(html_direct_from_protein_(aligned_structures))
    return html

with gr.Blocks() as demo:
    gr.Markdown(
        """
        # Protein Structure Prediction App

        """)
    with gr.Tab('ESMfold'):
        gr.Markdown(
        """
        # Protein Structure Prediction with ESMfold!
        Enter a protein sequence and view the structure.

        """)
        with gr.Accordion("Details", open=False) as accordion:
            gr.Markdown("""
                #### Details
                Use the ESMfold model serving [endpoint](https://adb-830292400663869.9.azuredatabricks.net/ml/endpoints/esmfold?o=830292400663869) to get pdb structure for a protein sequence of interest.
            """)
        with gr.Row():
            protein = gr.Textbox(label="Protein",scale=4)
            btn = gr.Button("Predict", scale=1)

        if not ASTEXT:
            html_structure = gr.HTML(label="Structure")
        else:
            html_structure = gr.Textbox(label="Structure")
        btn.click(
            fn=pdb_btn_fn, 
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
        # Protein Structure Prediction with alphafold!
        You can run a structure prediction or view previous runs

        """)
        with gr.Tab('Run'):
            with gr.Accordion("Details", open=False) as accordion:
                gr.Markdown("""
                    #### Run Details
                    Submits a job run on [this workflow](https://adb-830292400663869.9.azuredatabricks.net/jobs/742976642598070?o=830292400663869). run_name can be any anme you like. For multimers use ":" to split chains. Runs can be picked up in Unity catalog [here](https://adb-830292400663869.9.azuredatabricks.net/explore/data/volumes/protein_folding/alphafold/results?o=830292400663869). 
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
            n_designs = gr.Textbox(label="number of designs",scale=4)
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
            

if __name__ == "__main__":
    demo.launch()