from autoagent.types import Agent
from autoagent.tools import answer_query
from autoagent.tools import visual_question_answering

from autoagent.registry import register_plugin_agent

@register_plugin_agent(name="Generation Agent", func_name="get_generation_agent")
def get_generation_agent(model: str):
    '''
    The Generation Agent generates responses based on the retrieved documents and user context, ensuring that the output is coherent and contextually relevant.
    '''
    instructions = "Your task is to generate a coherent and contextually relevant response based on the retrieved documents and user context. Ensure that the response addresses the user's query comprehensively."
    return Agent(
    name="Generation Agent",
    model=model,
    instructions=instructions,
    functions=[answer_query, visual_question_answering]
    )

