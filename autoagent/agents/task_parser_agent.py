# -*- coding: utf-8 -*-

from autoagent.types import Agent

from autoagent.registry import register_plugin_agent

@register_plugin_agent(name="任务解析智能代理", func_name="get_task_parser_agent")
def get_math_solver_agent(model: str):
    '''
    这个智能体用于对任务进行解析，从而能够理解任务，形成格式化的json输出。
    '''
    instructions = '您是负责解析任务的智能助手，您需要：\n1. 理解提供的任务内容和目标；\n2. 提供清晰的任务结构和逻辑关系；\n3. 将分析结果整理为格式化的JSON输出。'
    return Agent(
    name="任务解析智能代理",
    model=model,
    instructions=instructions,
    functions=[]
    )

