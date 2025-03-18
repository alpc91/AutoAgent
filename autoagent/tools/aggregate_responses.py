from autoagent.types import Result, Agent
from typing import Union
from autoagent.registry import register_plugin_tool

@register_plugin_tool("aggregate_responses")
def aggregate_responses(responses: list, context_variables: dict) -> Union[str, Agent, Result]:
    """
    Combine and refine multiple responses into a single, cohesive output.

    Args:
        responses: A list of responses from different agents or tools.
    Returns:
        A single, cohesive response that aggregates the information from all inputs.
    """
    aggregated_response = '\n'.join([response for response in responses if isinstance(response, str)])
    return Result(value=aggregated_response, context_variables=context_variables)