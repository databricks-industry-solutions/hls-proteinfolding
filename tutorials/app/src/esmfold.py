
from databricks.sdk import WorkspaceClient
from structure_utils import select_and_align

workspace_client = WorkspaceClient()

def query_esmfold(protein : str) -> str:
    """
    Query ESMfold with input sequence
    """
    if not protein.strip():
        return "ERROR: The question should not be empty"

    try:
        logger.info(f"Sending request to model endpoint: {os.getenv('ESMFOLD_SERVING_ENDPOINT')}")
        response = workspace_client.serving_endpoints.query(
            name=os.getenv('ESMFOLD_SERVING_ENDPOINT'),
            inputs=[protein]
        )
        logger.info("Received response from model endpoint")
        return response.predictions[0]
    except Exception as e:
        logger.error(f"Error querying model: {str(e)}", exc_info=True)
        return f"Error: {str(e)}"
    