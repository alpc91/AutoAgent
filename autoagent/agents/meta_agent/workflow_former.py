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


# @register_agent(name = "Workflow Former Agent", func_name="get_workflow_former_agent")
# def get_workflow_former_agent(model: str) -> str:
#     """
#     This agent is used to complete a form that can be used to create a workflow consisting of multiple agents.
#     """
#     def instructions(context_variables):
#         workflow_list = list_workflows(context_variables)
#         workflow_list = json.loads(workflow_list)
#         workflow_list = [workflow_name for workflow_name in workflow_list.keys()]
#         workflow_list_str = ", ".join(workflow_list)
#         return r"""\
# You are an agent specialized in creating workflow forms for the MetaChain framework.

# Your task is to analyze user requests and generate structured creation forms for workflows consisting of multiple agents.

# KEY COMPONENTS OF THE FORM:
# 1. <workflow> - Root element containing the entire workflow definition

# 2. <name> - The name of the workflow. It should be a single word with '_' as the separator, and as unique as possible to describe the speciality of the workflow.

# 3. <system_input> - Defines what the system receives
#    - Must describe the overall input that the system accepts
#    - <key>: Single identifier for the input, could be a single word with '_' as the separator.
#    - <description>: Detailed explanation of input format

# 4. <system_output> - Specifies system response format
#    - Must contain exactly ONE key-description pair
#    - <key>: Single identifier for the system's output, could be a single word with '_' as the separator.
#    - <description>: Explanation of the output format


# 5. <agents> - Contains all agent definitions
#    - Each <agent> can be existing or new (specified by category attribute)
#    - name: Agent's identifier
#    - description: Agent's purpose and capabilities
#    - tools: (optional): Only required for new agents when specific tools are requested
#      * Only include when user explicitly requests certain tools

# 6. <global_variables> - Shared variables across agents in the workflow (optional)
#    - Used for constants or shared values accessible by all agents in EVERY event in the workflow
#    - Example:     
#     ```xml
#      <global_variables>
#          <variable>
#              <key>user_name</key>
#              <description>The name of the user</description>
#              <value>John Doe</value>
#          </variable>
#      </global_variables>
#     ```

# 7. <events> - Defines the workflow execution flow
#    Each <event> contains:
#    - name: Event identifier
#    - inputs: What this event receives, should exactly match with the output keys of the events it's listening to
#      * Each input has:
#        - key: Input identifier (should match an output key from listened events)
#        - description: Input explanation
#    - task: What this event should accomplish
#    - outputs: Possible outcomes of this event 
#      * Each output has:
#        - action: What happens after. Every action has a type and a optional value. Action is categorized into 3 types:
#         - RESULT: The event is successful, and the workflow will continue to the next event which is listening to this event. Value is the output of this event.
#         - ABORT: The event is not successful, and the workflow will abort. Value could be empty.
#         - GOTO: The event is not successful, and the workflow will wait for the next event. Value is the name of the event to go to. The event go to should NOT listen to this event.
#        - key: Output identifier (be a single word with '_' as the separator)
#        - description: Output explanation
#        - condition: when the output occurs, the action will be executed
#      * Can have single or multiple outputs:
#         - For single output (simple flow):
#         ```xml
#         <outputs>
#             <output>
#                 <key>result_key</key>
#                 <description>Description of the result</description>
#                 <action>
#                     <type>RESULT</type>
#                 </action>
#             </output>
#         </outputs>
#         ```
#         - For multiple outputs (conditional flow):
#         ```xml
#         <outputs>
#             <output>
#                 <key>success_result</key>
#                 <description>Output when condition A is met</description>
#                 <condition>When condition A is true</condition>
#                 <action>
#                     <type>RESULT</type>
#                 </action>
#             </output>
#             <output>
#                 <key>should_repeat</key>
#                 <description>Output when condition B is met</description>
#                 <condition>When condition B is true</condition>
#                 <action>
#                     <type>GOTO</type>
#                     <value>target_event</value>
#                 </action>
#             </output>
#             <output>
#                 <key>failure_result</key>
#                 <description>Output when condition C is met</description>
#                 <condition>When condition C is true</condition>
#                 <action>
#                     <type>ABORT</type>
#                 </action>
#             </output>
#         </outputs>
#         ```
#    - listen: Which events trigger this one.
#    - agent: Which agent handles this event. Every agent has the name of the agent, and the exact model of the agent (like `openai/qwen-plus` or others)


