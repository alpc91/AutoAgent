from autoagent.types import Agent
from autoagent.tools import aggregate_responses

from autoagent.registry import register_plugin_agent

@register_plugin_agent(name="Aggregation Agent", func_name="get_aggregation_agent")
def get_aggregation_agent(model: str):
    '''
    The Aggregation Agent aggregates and refines the responses from multiple agents to produce a final, cohesive output.
    '''
    instructions = "Your task is to aggregate and refine the responses from the Query Processor Agent, Retrieval Agent, and Generation Agent to produce a final, cohesive output. Ensure that the final response is comprehensive and addresses all aspects of the user's query."
    return Agent(
    name="Aggregation Agent",
    model=model,
    instructions=instructions,
    functions=[aggregate_responses]
    )

