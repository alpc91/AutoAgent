from autoagent.types import Agent
from autoagent.tools import modify_query
from autoagent.tools import query_db
from autoagent.tools import can_answer

from autoagent.registry import register_plugin_agent

@register_plugin_agent(name="Query Processor Agent", func_name="get_query_processor_agent")
def get_query_processor_agent(model: str):
    '''
    The Query Processor Agent processes user queries, modifies them if necessary, and routes them to the appropriate agents for retrieval and generation.
    '''
    instructions = 'You are responsible for processing and modifying user queries as needed. Use the tools provided to enhance the query before passing it on to other agents.'
    return Agent(
    name="Query Processor Agent",
    model=model,
    instructions=instructions,
    functions=[modify_query, query_db, can_answer]
    )

