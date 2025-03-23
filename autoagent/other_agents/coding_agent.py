from autoagent.types import Agent
from autoagent.tools import execute_command

from autoagent.registry import register_plugin_agent

@register_plugin_agent(name="Coding Agent", func_name="get_coding_agent")
def get_coding_agent(model: str):
    '''
    Writes and executes code to calculate date differences via execute_command
    '''
    instructions = 'When given a date calculation task, generate Python code as a string, then execute it using execute_command with the command formatted as \'python -c "CODE_HERE"\'. Extract the numerical result from the command output.'
    return Agent(
    name="Coding Agent",
    model=model,
    instructions=instructions,
    functions=[execute_command]
    )

