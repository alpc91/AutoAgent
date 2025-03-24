# -*- coding: utf-8 -*-

from autoagent.types import Agent

from autoagent.registry import register_plugin_agent

@register_plugin_agent(name="评估预测智能代理", func_name="get_evaluate_predictive_agent")
def get_math_solver_agent(model: str):
    '''
    这个智能体用于根据已解析的任务内容和确定的现实可行目标，对分析后的任务执行步骤进行评估预测，从而反馈调整任务步骤和预期目标，形成格式化的json输出。
    '''
    instructions = '您是负责任务评估预测的智能助手，您需要：\n1. 理解已解析的任务内容和确定的现实可行目标\n2. 分析提出的任务执行步骤的可行性和效率\n3. 预测每个步骤可能遇到的障碍和风险\n4. 评估最终目标的达成概率和潜在偏差\n5. 提出针对性的调整建议以优化任务流程\n6. 将评估预测结果整理为格式化的JSON输出'
    return Agent(
    name="评估预测智能代理",
    model=model,
    instructions=instructions,
    functions=[]
    )

