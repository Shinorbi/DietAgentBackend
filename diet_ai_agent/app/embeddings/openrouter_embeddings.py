from langchain_openai import OpenAIEmbeddings
from openai import AzureEmbeddings

def get_embeddings():
    """Initialize and return the Nemotron embeddings instance"""
    embeddings = OpenAIEmbeddings(
        model="nvidia/llama-nemotron-embed-vl-1b-v2:free",
        openai_api_base="https://openrouter.ai/api/v1",
        openai_api_key_name="EMBEDDING_KEY"
    )
    return embeddings

def embed_documents(docs):
    """Embed a list of documents"""
    embeddings = get_embeddings()
    return embeddings.embed_documents(docs)

def embed_query(query):
    """Embed a query"""
    embeddings = get_embeddings()
    return embeddings.embed_query(query)