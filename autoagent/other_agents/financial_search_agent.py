from autoagent.types import Agent
from autoagent.tools import query_db
from autoagent.tools import modify_query
from autoagent.tools import answer_query
from autoagent.tools import can_answer

from autoagent.registry import register_plugin_agent

@register_plugin_agent(name="Financial Search Agent", func_name="get_financial_search_agent")
def get_financial_search_agent(model: str):
    '''
    The Financial Search Agent is responsible for searching and retrieving financial information such as balance sheets, cash flow statements, and income statements for a given ticker over a specified period.
    '''
    instructions = 'You are a Financial Search Agent. Your task is to search and retrieve financial information (balance sheets, cash flow statements, or income statements) for a given ticker over a specified period using the hosted_vllm/Qwen/QwQ-32B-AWQ language model.'
    return Agent(
    name="Financial Search Agent",
    model=model,
    instructions=instructions,
    functions=[query_db, modify_query, answer_query, can_answer]
    )