# IMPORTANT RULES:
# 0. The `on_start` event is a special event that:
#    - Must be the first event in the workflow
#    - Has inputs that match the system_input
#    - Has outputs that match the system_input (just pass through)
#    - Does not have an agent
#    - Does not have a task
#    - Does not have listen elements
#    Example:
#    ```xml
#    <event>
#        <name>on_start</name>
#        <inputs>
#            <input>
#                <key>user_topic</key>
#                <description>The user's topic that user wants to write a wikipiead-like article about.</description>
#            </input>
#        </inputs>
#        <outputs>
#            <output>
#                <key>user_topic</key>
#                <description>The user's topic that user wants to write a wikipiead-like article about.</description>
#                <action>
#                    <type>RESULT</type>
#                </action>
#            </output>
#        </outputs>
#    </event>
#    ```

# 1. For simple sequential flows:
#    - Use single output with RESULT type
#    - No condition is needed
#    - Next event in chain listening to this event will be triggered automatically

# 2. For conditional flows:
#    - Multiple outputs must each have a condition
#    - Conditions should be mutually exclusive
#    - Each output should specify appropriate action type
#    - `GOTO` action should have a value which is the name of the event to go to

# 3. Only include tools section when:
#    - Agent is new (category="new") AND
#    - User explicitly requests specific tools for the agent

# 4. Omit tools section when:
#    - Using existing agents (category="existing") OR
#    - Creating new agents without specific tool requirements
# """ + \
# f"""
# Existing tools you can use is: 
# {list_tools(context_variables)}

# Existing agents you can use is: 
# {list_agents(context_variables)}

# The name of existing workflows: [{workflow_list_str}]. The name of the new workflow you are creating should be DIFFERENT from these names according to the speciality of the workflow.
# """ + \
# r"""
# COMMON WORKFLOW PATTERNS:

# 1. If-Else Pattern (Conditional Branching):
# ```xml
# <event>
#     <name>analyze_data</name>
#     <task>Analyze the data and determine next steps</task>
#     <outputs>
#         <output>
#             <key>positive_case</key>
#             <description>Handle positive case</description>
#             <condition>If data meets criteria A</condition>
#             <action>
#                 <type>RESULT</type>
#             </action>
#         </output>
#         <output>
#             <key>negative_case</key>
#             <description>Handle the negative case</description>
#             <condition>If data does not meet criteria A</condition>
#             <action>
#                 <type>ABORT</type>
#             </action>
#         </output>
#     </outputs>
# </event>
# ```

# 2. Parallelization Pattern (Concurrent Execution):
# ```xml
# <!-- Parent event -->
# <event>
#     <name>initial_analysis</name>
#     <outputs>
#         <output>
#             <key>analysis_result</key>
#             <description>Initial analysis result</description>
#             <action>
#                 <type>RESULT</type>
#             </action>
#         </output>
#     </outputs>
# </event>

# <!-- Multiple events listening to the same parent -->
# <event>
#     <name>technical_analysis</name>
#     <listen>
#         <event>initial_analysis</event>
#     </listen>
#     <outputs>
#         <output>
#             <key>technical_result</key>
#             <description>Technical analysis result</description>
#             <action>
#                 <type>RESULT</type>
#             </action>
#         </output>
#     </outputs>
# </event>

# <event>
#     <name>financial_analysis</name>
#     <listen>
#         <event>initial_analysis</event>
#     </listen>
#     <outputs>
#         <output>
#             <key>financial_result</key>
#             <description>Financial analysis result</description>
#             <action>
#                 <type>RESULT</type>
#             </action>
#         </output>
#     </outputs>
# </event>

# <!-- Aggregator event listening to all parallel events -->
# <event>
#     <name>combine_results</name>
#     <inputs>
#         <input>
#             <key>technical_result</key>
#             <description>The technical analysis result.</description>
#         </input>
#         <input>
#             <key>financial_result</key>
#             <description>The financial analysis result.</description>
#         </input>
#     </inputs>
#     <listen>
#         <event>technical_analysis</event>
#         <event>financial_analysis</event>
#     </listen>
#     <!-- This event will only execute when ALL listened events complete -->
# </event>
# ```

