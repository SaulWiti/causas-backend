import os
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

class Config(BaseSettings):
    # Auth
    api_key_auth: str = Field(alias="API_KEY_AUTH")

    # MongoDB
    mongodb_uri: str = Field(alias="URI_MONGO")
    name_db_mongo: str = Field(alias="NAME_DB_MONGO")

    # Azure OpenAI
    azure_openai_endpoint: str = Field(alias="AZURE_OPENAI_ENDPOINT")
    azure_openai_api_key: str = Field(alias="AZURE_OPENAI_API_KEY")
    openai_api_version: str = Field(alias="OPENAI_API_VERSION")

    # Facebook-WhatsApp
    graph_facebook_url: str = Field(alias="GRAPH_FACEBOOK_URL")
    whatsapp_phone_id: str = Field(alias="WHATSAPP_PHONE_ID")
    whatsapp_api_key: str = Field(alias="WHATSAPP_API_KEY")

    def model_post_init(self, __context):
        os.environ["AZURE_OPENAI_ENDPOINT"] = self.azure_openai_endpoint
        os.environ["AZURE_OPENAI_API_KEY"] = self.azure_openai_api_key

        os.environ["OPENAI_API_VERSION"] = self.openai_api_version
        
        os.environ["API_KEY_AUTH"] = self.api_key_auth
        
        os.environ["URI_MONGO"] = self.mongodb_uri
        os.environ["NAME_DB_MONGO"] = self.name_db_mongo

        os.environ["GRAPH_FACEBOOK_URL"] = self.graph_facebook_url
        os.environ["WHATSAPP_PHONE_ID"] = self.whatsapp_phone_id
        os.environ["WHATSAPP_API_KEY"] = self.whatsapp_api_key

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

config = Config()
