# -*- coding: utf-8 -*-

from autoagent.types import Agent

from autoagent.registry import register_plugin_agent

@register_plugin_agent(name="分解任务智能代理", func_name="get_task_decomposition_agent")
def get_math_solver_agent(model: str):
    '''
    这个智能体用于对解析后的任务和现实可行的最终目标进行分析，分解任务，形成分阶段的子步骤和子目标，形成格式化的json输出。
    '''
    instructions = '您是负责任务分解的智能助手，您需要：\n1. 理解已解析的任务内容和确定的现实可行目标\n2. 将复杂任务分解为有序的子任务和子目标\n3. 确定每个子任务的优先级、依赖关系和完成标准\n4. 为每个子任务分配所需资源和时间估计\n5. 设计清晰的任务执行路径和里程碑\n6. 将任务分解结果整理为格式化的JSON输出'
    return Agent(
    name="分解任务智能代理",
    model=model,
    instructions=instructions,
    functions=[]
    )