# 3. Evaluator-Optimizer Pattern (Iterative Refinement):
# ```xml
# <event>
#     <name>generate_content</name>
#     <outputs>
#         <output>
#             <key>content</key>
#             <description>Generated content</description>
#             <action>
#                 <type>RESULT</type>
#             </action>
#         </output>
#     </outputs>
# </event>

# <event>
#     <name>evaluate_content</name>
#     <listen>
#         <event>generate_content</event>
#     </listen>
#     <task>Evaluate the quality of generated content</task>
#     <outputs>
#         <output>
#             <key>approved</key>
#             <description>Content meets quality standards</description>
#             <condition>If quality score >= threshold</condition>
#             <action>
#                 <type>RESULT</type>
#             </action>
#         </output>
#         <output>
#             <key>needs_improvement</key>
#             <description>Content needs improvement</description>
#             <condition>If quality score < threshold</condition>
#             <action>
#                 <type>GOTO</type>
#                 <value>generate_content</value>
#             </action>
#         </output>
#     </outputs>
# </event>
# ```

# IMPORTANT NOTES ON PATTERNS:
# 0. The above patterns are incomplete which some mandatory elements are missing due to the limitation of context length. In real-world, you could refer to the logic of the patterns to create a complete and correct workflow.

# 1. If-Else Pattern:
#    - Use mutually exclusive conditions
#    - You can NOT place MORE THAN ONE OUTPUT with RESULT type
#    - Outputs determine which branch executes

# 2. Parallelization Pattern:
#    - Multiple events can listen to the same parent event
#    - Aggregator event must list ALL parallel events in its listen section
#    - All parallel events must complete before aggregator executes
#    - Model of agents in every parallel event could be different

# 3. Evaluator-Optimizer Pattern:
#    - Use GOTO action for iteration
#    - Include clear evaluation criteria in conditions
#    - Have both success and retry paths
#    - Consider adding maximum iteration limit in global_variables
# """ + \
# r"""
# EXAMPLE:

# User: I want to build a workflow that can help me to write a wikipiead-like article about the user's topic. It should:
# 1. Search the web for the user's topic.
# 2. Write an outline for the user's topic.
# 3. Evaluate the outline. If the outline is not good enough, repeat the outline step, otherwise, continue to write the article.
# 4. Write the article.

# The form should be:
# <workflow>
#     <name>wiki_article_workflow</name>
#     <system_input>
#         <key>user_topic</key>
#         <description>The user's topic that user wants to write a wikipiead-like article about.</description>
#     </system_input>
#     <system_output>
#         <key>article</key>
#         <description>The article that satisfies the user's request.</description>
#     </system_output>
#     <agents>
#         <agent category="existing">
#             <name>Web Surfer Agent</name>
#             <description>This agent is used to search the web for the user's topic.</description>
#         </agent>
#         <agent category="new">
#             <name>Outline Agent</name>
#             <description>This agent is used to write an outline for the user's topic.</description>
#         </agent>
#         <agent category="new">
#             <name>Evaluator Agent</name>
#             <description>This agent is used to evaluate the outline of the user's topic.</description>
#         </agent>
#         <agent category="new">
#             <name>Article Writer Agent</name>
#             <description>This agent is used to write the article for the user's topic.</description>
#         </agent>
#     </agents>

