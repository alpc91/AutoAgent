from autoagent.types import Agent
from autoagent.tools import save_raw_docs_to_vector_db

from autoagent.registry import register_plugin_agent

@register_plugin_agent(name="Initialization Agent", func_name="get_initialization_agent")
def get_initialization_agent(model: str):
    '''
    The Initialization Agent is responsible for setting up the vector database by saving the raw documents into the knowledge base.
    '''
    instructions = "You are an Initialization Agent. Your task is to initialize the process by establishing the vector database using the `save_raw_docs_to_vector_db` tool with the parameter `doc_name='db', saved_vector_db_name='rag_db'`. This step is foundational and must be completed before any other tasks can proceed. If the collection `rag_db` of the vector database already exists, you do not need to repeat establishing the vector database."
    return Agent(
    name="Initialization Agent",
    model=model,
    instructions=instructions,
    functions=[save_raw_docs_to_vector_db]
    )

