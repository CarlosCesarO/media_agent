from google.cloud import bigquery
from google.oauth2 import service_account
from app.core.config import settings
from google.api_core.exceptions import GoogleAPIError


def get_bq_client() -> bigquery.Client:
    credentials = service_account.Credentials.from_service_account_file(
        settings.gcp_credentials_path,
        scopes=["https://www.googleapis.com/auth/cloud-platform"],
    )
    return bigquery.Client(
        project=settings.google_cloud_project,
        credentials=credentials,
    )


def run_query(sql: str, params: list | None = None) -> list[dict]:
    try:
        client = get_bq_client()
        job_config = bigquery.QueryJobConfig()
        if params:
            job_config.query_parameters = params
        query_job = client.query(sql, job_config=job_config)
        results = query_job.result()
        return [dict(row) for row in results]
    except GoogleAPIError as e:
        raise RuntimeError(f"Erro no BigQuery: {e.message}") from e