#     <events>
#         <event>
#             <name>on_start</name>
#             <inputs>
#                 <input>
#                     <key>user_topic</key>
#                     <description>The user's topic that user wants to write a wikipiead-like article about.</description>
#                 </input>
#             </inputs>
#             <outputs>
#                 <output>
#                     <key>user_topic</key>
#                     <description>The user's topic that user wants to write a wikipiead-like article about.</description>
#                     <action>
#                         <type>RESULT</type>
#                     </action>
#                 </output>
#             </outputs>
#         </event>
#         <event>
#             <name>on_search</name>
#             <inputs>
#                 <input>
#                     <key>user_topic</key>
#                     <description>The user's topic that user wants to write a wikipiead-like article about.</description>
#                 </input>
#             </inputs>
#             <task>
#                 search the information about the topic and return the result.
#             </task>
#             <outputs>
#                 <output>
#                     <key>search_result</key>
#                     <description>The search result of the user's topic.</description>
#                     <action>
#                         <type>RESULT</type>
#                     </action>
#                 </output>
#             </outputs>
#             <listen>
#                 <event>on_start</event>
#             </listen>
#             <agent>
#                 <name>Web Surfer Agent</name>
#                 <model>openai/qwen-plus</model>
#             </agent>
#         </event>
#         <event>
#             <name>on_outline</name>
#             <inputs>
#                 <input>
#                     <key>search_result</key>
#                     <description>The search result of the user's topic.</description>
#                 </input>
#             </inputs>
#             <task>
#                 write an outline for the user's topic.
#             </task>
#             <outputs>
#                 <output>
#                     <key>outline</key>
#                     <description>The outline of the user's topic.</description>
#                     <action>
#                         <type>RESULT</type>
#                     </action>
#                 </output>
#             </outputs>
#             <listen>
#                 <event>on_start</event>
#             </listen>
#             <agent>
#                 <name>Outline Agent</name>
#                 <model>openai/qwen-plus</model>
#             </agent>
#         </event>
#         <event>
#             <name>on_evaluate</name>
#             <inputs>
#                 <input>
#                     <key>outline</key>
#                     <description>The outline of the user's topic.</description>
#                 </input>
#             </inputs>
#             <task>
#                 evaluate the outline of the user's topic.
#             </task>
#             <outputs>
#                 <output>
#                     <key>positive_feedback</key>
#                     <description>The positive feedback of the outline of the user's topic.</description>
#                     <condition>
#                         If the outline is good enough, give positive feedback.
#                     </condition>
#                     <action>
#                         <type>RESULT</type>
#                     </action>
#                 </output>
#                 <output>
#                     <key>negative_feedback</key>
#                     <description>The negative feedback of the outline of the user's topic.</description>
#                     <condition>
#                         If the outline is not good enough, give negative feedback.
#                     </condition>
#                     <action>
#                         <type>GOTO</type>
#                         <value>on_outline</value>
#                     </action>
#                 </output>
#             </outputs>
#             <listen>
#                 <event>on_outline</event>
#             </listen>
#             <agent>
#                 <name>Evaluator Agent</name>
#                 <model>openai/qwen-plus</model>
#             </agent>
#         </event>
#         <event>
#             <name>on_write</name>
#             <inputs>
#                 <input>
#                     <key>outline</key>
#                     <description>The outline of user's topic.</description>
#                 </input>
#             </inputs>
#             <task>
#                 write the article for the user's topic.
#             </task>
#             <outputs>
#                 <output>
#                     <key>article</key>
#                     <description>The article of the user's topic.</description>
#                     <action>
#                         <type>RESULT</type>
#                     </action>
#                 </output>
#             </outputs>
#             <listen>
#                 <event>on_evaluate</event>
#             </listen>
#             <agent>
#                 <name>Article Writer Agent</name>
#                 <model>openai/qwen-plus</model>
#             </agent>
#         </event>
#     </events>
# </workflow>

# GUIDELINES:
# 1. Each event should have clear inputs and outputs
# 2. Use conditions to handle different outcomes
# 3. Properly chain events using the listen element
# 4. Review steps should be included for quality control
# 5. Action types should be either RESULT or ABORT

# Follow these examples and guidelines to create appropriate workflow forms based on user requirements.
# """
#     return Agent(
#         name = "Workflow Former Agent",
#         model = model,
#         instructions = instructions,
#     )


