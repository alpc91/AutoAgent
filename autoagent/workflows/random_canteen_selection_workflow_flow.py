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

from autoagent.agents import get_coding_agent

from autoagent.agents import get_vote_aggregator_agent
@default_drive.make_event
async def on_start(event: EventInput, global_ctx):
    print("start the workflow:" + 'random_canteen_selection_workflow')
@default_drive.listen_group([on_start])
async def generate_scores_canteen_a(event: EventInput, global_ctx):
    inputs = [{'key': 'canteen_names', 'description': '需要评估的食堂名称列表，例如["A食堂", "B食堂", "C食堂"]。'}]
    input_dict = dict()
    for inp in inputs: 
        input_dict[inp["key"]] = global_ctx.get(inp["key"], None)
    
    messages = global_ctx.get('messages', [])
    task = '为第一个食堂生成一个随机评分。'
    outputs = [{'key': 'score_canteen_a', 'description': 'A食堂的随机评分（0-10分）。', 'condition': None, 'action': {'type': 'RESULT', 'value': None}}]
    agent = get_coding_agent('openai/qwen-plus')
    

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
@default_drive.listen_group([on_start])
async def generate_scores_canteen_b(event: EventInput, global_ctx):
    inputs = [{'key': 'canteen_names', 'description': '需要评估的食堂名称列表，例如["A食堂", "B食堂", "C食堂"]。'}]
    input_dict = dict()
    for inp in inputs: 
        input_dict[inp["key"]] = global_ctx.get(inp["key"], None)
    
    messages = global_ctx.get('messages', [])
    task = '为第二个食堂生成一个随机评分。'
    outputs = [{'key': 'score_canteen_b', 'description': 'B食堂的随机评分（0-10分）。', 'condition': None, 'action': {'type': 'RESULT', 'value': None}}]
    agent = get_coding_agent('openai/qwen-plus')
    

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
@default_drive.listen_group([on_start])
async def generate_scores_canteen_c(event: EventInput, global_ctx):
    inputs = [{'key': 'canteen_names', 'description': '需要评估的食堂名称列表，例如["A食堂", "B食堂", "C食堂"]。'}]
    input_dict = dict()
    for inp in inputs: 
        input_dict[inp["key"]] = global_ctx.get(inp["key"], None)
    
    messages = global_ctx.get('messages', [])
    task = '为第三个食堂生成一个随机评分。'
    outputs = [{'key': 'score_canteen_c', 'description': 'C食堂的随机评分（0-10分）。', 'condition': None, 'action': {'type': 'RESULT', 'value': None}}]
    agent = get_coding_agent('openai/qwen-plus')
    

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
@default_drive.listen_group([generate_scores_canteen_a, generate_scores_canteen_b, generate_scores_canteen_c])
async def aggregate_scores(event: EventInput, global_ctx):
    inputs = [{'key': 'score_canteen_a', 'description': 'A食堂的随机评分（0-10分）。'}, {'key': 'score_canteen_b', 'description': 'B食堂的随机评分（0-10分）。'}, {'key': 'score_canteen_c', 'description': 'C食堂的随机评分（0-10分）。'}]
    input_dict = dict()
    for inp in inputs: 
        input_dict[inp["key"]] = global_ctx.get(inp["key"], None)
    
    messages = global_ctx.get('messages', [])
    task = '聚合所有食堂的评分并选出得分最高的食堂。'
    outputs = [{'key': 'selected_canteen', 'description': '最终被选中的食堂名称。', 'condition': None, 'action': {'type': 'RESULT', 'value': None}}]
    agent = get_vote_aggregator_agent('openai/qwen-plus')
    

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

@register_workflow(name = 'random_canteen_selection_workflow')
async def random_canteen_selection_workflow(system_input: str):
    storage_results = dict(canteen_names = system_input)
    await default_drive.invoke_event(
        on_start,
        global_ctx=storage_results,
    )
    system_output = storage_results.get('selected_canteen', None)
    return system_output
