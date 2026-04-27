from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    openai_api_key: str
    google_cloud_project: str
    gcp_credentials_path: str

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()