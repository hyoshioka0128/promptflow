from enum import Enum
from typing import Union

from promptflow.tools.common import handle_openai_error, init_openai_client, init_azure_openai_client
from promptflow.tools.exception import InvalidConnectionType

from promptflow._core.tool import tool
from promptflow.connections import AzureOpenAIConnection, OpenAIConnection
try:
    from promptflow.connections import ServerlessConnection
except ImportError:
    # If unable to import ServerlessConnection, define a placeholder class to allow isinstance checks to pass.
    # ServerlessConnection was introduced in pf version 1.6.0.
    class ServerlessConnection:
        pass


class EmbeddingModel(str, Enum):
    TEXT_EMBEDDING_ADA_002 = "text-embedding-ada-002"
    TEXT_SEARCH_ADA_DOC_001 = "text-search-ada-doc-001"
    TEXT_SEARCH_ADA_QUERY_001 = "text-search-ada-query-001"


@tool
@handle_openai_error()
def embedding(
    connection: Union[AzureOpenAIConnection, OpenAIConnection, ServerlessConnection],
    input: str,
    deployment_name: str = "",
    model: EmbeddingModel = EmbeddingModel.TEXT_EMBEDDING_ADA_002
):
    if isinstance(connection, AzureOpenAIConnection):
        client = init_azure_openai_client(connection)
        return client.embeddings.create(
            input=input,
            model=deployment_name,
            extra_headers={"ms-azure-ai-promptflow-called-from": "aoai-tool"}
        ).data[0].embedding
    elif isinstance(connection, OpenAIConnection):
        client = init_openai_client(connection)
        return client.embeddings.create(
            input=input,
            model=model
        ).data[0].embedding
    elif isinstance(connection, ServerlessConnection):
        client = init_openai_client(connection)
        return client.embeddings.create(
            input=[input],
            model=model,
            encoding_format="float"
        ).data[0].embedding
    else:
        error_message = f"Not Support connection type '{type(connection).__name__}' for embedding api. " \
                        f"Connection type should be in [AzureOpenAIConnection, OpenAIConnection]."
        raise InvalidConnectionType(message=error_message)
