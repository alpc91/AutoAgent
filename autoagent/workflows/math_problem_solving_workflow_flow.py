import asyncio
import json
import argparse
from openai import AsyncOpenAI
from openai.types.chat import ChatCompletionMessageToolCall
from autoagent.flow import default_drive, EventInput, ReturnBehavior
from autoagent.flow.dynamic import goto_events, abort_this
import re
from autoagent import MetaChain
from autoagent.types import Response
from autoagent.registry import register_workflow

def extract_answer(response: str, key: str):
    pattern = f"<{key}>(.*?)</{key}>"
    matches = re.findall(pattern, response, re.DOTALL)
    return matches[0] if len(matches) > 0 else None

from autoagent.agents import get_math_solver_agent

from autoagent.agents import get_coding_agent

from autoagent.agents import get_vote_aggregator_agent
@default_drive.make_event
async def on_start(event: EventInput, global_ctx):
    print("start the workflow:" + 'math_problem_solving_workflow')
@default_drive.listen_group([on_start])
async def solve_math_problem(event: EventInput, global_ctx):
    inputs = [{'key': 'math_problem', 'description': '用户提供的数学问题描述。'}]
    input_dict = dict()
    for inp in inputs: 
        input_dict[inp["key"]] = global_ctx.get(inp["key"], None)
    
    messages = global_ctx.get('messages', [])
    task = '使用 Math Solver Agent 提供多种解决方案。'
    outputs = [{'key': 'solutions', 'description': '由 Math Solver Agent 生成的多个解决方案。', 'condition': None, 'action': {'type': 'RESULT', 'value': None}}]
    agent = get_math_solver_agent('hosted_vllm/Qwen/QwQ-32B-AWQ')
    

    input_str = []
    for key, value in input_dict.items():
        input_str.append(f"The {key.replace('_', ' ')} is {value}")
    input_str = "\n".join(input_str) + "\n"
    query = input_str + '.\nThe task is: ' + task + '.\n'
    messages.append({
        "role": "user",
        "content": query
    })
    client = MetaChain()
    response: Response = await client.run_async(agent = agent, messages = messages, context_variables = global_ctx, debug = True)
    result = response.messages[-1]["content"]
    messages.extend(response.messages)
    global_ctx["messages"] = messages

    for output in outputs:
        ans = extract_answer(result, output["key"])
        if ans:
            if output["action"]["type"] == "RESULT":
                global_ctx[output["key"]] = ans
                return ans
            elif output["action"]["type"] == "ABORT":
                return abort_this()
            elif output["action"]["type"] == "GO_TO":
                return goto_events([output["action"]["value"]])
        elif len(outputs) == 1: 
            global_ctx[output["key"]] = result
            return result
    raise Exception("No valid answer found")
@default_drive.listen_group([solve_math_problem])
async def verify_solutions_with_code(event: EventInput, global_ctx):
    inputs = [{'key': 'solutions', 'description': '由 Math Solver Agent 生成的多个解决方案。'}]
    input_dict = dict()
    for inp in inputs: 
        input_dict[inp["key"]] = global_ctx.get(inp["key"], None)
    
    messages = global_ctx.get('messages', [])
    task = '使用 Coding Agent 编写代码以验证解决方案的有效性。'
    outputs = [{'key': 'verified_solutions', 'description': '经过 Coding Agent 验证后的有效解决方案。', 'condition': None, 'action': {'type': 'RESULT', 'value': None}}]
    agent = get_coding_agent('hosted_vllm/Qwen/QwQ-32B-AWQ')
    

    input_str = []
    for key, value in input_dict.items():
        input_str.append(f"The {key.replace('_', ' ')} is {value}")
    input_str = "\n".join(input_str) + "\n"
    query = input_str + '.\nThe task is: ' + task + '.\n'
    messages.append({
        "role": "user",
        "content": query
    })
    client = MetaChain()
    response: Response = await client.run_async(agent = agent, messages = messages, context_variables = global_ctx, debug = True)
    result = response.messages[-1]["content"]
    messages.extend(response.messages)
    global_ctx["messages"] = messages

    for output in outputs:
        ans = extract_answer(result, output["key"])
        if ans:
            if output["action"]["type"] == "RESULT":
                global_ctx[output["key"]] = ans
                return ans
            elif output["action"]["type"] == "ABORT":
                return abort_this()
            elif output["action"]["type"] == "GO_TO":
                return goto_events([output["action"]["value"]])
        elif len(outputs) == 1: 
            global_ctx[output["key"]] = result
            return result
    raise Exception("No valid answer found")
@default_drive.listen_group([verify_solutions_with_code])
async def aggregate_and_determine_final_answer(event: EventInput, global_ctx):
    inputs = [{'key': 'verified_solutions', 'description': '经过 Coding Agent 验证后的有效解决方案。'}]
    input_dict = dict()
    for inp in inputs: 
        input_dict[inp["key"]] = global_ctx.get(inp["key"], None)
    
    messages = global_ctx.get('messages', [])
    task = '使用 Vote Aggregator Agent 聚合所有解决方案并选择最终答案。'
    outputs = [{'key': 'final_answer', 'description': '最终确定的数学问题答案。', 'condition': None, 'action': {'type': 'RESULT', 'value': None}}]
    agent = get_vote_aggregator_agent('hosted_vllm/Qwen/QwQ-32B-AWQ')
    

    input_str = []
    for key, value in input_dict.items():
        input_str.append(f"The {key.replace('_', ' ')} is {value}")
    input_str = "\n".join(input_str) + "\n"
    query = input_str + '.\nThe task is: ' + task + '.\n'
    messages.append({
        "role": "user",
        "content": query
    })
    client = MetaChain()
    response: Response = await client.run_async(agent = agent, messages = messages, context_variables = global_ctx, debug = True)
    result = response.messages[-1]["content"]
    messages.extend(response.messages)
    global_ctx["messages"] = messages

    for output in outputs:
        ans = extract_answer(result, output["key"])
        if ans:
            if output["action"]["type"] == "RESULT":
                global_ctx[output["key"]] = ans
                return ans
            elif output["action"]["type"] == "ABORT":
                return abort_this()
            elif output["action"]["type"] == "GO_TO":
                return goto_events([output["action"]["value"]])
        elif len(outputs) == 1: 
            global_ctx[output["key"]] = result
            return result
    raise Exception("No valid answer found")

@register_workflow(name = 'math_problem_solving_workflow')
async def math_problem_solving_workflow(system_input: str):
    storage_results = dict(math_problem = system_input)
    await default_drive.invoke_event(
        on_start,
        global_ctx=storage_results,
    )
    system_output = storage_results.get('final_answer', None)
    return system_output
