import os
import requests
import json
import logging
import mlflow
from databricks.sdk import WorkspaceClient

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
workspace_client = WorkspaceClient()

def hit_model_endpoint(endpoint_name, inputs) -> str:
    """
    Query endpoint with input
    """
    try:
        logger.info(f"Sending request to model endpoint: {endpoint_name}")
        response = workspace_client.serving_endpoints.query(
            name=endpoint_name,
            inputs=inputs
        )
        logger.info("Received response from model endpoint")
        return response.predictions
    except Exception as e:
        logger.error(f"Error querying model: {str(e)}", exc_info=True)
        return f"Error: {str(e)}"
    
@mlflow.trace(span_type="LLM")
def hit_esmfold(sequence):
    return hit_model_endpoint('esmfold', [sequence])[0]

@mlflow.trace(span_type="TOOL")
def hit_rfdiffusion(input_dict):
    return hit_model_endpoint('rfdiffusion_inpainting', [input_dict])[0]

@mlflow.trace(span_type="TOOL")
def hit_proteinmpnn(pdb_str):
    return hit_model_endpoint('proteinmpnn', [pdb_str])

def _get_sp_token(base_url, sp_id, sp_oauth_token):
        token_url = f"{base_url}/oidc/v1/token"
        response = requests.post(
            token_url,
            auth=(sp_id, sp_oauth_token),
            data={'grant_type': 'client_credentials', 'scope': 'all-apis'}
        )
        token = response.json().get('access_token')
        logging.info(f"got token: (first two char are) {token[:2]}")
        return token

def run_boltz_model(ds_dict):
    token = _get_sp_token(
        base_url = f"https://{os.environ['DATABRICKS_HOST']}",
        sp_id = os.environ['DATABRICKS_CLIENT_ID'],
        sp_oauth_token = os.environ['DATABRICKS_CLIENT_SECRET']
    )
    url = f"https://{os.environ['DATABRICKS_HOST']}/serving-endpoints/{os.getenv('BOLTZ_SERVING_ENDPOINT')}/invocations"
    logging.info(f"hitting {url}")
    headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}
    data_json = json.dumps(ds_dict, allow_nan=True)
    response = requests.request(method='POST', headers=headers, url=url, data=data_json)
    if response.status_code != 200:
        raise Exception(f'Request failed with status {response.status_code}, {response.text}')
    return response.json()

def _format_boltz_input(indict):
    return {
        'dataframe_split':{
        "columns": [
        "input",
        "msa",
        "use_msa_server"
        ],
        "data": [
        [
            indict['input'],
            indict["msa"],
            indict["use_msa_server"]
        ]
        ]
    }     
    }

@mlflow.trace(span_type="LLM")
def hit_boltz(protein : str) -> str:
    """
    Query Boltz with input sequence
    """
    if not protein.strip():
        return "ERROR: The question should not be empty"

    try:
        logger.info(f"Sending request to model endpoint: {os.getenv('BOLTZ_SERVING_ENDPOINT')}")

        in_dict = {
            'input':protein,
            'msa':'no_msa',
            'use_msa_server':'False'
        }
        in_dict = _format_boltz_input(in_dict)
        logging.info(f"submitting: {in_dict}")
        response = run_boltz_model(in_dict)
        logger.info("Received response from model endpoint")
        return response['predictions'][0]['pdb']
    except Exception as e:
        logger.error(f"Error querying model: {str(e)}", exc_info=True)
        return f"Error: {str(e)}"