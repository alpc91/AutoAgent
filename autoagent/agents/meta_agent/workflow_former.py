from autoagent.registry import register_agent
from autoagent.tools.meta.edit_agents import list_agents, create_agent, delete_agent, run_agent, read_agent
from autoagent.tools.meta.edit_tools import list_tools, create_tool, delete_tool, run_tool
from autoagent.tools.meta.edit_workflow import list_workflows
from autoagent.tools.terminal_tools import execute_command
from autoagent.types import Agent
from autoagent.io_utils import read_file
from pydantic import BaseModel, Field
from typing import List
import json


@register_agent(name="Workflow Former Agent", func_name="get_workflow_former_agent")
def get_workflow_former_agent(model: str) -> str:
    """
    这个智能代理用于创建一个json，该json可用于创建由多个代理组成的协作流程。
    """
    def instructions(context_variables):
        # workflow_list = list_workflows(context_variables)
        # workflow_list = json.loads(workflow_list)
        # workflow_list = [workflow_name for workflow_name in workflow_list.keys()]
        # workflow_list_str = ", ".join(workflow_list)
        return r"""\-
您是一个专门用于创建多智能代理协作工作流json的智能代理。

您的任务是分析用户请求并生成用于创建由多个代理组成的流程的结构化json。

「json包含以下必要字段」：
1. "agents" - 所有参与协作流程的智能代理的名称。它应该是一个列表格式，其中每一项是一个字典。每一个字典包含两个字段：第一个字段的关键词是"id"，它的值是一个字符串元素,固定为空字符串，表示智能代理的id；第二个字段的关键词是"name"，它的值，也是一个字符串元素，代表智能代理的名称。

2. "relations" - 智能代理之间的协作关系。它应该是一个列表格式，其中每一项是一个字典。每一个字典包含两个字段：第一个字段的关键词是"input"，它的值是一个字符串元素，表示一个智能代理的名称；第二个字段的关键词是"output"，它的值，也是一个字符串元素，表示另一个智能代理的名称。该字典表示"output"智能代理依赖"input"智能代理的执行结果。

""" + \
f"""
可以使用的现有智能代理包括： 
{list_agents(context_variables)}
""" + \
r"""  

结构化json数据说明：
1. 这个json应该包含所有参与协作流程的智能代理的名称。
2. 这个json应该包含所有参与协作流程的智能代理之间的协作关系。
3. 这个json必须包含且仅包含这两个字段。
4. 这个json应该是有效的python中json格式。
5. 这个json的标点符号应该是英文的。

智能代理说明：
1. 每个智能代理的名称应该是一个字符串，表示该智能代理的名称。
2. 除了从现有的智能代理中选择的用于具体流程执行的智能代理外，每一个json都应该包含一个系统级智能代理，该智能代理作为流程的起始点和终止点。这个系统级智能代理的名称应该是"系统级智能代理"。

协作关系说明：
1. 代理之间的协作关系是通过字典来表示的。每个字典包含两个关键词，第一个关键词是"input"，是一个智能代理的名称；第二个关键词是"output"，是另一个智能代理名称，该字典表示"output"智能代理依赖"input"智能代理的执行结果。
2. 如果两个智能代理之间没有依赖关系，则他们的字典不需要出现在列表中。
3. 保证字典中"input"智能代理在"output"智能代理之前执行。
4. 保证这个字典列表中体现了智能代理之间的所有协作关系。
5. 协作关系列表应当用方括号[]而不是花括号{}。
6. 协作关系的字典应当用花括号{}而不是方括号[]。

""" + \
r"""
** EXAMPLE:

用户：我想构建一个智能代理协作工作流程，帮助我撰写一篇关于用户主题的类似维基百科的文章。它应该：
1. 在网上搜索用户主题。
2. 为用户主题撰写大纲。
3. 评估大纲。如果大纲不够好，重复大纲步骤，否则继续撰写文章。
4. 撰写文章。

流程json应为：
{
    "agents": [
        {"id":"", "name": "系统级智能代理"},
        {"id":"", "name": "页面搜索智能代理"},
        {"id":"", "name": "大纲撰写智能代理"},
        {"id":"", "name": "评估智能代理"},
        {"id":"", "name": "文章撰写智能代理"}
    ],
    "relations": [
        {"input":"系统级智能代理","output":"页面搜索智能代理"},
        {"input":"页面搜索智能代理","output":"大纲撰写智能代理"},
        {"input":"大纲撰写智能代理","output":"评估智能代理"},
        {"input":"评估智能代理","output":"文章撰写智能代理"},
        {"input":"评估智能代理","output":"大纲撰写智能代理"},
        {"input":"文章撰写智能代理","output":"系统级智能代理"}
    ]
}

指导原则：
1. 系统级智能代理作为整个协作流程的第一个协作流程的输入智能代理。
2. 系统级智能代理作为整个协作流程的最后一个协作流程的输出智能代理。
3. 包含审核步骤以进行质量控制。

根据示例和指导原则，根据用户需求创建适当的流程json。
"""
    return Agent(
        name = "Workflow Former Agent",
        model = model,
        instructions = instructions,
    )

# if __name__ == "__main__":
#     from autoagent import MetaChain
#     agent = get_workflow_former_agent("hosted_vllm/Qwen/QwQ-32B-AWQ")
#     client = MetaChain()
# #     task_yaml = """\
# # I want to create a workflow that can help me to solving the math problem.

# # The workflow should:
# # 2. Parallelize solving the math problem with the same `Math Solver Agent` using different language models (`gpt-4o-2024-08-06`, `hosted_vllm/Qwen/QwQ-32B-AWQ`, `deepseek/deepseek-chat`)
# # 3. Aggregate the results from the `Math Solver Agent` and return the final result using majority voting.

# # Please create the form of this workflow in the XML format.
# # """
#     task_yaml = """\
# I want to create a workflow that can help me to solving the math problem.

# The workflow should:
# 1. The `Objective Extraction Agent` will extract the objective of the math problem.
# 2. The `Condition Extraction Agent` will extract the conditions of the math problem.
# 3. The `Math Solver Agent` will evaluate whether the conditions are enough to solve the math problem: if yes, solve the math problem; if no, return to the `Condition Extraction Agent` to extract more conditions.

# Please create the form of this workflow in the XML format.
# """
#     task_yaml = task_yaml + """\
# Directly output the form in the XML format.
# """
#     messages = [{"role": "user", "content": task_yaml}]
#     response = client.run(agent, messages)
#     print(response.messages[-1]["content"])