# -*- coding: utf-8 -*-

from autoagent.types import Agent

from autoagent.registry import register_plugin_agent

@register_plugin_agent(name="确定目标智能代理", func_name="get_task_target_agent")
def get_math_solver_agent(model: str):
    '''
    这个智能体用于对解析后的任务进行分析，结合实际情况，确定任务现实可行的最终目标，形成格式化的json输出。
    '''
    instructions = '您是负责确定任务目标的智能助手，您需要：\n1. 理解已解析任务的内容和初步目标\n2. 分析任务在实际环境中的可行性\n3. 识别潜在的限制条件和资源约束\n4. 确定现实可行的最终任务目标\n5. 将目标分析结果整理为格式化的JSON输出'
    return Agent(
    name="确定目标智能代理",
    model=model,
    instructions=instructions,
    functions=[]
    )

