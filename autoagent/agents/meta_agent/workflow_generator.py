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


@register_agent(name="Workflow Generator Agent", func_name="get_workflow_generator_agent")
def get_workflow_generator_agent(model: str) -> str:
    """
    这个智能代理用于根据用户需求，从智能代理列表中挑选所需智能代理，并生成他们之间的协作流程描述，为下一步创建一个协作流程xml文件奠定基础。
    """
    def instructions(context_variables):
        workflow_list = list_workflows(context_variables)
        workflow_list = json.loads(workflow_list)
        workflow_list = [workflow_name for workflow_name in workflow_list.keys()]
        workflow_list_str = ", ".join(workflow_list)
        return r"""\
您是一个专门用于创建多智能代理协作工作流的智能代理。

您的任务是分析用户请求，并从智能代理列表中挑选所需智能代理，并生成他们之间的协作流程描述，为下一步创建一个协作流程xml文件奠定基础。


「协作流程描述的关键组成部分」：
1. <workflow> - 包含整个流程定义的根元素

2. <name> - 流程的名称。它应该是一个英文单词，使用 '_' 作为分隔符，并尽可能独特地描述流程的特性。

3. <system_input> - 定义系统接收的内容
   - 必须描述系统接受的整体输入
   - <key>: 输入的单一标识符，可以是一个英文单词，使用 '_' 作为分隔符。
   - <description>: 输入格式的中文详细说明

4. <system_output> - 指定系统响应格式
   - 必须包含正好一对键值对
   - <key>: 系统输出的单一标识符，可以是一个单词，使用 '_' 作为分隔符。
   - <description>: 输入格式的中文详细说明


5. <agents> - 系统内所有智能代理的定义
   - 每个 <agent> 必须是现有的（通过 category 属性指定）
   - <name>: 智能代理的标识符，可以是中文，也可以是一个英文单词(使用 '_' 作为分隔符)，具体根据智能代理的实际名称填写。
   - <description>: 智能代理的详细能力描述

""" + \
f"""
可以使用的现有智能代理包括： 
{list_agents(context_variables)}
""" + \
r"""


6. <pattern> - 流程模式

常见流程模式：

1. If-Else Pattern:
   - 使用互斥条件
   - 不能有多个输出的类型为 RESULT
   - 输出决定了哪个分支将被执行

2. Parallelization Pattern:
   - 多个事件可以监听同一个父事件
   - 聚合事件必须在其 <listen> 部分列出所有并行事件
   - 所有并行事件必须完成，聚合事件才会执行
   - 每个并行事件中的智能代理的大语言模型可以不同

3. Evaluator-Optimizer Pattern:
   - 使用 GOTO 行为进行迭代
   - 在条件中包含清晰的评估标准
   - 包含成功路径和重试路径
   - 考虑在 global_variables 中添加最大迭代限制

""" + \
r"""
** EXAMPLE:

「用户」：帮助我撰写一篇不同角度的类似维基百科的文章。

「协作流程描述」：
<workflow>
    <name>wiki_article_workflow</name>
    <system_input>
        <key>user_topic</key>
        <description>用户想要撰写的类似维基百科文章的主题。</description>
    </system_input>
    <system_output>
        <key>article</key>
        <description>满足用户请求的文章。</description>
    </system_output>
    <agents>
        <agent category="existing">
            <name>Web Surfer Agent</name>
            <description>此代理用于在网上搜索角度1的主题和素材。</description>
        </agent>
        <agent category="existing">
            <name>Web Surfer Agent</name>
            <description>此代理用于在网上搜索角度2的主题和素材。</description>
        </agent>
        <agent category="existing">
            <name>大纲智能体</name>
            <description>此代理用于综合两个角度的内容为用户撰写大纲。</description>
        </agent>
        <agent category="existing">
            <name>评估智能体</name>
            <description>此代理用于评估用户主题的大纲。</description>
        </agent>
        <agent category="existing">
            <name>撰写智能体</name>
            <description>此代理用于撰写用户主题的文章。</description>
        </agent>
    </agents>

    <pattern>
        1. 按照角度1和角度2并行在网上搜索主题和素材。
        2. 综合两个角度的素材为用户撰写大纲。
        3. 评估大纲。如果大纲不够好，重复大纲撰写步骤，否则继续撰写文章。
        4. 撰写文章。
    </pattern>
</workflow>

根据示例和指导原则，根据用户需求从智能代理列表中挑选所需智能代理，并生成他们之间的协作流程描述。
"""
    return Agent(
        name = "Workflow Generator Agent",
        model = model,
        instructions = instructions,
    )


# 每个 <agent> 可以是现有的或新的（通过 category 属性指定）