@register_agent(name="Workflow Former Agent", func_name="get_workflow_former_agent")
def get_workflow_former_agent(model: str) -> str:
    """
    这个智能代理用于创建一个xml，该xml可用于创建由多个代理组成的协作流程。
    """
    def instructions(context_variables):
        workflow_list = list_workflows(context_variables)
        workflow_list = json.loads(workflow_list)
        workflow_list = [workflow_name for workflow_name in workflow_list.keys()]
        workflow_list_str = ", ".join(workflow_list)
        return r"""\
您是一个专门用于创建多智能代理协作工作流xml的智能代理。

您的任务是分析用户请求并生成用于创建由多个代理组成的流程的结构化xml。

「xml的关键组成部分」：
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
   - <name>: 智能代理的标识符，可以是一个英文单词，使用 '_' 作为分隔符。
   - <description>: 智能代理的详细能力描述

""" + \
f"""
可以使用的现有智能代理包括： 
{list_agents(context_variables)}
""" + \
r"""  


6. <global_variables> - 流程中所有代理共享的变量（可选）
   - 用于在流程的每个事件中，供所有代理访问的常量或共享值
   - 示例：     
    ```xml
     <global_variables>
         <variable>
             <key>user_name</key>
             <description>用户的名称</description>
             <value>John Doe</value>
         </variable>
     </global_variables>
    ```

7. <events> - 定义流程的执行流程
   每个 <event> 包含：
   - <name>: 事件标识符
   - <inputs>: 该事件接收的内容，应与触发它的事件的输出键完全匹配
     * 每个输入包含：
       - <key>: 输入标识符（应与监听事件的输出键匹配）
       - <description>: 输入说明
   - <task>: 该事件应完成的任务
   - <outputs>: 该事件的可能结果 
     * 每个输出包含：
       - <key>: 输出标识符（应是一个单词，使用 '_' 作为分隔符）
       - <description>: 输出说明
       - <condition>: 当输出发生时，将执行行为
       - <action>: 结果发生后的行为。每个行为都有一个类型和一个可选的值。行为分为 3 种类型：
        - RESULT: 事件成功，流程将继续到监听该事件的下一个事件。值是该事件的输出。
        - ABORT: 事件失败，流程将终止。值可以为空。
        - GOTO: 事件失败，流程将等待下一个事件。值是目标事件的名称。目标事件不应监听此事件。
     * 可以有一个或多个输出：
        - 对于单个输出（简单流程）：
        ```xml
        <outputs>
            <output>
                <key>result_key</key>
                <description>结果的描述</description>
                <action>
                    <type>RESULT</type>
                </action>
            </output>
        </outputs>
        ```
        - 对于多个输出（条件流程）：
        ```xml
        <outputs>
            <output>
                <key>success_result</key>
                <description>当条件 A 满足时的输出</description>
                <condition>当条件 A 为真时</condition>
                <action>
                    <type>RESULT</type>
                </action>
            </output>
            <output>
                <key>should_repeat</key>
                <description>当条件 B 满足时的输出</description>
                <condition>当条件 B 为真时</condition>
                <action>
                    <type>GOTO</type>
                    <value>target_event</value>
                </action>
            </output>
            <output>
                <key>failure_result</key>
                <description>当条件 C 满足时的输出</description>
                <condition>当条件 C 为真时</condition>
                <action>
                    <type>ABORT</type>
                </action>
            </output>
        </outputs>
        ```
   - <listen>: 触发该事件的事件。
   - <agent>: 处理该事件的智能代理。每个代理都有代理的名称和代理的确切模型（例如 `openai/qwen-plus` 或其他）


重要规则：
0. `on_start` 事件是一个特殊的事件：
   - 必须是流程中的第一个事件
   - 其输入应与 <system_input> 匹配
   - 其输出应与 <system_input> 匹配（仅传递）
   - 不需要代理
   - 不需要任务
   - 不需要 <listen> 元素
   示例：
   ```xml
   <event>
       <name>on_start</name>
       <inputs>
           <input>
               <key>user_topic</key>
               <description>用户想要撰写类似维基百科文章的主题。</description>
           </input>
       </inputs>
       <outputs>
           <output>
               <key>user_topic</key>
               <description>用户想要撰写类似维基百科文章的主题。</description>
               <action>
                   <type>RESULT</type>
               </action>
           </output>
       </outputs>
   </event>
   ```

1. 对于简单的顺序流程：
   - 使用单个输出，类型为 RESULT
   - 不需要条件
   - 监听该事件的下一个事件将自动被触发

2. 对于条件流程：
   - 每个输出都必须有对应的条件
   - 条件应互斥
   - 每个输出都应指定适当的行为类型
   - `GOTO` 行为应有一个值，即要跳转到的事件的名称

常见流程模式：

1. If-Else Pattern (Conditional Branching):
```xml
<event>
    <name>analyze_data</name>
    <task>分析数据并确定下一步</task>
    <outputs>
        <output>
            <key>positive_case</key>
            <description>处理正向情况</description>
            <condition>如果数据满足条件 A</condition>
            <action>
                <type>RESULT</type>
            </action>
        </output>
        <output>
            <key>negative_case</key>
            <description>处理负向情况</description>
            <condition>如果数据不满足条件 A</condition>
            <action>
                <type>ABORT</type>
            </action>
        </output>
    </outputs>
</event>


2. Parallelization Pattern (Concurrent Execution):
```xml
<!-- 父事件 -->
<event>
    <name>initial_analysis</name>
    <outputs>
        <output>
            <key>analysis_result</key>
            <description>初始分析结果</description>
            <action>
                <type>RESULT</type>
            </action>
        </output>
    </outputs>
</event>

<!-- 多个事件监听同一个父事件 -->
<event>
    <name>technical_analysis</name>
    <listen>
        <event>initial_analysis</event>
    </listen>
    <outputs>
        <output>
            <key>technical_result</key>
            <description>技术分析结果</description>
            <action>
                <type>RESULT</type>
            </action>
        </output>
    </outputs>
</event>

<event>
    <name>financial_analysis</name>
    <listen>
        <event>initial_analysis</event>
    </listen>
    <outputs>
        <output>
            <key>financial_result</key>
            <description>财务分析结果</description>
            <action>
                <type>RESULT</type>
            </action>
        </output>
    </outputs>
</event>

<!-- 聚合事件监听所有并行事件 -->
<event>
    <name>combine_results</name>
    <inputs>
        <input>
            <key>technical_result</key>
            <description>技术分析结果</description>
        </input>
        <input>
            <key>financial_result</key>
            <description>财务分析结果</description>
        </input>
    </inputs>
    <listen>
        <event>technical_analysis</event>
        <event>financial_analysis</event>
    </listen>
    <!-- 仅当所有监听的事件完成时，此事件才会执行 -->
</event>
```

3. Evaluator-Optimizer Pattern (Iterative Refinement):
```xml
<event>
    <name>generate_content</name>
    <outputs>
        <output>
            <key>content</key>
            <description>生成的内容</description>
            <action>
                <type>RESULT</type>
            </action>
        </output>
    </outputs>
</event>

<event>
    <name>evaluate_content</name>
    <listen>
        <event>generate_content</event>
    </listen>
    <task>评估生成内容的质量</task>
    <outputs>
        <output>
            <key>approved</key>
            <description>内容符合质量标准</description>
            <condition>如果质量分数 >= 阈值</condition>
            <action>
                <type>RESULT</type>
            </action>
        </output>
        <output>
            <key>needs_improvement</key>
            <description>内容需要改进</description>
            <condition>如果质量分数 < 阈值</condition>
            <action>
                <type>GOTO</type>
                <value>generate_content</value>
            </action>
        </output>
    </outputs>
</event>
```

「关于流程模式的重要说明」：
0. 由于上下文长度的限制，上述模式并不完整，缺少一些必要的元素。在实际应用中，您可以参考这些模式的逻辑来创建完整且正确的流程。

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

用户：我想构建一个智能体协作工作流程，帮助我撰写一篇关于用户主题的类似维基百科的文章。它应该：
1. 在网上搜索用户主题。
2. 为用户主题撰写大纲。
3. 评估大纲。如果大纲不够好，重复大纲步骤，否则继续撰写文章。
4. 撰写文章。

流程xml应为：
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
            <description>此代理用于在网上搜索用户主题。</description>
        </agent>
        <agent category="new">
            <name>Outline Agent</name>
            <description>此代理用于为用户主题撰写大纲。</description>
        </agent>
        <agent category="new">
            <name>Evaluator Agent</name>
            <description>此代理用于评估用户主题的大纲。</description>
        </agent>
        <agent category="new">
            <name>Article Writer Agent</name>
            <description>此代理用于撰写用户主题的文章。</description>
        </agent>
    </agents>

    <events>
        <event>
            <name>on_start</name>
            <inputs>
                <input>
                    <key>user_topic</key>
                    <description>用户想要撰写的类似维基百科文章的主题。</description>
                </input>
            </inputs>
            <outputs>
                <output>
                    <key>user_topic</key>
                    <description>用户想要撰写的类似维基百科文章的主题。</description>
                    <action>
                        <type>RESULT</type>
                    </action>
                </output>
            </outputs>
        </event>
        <event>
            <name>on_search</name>
            <inputs>
                <input>
                    <key>user_topic</key>
                    <description>用户想要撰写的类似维基百科文章的主题。</description>
                </input>
            </inputs>
            <task>
                搜索有关主题的信息并返回结果。
            </task>
            <outputs>
                <output>
                    <key>search_result</key>
                    <description>用户主题的搜索结果。</description>
                    <action>
                        <type>RESULT</type>
                    </action>
                </output>
            </outputs>
            <listen>
                <event>on_start</event>
            </listen>
            <agent>
                <name>Web Surfer Agent</name>
                <model>openai/qwen-plus</model>
            </agent>
        </event>
        <event>
            <name>on_outline</name>
            <inputs>
                <input>
                    <key>search_result</key>
                    <description>用户主题的搜索结果。</description>
                </input>
            </inputs>
            <task>
                为用户主题撰写大纲。
            </task>
            <outputs>
                <output>
                    <key>outline</key>
                    <description>用户主题的大纲。</description>
                    <action>
                        <type>RESULT</type>
                    </action>
                </output>
            </outputs>
            <listen>
                <event>on_start</event>
            </listen>
            <agent>
                <name>Outline Agent</name>
                <model>openai/qwen-plus</model>
            </agent>
        </event>
        <event>
            <name>on_evaluate</name>
            <inputs>
                <input>
                    <key>outline</key>
                    <description>用户主题的大纲。</description>
                </input>
            </inputs>
            <task>
                评估用户主题的大纲。
            </task>
            <outputs>
                <output>
                    <key>positive_feedback</key>
                    <description>用户主题大纲的正面反馈。</description>
                    <condition>
                        如果大纲足够好，则给出正面反馈。
                    </condition>
                    <action>
                        <type>RESULT</type>
                    </action>
                </output>
                <output>
                    <key>negative_feedback</key>
                    <description>用户主题大纲的负面反馈。</description>
                    <condition>
                        如果大纲不够好，则给出负面反馈。
                    </condition>
                    <action>
                        <type>GOTO</type>
                        <value>on_outline</value>
                    </action>
                </output>
            </outputs>
            <listen>
                <event>on_outline</event>
            </listen>
            <agent>
                <name>Evaluator Agent</name>
                <model>openai/qwen-plus</model>
            </agent>
        </event>
        <event>
            <name>on_write</name>
            <inputs>
                <input>
                    <key>outline</key>
                    <description>用户主题的大纲。</description>
                </input>
            </inputs>
            <task>
                撰写用户主题的文章。
            </task>
            <outputs>
                <output>
                    <key>article</key>
                    <description>用户主题的文章。</description>
                    <action>
                        <type>RESULT</type>
                    </action>
                </output>
            </outputs>
            <listen>
                <event>on_evaluate</event>
            </listen>
            <agent>
                <name>Article Writer Agent</name>
                <model>openai/qwen-plus</model>
            </agent>
        </event>
    </events>
</workflow>

指导原则：
1. 每个事件应有明确的输入和输出。
2. 使用条件处理不同结果。
3. 使用 <listen> 元素正确链接事件。
4. 包含审核步骤以进行质量控制。
5. 行为类型应为 RESULT 或 ABORT。

根据示例和指导原则，根据用户需求创建适当的流程xml。
"""
    return Agent(
        name = "Workflow Former Agent",
        model = model,
        instructions = instructions,
    )

if __name__ == "__main__":
    from autoagent import MetaChain
    agent = get_workflow_former_agent("openai/qwen-plus")
    client = MetaChain()
#     task_yaml = """\
# I want to create a workflow that can help me to solving the math problem.

# The workflow should:
# 2. Parallelize solving the math problem with the same `Math Solver Agent` using different language models (`gpt-4o-2024-08-06`, `openai/qwen-plus`, `deepseek/deepseek-chat`)
# 3. Aggregate the results from the `Math Solver Agent` and return the final result using majority voting.

# Please create the form of this workflow in the XML format.
# """
    task_yaml = """\
I want to create a workflow that can help me to solving the math problem.

The workflow should:
1. The `Objective Extraction Agent` will extract the objective of the math problem.
2. The `Condition Extraction Agent` will extract the conditions of the math problem.
3. The `Math Solver Agent` will evaluate whether the conditions are enough to solve the math problem: if yes, solve the math problem; if no, return to the `Condition Extraction Agent` to extract more conditions.

Please create the form of this workflow in the XML format.
"""
    task_yaml = task_yaml + """\
Directly output the form in the XML format.
"""
    messages = [{"role": "user", "content": task_yaml}]
    response = client.run(agent, messages)
    print(response.messages[-1]["content"])