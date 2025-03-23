from autoagent.types import Agent
from autoagent.tools import query_db
from autoagent.tools import save_raw_docs_to_vector_db

from autoagent.registry import register_plugin_agent

@register_plugin_agent(name="Retrieval Agent", func_name="get_retrieval_agent")
def get_retrieval_agent(model: str):
    '''
    The Retrieval Agent retrieves relevant documents and information from the vector database to support the generation process.
    '''
    instructions = 'Your task is to retrieve relevant documents and information from the vector database using the processed query provided by the Query Processor Agent.'
    return Agent(
    name="Retrieval Agent",
    model=model,
    instructions=instructions,
    functions=[query_db, save_raw_docs_to_vector_db]
    )

