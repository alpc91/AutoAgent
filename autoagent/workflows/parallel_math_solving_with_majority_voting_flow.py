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
    print("start the workflow:" + 'parallel_math_solving_with_majority_voting')
@default_drive.listen_group([on_start])
async def solve_with_math_solver(event: EventInput, global_ctx):
    inputs = [{'key': 'math_problem', 'description': 'The math problem that needs to be solved.'}]
    input_dict = dict()
    for inp in inputs: 
        input_dict[inp["key"]] = global_ctx.get(inp["key"], None)
    
    messages = global_ctx.get('messages', [])
    task = 'Solve the math problem using the Math Solver Agent.'
    outputs = [{'key': 'math_solution', 'description': 'The solution provided by the Math Solver Agent.', 'condition': None, 'action': {'type': 'RESULT', 'value': None}}]
    agent = get_math_solver_agent('openai/qwen-vl-plus')
    

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
async def solve_with_coding_agent(event: EventInput, global_ctx):
    inputs = [{'key': 'math_problem', 'description': 'The math problem that needs to be solved.'}]
    input_dict = dict()
    for inp in inputs: 
        input_dict[inp["key"]] = global_ctx.get(inp["key"], None)
    
    messages = global_ctx.get('messages', [])
    task = 'Solve the math problem using the Coding Agent.'
    outputs = [{'key': 'code_solution', 'description': 'The solution provided by the Coding Agent.', 'condition': None, 'action': {'type': 'RESULT', 'value': None}}]
    agent = get_coding_agent('openai/qwen-vl-plus')
    

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
@default_drive.listen_group([solve_with_math_solver, solve_with_coding_agent])
async def aggregate_results(event: EventInput, global_ctx):
    inputs = [{'key': 'math_solution', 'description': 'The solution provided by the Math Solver Agent.'}, {'key': 'code_solution', 'description': 'The solution provided by the Coding Agent.'}]
    input_dict = dict()
    for inp in inputs: 
        input_dict[inp["key"]] = global_ctx.get(inp["key"], None)
    
    messages = global_ctx.get('messages', [])
    task = 'Aggregate the results from the Math Solver Agent and the Coding Agent using majority voting.'
    outputs = [{'key': 'final_result', 'description': 'The final result of the math problem solving process.', 'condition': None, 'action': {'type': 'RESULT', 'value': None}}]
    agent = get_vote_aggregator_agent('openai/qwen-vl-plus')
    

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

@register_workflow(name = 'parallel_math_solving_with_majority_voting')
async def parallel_math_solving_with_majority_voting(system_input: str):
    storage_results = dict(math_problem = system_input)
    await default_drive.invoke_event(
        on_start,
        global_ctx=storage_results,
    )
    system_output = storage_results.get('final_result', None)
    return system_output
