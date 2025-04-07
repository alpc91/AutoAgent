from autoagent import MetaChain
from autoagent.util import ask_text, single_select_menu, print_markdown, debug_print, UserCompleter
from prompt_toolkit import PromptSession
from prompt_toolkit.formatted_text import HTML
from prompt_toolkit.styles import Style
from autoagent.logger import LoggerManager, MetaChainLogger 
from rich.console import Console
from rich.panel import Panel
from autoagent.agents.meta_agent.workflow_generator import get_workflow_generator_agent
from autoagent.agents.meta_agent.workflow_former import get_workflow_former_agent
from autoagent.agents.meta_agent.workflow_creator import get_workflow_creator_agent
import re
from autoagent.agents.meta_agent.worklow_form_complie import parse_workflow_form, WorkflowForm
from autoagent.types import Result
from autoagent.memory.rag_zh_memory import RAGPipeline
import math
import os
from typing import Union
from autoagent.environment.docker_env import DockerEnv
from autoagent.environment.local_env import LocalEnv
from autoagent.environment.markdown_browser.mdconvert import MarkdownConverter
import zipfile

import sys, json
import asyncio, time
from loguru import logger
from typing import List, Dict
# from ultrarag.modules.llm import BaseLLM, OpenaiLLM
# from ultrarag.modules.router import BaseRouter
from ultrarag.modules.embedding import EmbClient
from ultrarag.modules.database import BaseIndex, QdrantIndex
from ultrarag.modules.reranker import BaseRerank, RerankerClient
from ultrarag.modules.knowledge_managment.knowledge_managment import QdrantIndexSearchWarper
from ultrarag.common.utils import format_view, GENERATE_PROMPTS
from ultrarag.modules.embedding import BaseEmbedding
from ultrarag.modules.knowledge_managment import Knowledge_Managment
import hashlib
from ultrarag.modules.embedding import EmbeddingClient, load_model, OpenAIEmbedding
# from ultrarag.modules.llm import OpenaiLLM, HuggingfaceClient, HuggingFaceServer, VllmServer
from ultrarag.modules.reranker import RerankerClient, RerankerServer
from ultrarag.modules.knowledge_managment.doc_index import text_index

import json

def workflow_generating(workflow_generator, client, messages, context_variables, requirements, debug):
    messages.append({"role": "user", "content": requirements})
    response = client.run(workflow_generator, messages, context_variables, debug=debug)
    workflow = response.messages[-1]["content"]
    if "reasoning_content" in response.messages[-1] or (hasattr(response.messages[-1], 'reasoning_content') and response.messages[-1].reasoning_content):
        reasoning_content = response.messages[-1]["reasoning_content"]
    else:
        reasoning_content = "No reasoning content available"
    messages.extend(response.messages)

    return reasoning_content, workflow, messages


def parse_json_form(json_str: str) -> str:
    """
    读取并解析workflow form json文件
    
    Args:
        json_content: json文件内容
    
    Returns:
        解析后的json对象，如果解析失败返回None
    """
    if not isinstance(json_str, str):
        return "Invalid input: json_str should be a string"
    try:
        return json.loads(json_str)
    except json.JSONDecodeError as e:
        error_msg = (
            f"JSON解析错误: {e.msg} "
            f"(行号: {e.lineno}, 位置: {e.pos})"
        )
        return  error_msg
    


def workflow_profiling(workflow_former, client, messages, context_variables, debug):
    messages.append({"role": "user", "content": """
Directly output the form in the json format without ANY other text.
"""})
    response = client.run(workflow_former, messages, context_variables, debug=debug)
    output_json_form = response.messages[-1]["content"]
    messages.extend(response.messages)

    MAX_RETRY = 3
    for i in range(MAX_RETRY):
        workflow_form = parse_json_form(output_json_form)
        if isinstance(workflow_form, dict):
            # 如果成功解析json为workflow form，则输出
            with open("workflow_form.json", "w") as f:
                f.write(output_json_form)
            break
        elif isinstance(workflow_form, str):
            print(f"Error parsing json to workflow form: {workflow_form}. Retry {i+1}/{MAX_RETRY}")
            messages.append({"role": "user", "content": f"Error parsing json to workflow form, the error message is: {workflow_form}\nNote that there are some special restrictions for creating workflow form, please try again."})
            response = client.run(workflow_former, messages, context_variables, debug=debug)
            output_json_form = response.messages[-1]["content"]
            messages.extend(response.messages)
        else:
            raise ValueError(f"Unexpected error: {workflow_form}")
    return workflow_form, output_json_form, messages

def workflow_editing(workflow_creator_agent, client, messages, context_variables, workflow_form, output_json_form, requirements, task, debug, suggestions = ""):
    MAX_RETRY = 3
    if suggestions != "":
        suggestions = "[IMPORTANT] Here are some suggestions for creating the workflow: " + suggestions
    agents = workflow_form.agents
    new_agents = []
    for agent in agents:
        if agent.category == "new":
            new_agents.append(agent)

    if len(new_agents) != 0:
        new_agent_str = "AGENT CREATION INSTRUCTIONS:\nBefore you create the workflow, you need to create the following new agents in the workflow:\n"
        for agent in new_agents:
            new_agent_str += f"Agent name: {agent.name}\nAgent description: {agent.description}\n"
            new_agent_str += f"Agent tools: {agent.tools}\n" if agent.tools else "Agent tools: []\n"
    else: 
        new_agent_str = ""

    def case_resolved(task_response: str, context_variables: dict): 
        """
        Use this tools when the desired workflow is created and tested successfully. You can NOT use this tool if the workflow is not created or tested successfully by running the workflow.
        """
        return f"Case resolved. The desired workflow is created and tested successfully.    : {task_response}"
    def case_not_resolved(task_response: str, context_variables: dict):
        """
        Use this tools when you encounter irresistible errors after trying your best with multiple attempts for creating the desired workflow. You can NOT use this tool before you have tried your best.
        """
        return f"Case not resolved. The desired workflow is not created or tested successfully. Details: {task_response}"
    workflow_creator_agent.functions.extend([case_resolved, case_not_resolved])

    messages.append({"role": "user", "content": f"""\
WORKFLOW CREATION INSTRUCTIONS:
The user's request to create workflow is: {requirements}
Given the completed workflow form with XML format: {output_json_form}

TASK: 
Your task is to create the workflow for me, and then test the workflow by running the workflow using `run_workflow` tool to complete the user's task: 
{task}

{new_agent_str}

TERMINATION INSTRUCTIONS:
After you have created the workflow and tested it successfully, you can use the `case_resolved` tool to indicate the case is resolved, otherwise you should try your best to create the workflow. And ONLY after you have tried multiple times, you can use the `case_not_resolved` tool to indicate the case is not resolved and give the reason.

Remember: you can NOT stop util you have created the workflow and tested it successfully.
{suggestions}
"""})
    response = client.run(workflow_creator_agent, messages, context_variables, debug=debug)
    content = response.messages[-1]["content"]
    # if "</think>" in content:
    #     content = content.split("</think>", 1)[1].lstrip()
    for i in range(MAX_RETRY):
        if content.startswith("Case resolved"):
            return content, messages
        messages.append({"role": "user", "content": f"""\
WORKFLOW CREATION INSTRUCTIONS:
The user's request to create workflow is: {requirements}
Given the completed workflow form with XML format: {output_json_form}

TASK: 
Your task is to create the workflow for me, and then test the workflow by running the workflow using `run_workflow` tool to complete the user's task: 
{task}

{new_agent_str}

TERMINATION INSTRUCTIONS:
After you have created the workflow and tested it successfully, you can use the `case_resolved` tool to indicate the case is resolved, otherwise you should try your best to create the workflow. And ONLY after you have tried multiple times, you can use the `case_not_resolved` tool to indicate the case is not resolved and give the reason.

Remember: you can NOT stop util you have created the workflow and tested it successfully.

FEEDBACK:
The last attempt failed with the following error: {content}, please try again to create the desired workflow.
{suggestions}
"""})
        response = client.run(workflow_creator_agent, messages, context_variables, debug=debug)
        content = response.messages[-1]["content"]
    if i == MAX_RETRY:
        return f"The desired workflow is not created or tested successfully with {MAX_RETRY} attempts.", messages

def generate_kb_config_id(embedding_model_name):
    """
    Generate a unique kb_config_id based on the embedding model name.
    
    Args:
        embedding_model_name: Name of the embedding model
    Returns:
        str: MD5 hash of the configuration string
    """
    config_str = f"{embedding_model_name}"
    return hashlib.md5(config_str.encode()).hexdigest()

def generate_knowledge_base_id(kb_name, kb_config_id, file_list, chunk_size, overlap, others):
    """
    Generate a unique knowledge_base_id based on multiple parameters.
    
    Args:
        kb_name: Name of the knowledge base
        kb_config_id: Configuration ID
        file_list: List of files
        chunk_size: Size of chunks
        overlap: Overlap size
        others: Additional parameters
    Returns:
        str: MD5 hash of the combined parameters
    """
    combined_str = f"{kb_name}-{kb_config_id}-{file_list}-{chunk_size}-{overlap}-{others}"
    return hashlib.md5(combined_str.encode()).hexdigest()

def meta_workflow(model: str, context_variables: dict, debug: bool = True):
    print('\033[s\033[?25l', end='')  # Save cursor position and hide cursor
    logger = LoggerManager.get_logger()
    workflow_generator = get_workflow_generator_agent("openai/qwen-plus")
    workflow_former = get_workflow_former_agent("openai/qwen-plus")
    workflow_creator_agent = get_workflow_creator_agent("openai/qwen-plus")
    # workflow_generator = get_workflow_generator_agent("hosted_vllm/Qwen/QwQ-32B-AWQ")
    # workflow_former = get_workflow_former_agent("hosted_vllm/Qwen/QwQ-32B-AWQ")
    # workflow_creator_agent = get_workflow_creator_agent("hosted_vllm/Qwen/QwQ-32B-AWQ")
    # workflow_former = get_workflow_former_agent("hosted_vllm/Qwen/Qwen-32B-Instruct-AWQ")
    # workflow_creator_agent = get_workflow_creator_agent("hosted_vllm/Qwen/Qwen-32B-Instruct-AWQ")

    path_files_csv = "./rag_db/manage_table/file_manager.csv"
    path_kb_csv = "./rag_db/manage_table/knowledge_base_manager.csv"
    path_files_dir = "./rag_db/files"
    path_kb_dir = "./rag_db/kb"

    # 初始化流水线
    embedding_model_name = "OpenBMB/MiniCPM-Embedding-Light"
    chunk_size = 512
    overlap = 10
    embedding_model_path = "/home/crf/workspace/UltraRAG/resource/models/minicpm-embedding-light"
    embedding = load_model(embedding_model_path, "cuda")


    reranker_model_path = "/home/crf/workspace/UltraRAG/resource/models/minicpm-reranker-light"
    reranker = RerankerServer(model_path=reranker_model_path, device="cuda")

    
    kb_config_id = generate_kb_config_id(embedding_model_name)
    qdrant_dir = f"./rag_db_qdrant"

    os.makedirs("./rag_db", exist_ok=True)
    os.makedirs(qdrant_dir, exist_ok=True)

    # 检查并删除 .lock 文件（todo）
    lock_file_path = os.path.join(qdrant_dir, '.lock')
    if os.path.exists(lock_file_path):
        logger.info(f"Removing .lock file at: {lock_file_path}")
        os.remove(lock_file_path)
    
    qdrant_index = QdrantIndex(url=qdrant_dir, encoder=embedding)

    kb_name = "base_info"
    file_list = ["./rag_docs/base_info.txt", "./rag_docs/history.txt", "./rag_docs/trick.txt"]
    kb_id = generate_knowledge_base_id(kb_name, kb_config_id, file_list, chunk_size, overlap, None)
    kb_path = f"./rag_db/{kb_id}.jsonl"
    kb_df = None



    kb_df = asyncio.run(Knowledge_Managment.index(qdrant_index,kb_config_id,kb_name,embedding_model_name,embedding_model_path,qdrant_dir,kb_path,kb_id,file_list,embedding,chunk_size,overlap,None,kb_df))
    os.makedirs(os.path.dirname(path_kb_csv), exist_ok=True)
    kb_df.to_csv(path_kb_csv, index=False)


    searcher = Knowledge_Managment.get_searcher(
                embedding_model=embedding,
                knowledge_id=[kb_id],
                knowledge_stat_tab_path=path_kb_csv
            )
    query = "从上下文信息中进行学习"
    recalls = asyncio.run(searcher.search(query=query, topn=2))
    content = "\n".join([item.content for item in recalls])
    print(content)
    # scores, reranks = asyncio.run(reranker.rerank(query=query, nodes=recalls, func=lambda x: x.content))
    # reranks = reranks[:5]



    # asyncio.run(text_index(
    #     qdrant_index=qdrant_index,
    #     knowledge_id=kb_id,
    #     text="李白是中国唐代著名的诗人，他的诗歌以豪放、奔放著称，尤其是《将进酒》一诗，表达了他对人生的热爱和对自由的向往。",
    #     chunk_size=chunk_size,
    #     chunk_overlap=overlap,
    #     text_chunks_save_path=kb_path
    # ))

    # searcher = Knowledge_Managment.get_searcher(
    #             embedding_model=embedding,
    #             knowledge_id=[kb_id],
    #             knowledge_stat_tab_path=path_kb_csv
    #         )
    # query = "从上下文信息中进行学习"
    # recalls = asyncio.run(searcher.search(query="李白是谁？", topn=5))
    # # scores, reranks = asyncio.run(reranker.rerank(query=query, nodes=recalls, func=lambda x: x.content))
    # # reranks = reranks[:5]

    # content = "\n".join([item.content for item in recalls])
    # print(content)





    # rag = RAGPipeline("./rag_db")

    # # _index = QdrantIndex(database_url, encoder=EmbClient(url_or_path=embedding_url))
    # # _rerank = RerankerClient(url=reranker_url)
    
    # # 处理文档（示例路径）
    # print(rag.process_input(
    #     input_path="./rag_docs/base_info.txt",
    #     collection_name="base_info",
    #     overwrite=True
    # ))

    # print(rag.process_input(
    #     input_path="./rag_docs/history.txt",
    #     collection_name="history",
    #     overwrite=True
    # ))

    # print(rag.process_input(
    #     input_path="./rag_docs/trick.txt",
    #     collection_name="trick",
    #     overwrite=True
    # ))
    
    # # 执行查询
    # question = "数据库说了啥？"
    # results = rag.query(question, "base_info", top_k=3)
    
    # print("\n检索结果：")
    # for doc, score in zip(results['documents'], results['scores']):
    #     print(f"[相似度：{score:.2f}] {doc}...")

    agent = workflow_generator
    agents = {workflow_generator.name.replace(' ', '_'): workflow_generator, workflow_former.name.replace(' ', '_'): workflow_former, workflow_creator_agent.name.replace(' ', '_'): workflow_creator_agent}
    style = Style.from_dict({
        'bottom-toolbar': 'bg:#333333 #ffffff',
    })
    # 创建会话
    session = PromptSession(
        completer=UserCompleter(agents.keys()),
        complete_while_typing=True,
        style=style
    )

    client = MetaChain(log_path=logger)
    console = Console()
    messages = []

    stage = 0
    sys_messages = ["现在是状态确定阶段。", "现在是目标分析阶段。", "现在是任务分配阶段。", "现在是方案计划阶段。"]
    # print(sys_messages[stage % 4])
    searcher = Knowledge_Managment.get_searcher(
            embedding_model=embedding,
            knowledge_id=[kb_id],
            knowledge_stat_tab_path=path_kb_csv
        )
    query = sys_messages[stage % 4]
    recalls = asyncio.run(searcher.search(query=query, topn=2))
    rag_content = "\n".join([item.content for item in recalls])
    print(rag_content)

    last_message = sys_messages[stage % 4]+"请告诉我您对创建MCT节点实例还有什么具体需求？"#请告诉我您想要创建什么实例（选择哪些智能代理，形成什么工作流）？"#"Tell me what do you want to create with `Workflow Chain`?"
    workflow = None
    workflow_form = None
    while True:
        query = session.prompt(
            f'{last_message} (type "exit" to quit, press "Enter" to continue): ',
            # bottom_toolbar=HTML('<b>Prompt:</b> Enter <b>@</b> to mention Agents'), 
        )
        if query.strip().lower() == 'exit':
            logo_text = "Workflow Chain completed. See you next time! :waving_hand:"
            console.print(Panel(logo_text, style="bold salmon1", expand=True))
            break
            

        if query=="" and workflow_form:
            # 将当前阶段信息和工作流添加到历史记录文件中
            with open("./rag_docs/history.txt", "a", encoding="utf-8") as history_file:
                history_file.write("\n\n" + sys_messages[stage % 4]+"\n该阶段的协作流程如下：\n"+workflow)
            
            # 更新RAG数据库
            # print(rag.add_text(sys_messages[stage % 4]+"\n该阶段的协作流程如下：\n"+workflow, "history"))
            asyncio.run(text_index(
                qdrant_index=qdrant_index,
                knowledge_id=kb_id,
                text=sys_messages[stage % 4]+"\n该阶段的协作流程如下：\n"+workflow,
                chunk_size=chunk_size,
                chunk_overlap=overlap,
                text_chunks_save_path=kb_path
            ))

            agent = workflow_generator
            stage += 1
            messages = []

            searcher = Knowledge_Managment.get_searcher(
                    embedding_model=embedding,
                    knowledge_id=[kb_id],
                    knowledge_stat_tab_path=path_kb_csv
                )
            query = sys_messages[stage % 4]
            recalls = asyncio.run(searcher.search(query=query, topn=2))
            rag_content = "\n".join([item.content for item in recalls])
            print(rag_content)

            last_message = sys_messages[stage % 4]+"请告诉我您对创建MCT节点实例还有什么具体需求？"
            workflow = None
            workflow_form = None
            continue

        # words = query.split()
        console.print(f"[bold green]Your request: {sys_messages[stage % 4]+query}[/bold green]", end=" ")
        # for word in words:
        #     if word.startswith('@') and word[1:] in agents.keys():
        #         # print(f"[bold magenta]{word}[bold magenta]", end=' ') 
        #         agent = agents[word.replace('@', '')]
        #     else:
        #         # print(word, end=' ')
        #         pass
        print()
        agent_name = agent.name
        console.print(f"[bold green][bold magenta]@{agent_name}[/bold magenta] will help you, be patient...[/bold green]")
        match agent_name:
            case "Workflow Generator Agent":
                # if query == "":
                #     console.print(f"[bold red]必须输入实例要求。[/bold red]")#f"[bold red]There MUST be a request to create the agent form.[/bold red]")
                #     continue
                if workflow_form:
                    requirements = query
                else:
                    requirements = '这是向量数据库中检索出来的相关信息：\n'+rag_content+'\n\n这是当前的阶段和需求：'+sys_messages[stage % 4]+'\n'+query
                
                # print(f"实例要求:\n {requirements}\n\n")

                reasoning_content, workflow, messages = workflow_generating(workflow_generator, client, messages, context_variables, requirements, debug)
                # workflow = "这是一个节点实例的语言描述"
                agent = workflow_former
                console.print(f"[bold green][bold magenta]@{agent_name}[/bold magenta] 思维链:\n[/bold green][bold blue]{reasoning_content}[/bold blue]")
                console.print(f"[bold green][bold magenta]@{agent_name}[/bold magenta] 生成的MCT节点实例语言描述:\n[/bold green][bold blue]{workflow}[/bold blue]")

                workflow_form, output_json_form, messages = workflow_profiling(workflow_former, client, messages, context_variables, debug)

                if workflow_form is None:
                    console.print(f"[bold red][bold magenta]@{agent_name}[/bold magenta] json文件生成失败, 请给出修改建议.[/bold red]")
                    last_message = "请提出具体修改建议或告诉我您想要创建MCT节点实例的需求是什么？"
                    # console.print(f"[bold red][bold magenta]@{agent_name}[/bold magenta] has not created workflow form successfully, please modify your requirements again.[/bold red]")
                    # last_message = "Tell me what do you want to create with `Workflow Chain`?"
                    continue
                agent = workflow_generator 
                context_variables["workflow_form"] = workflow_form

                console.print(f"[bold green][bold magenta]@{agent_name}[/bold magenta] 生成的json为:\n[/bold green][bold blue]{output_json_form}[/bold blue]")
                last_message = '如果前端展示的工作流符合你的要求，请按"Enter"回车；否则，请提出具体修改建议。'#将为进行前端展示并开始生成协作工作流python脚本并驱动后端开始执行
                # console.print(f"[bold green][bold magenta]@{agent_name}[/bold magenta] has created workflow form successfully with the following details:\n[/bold green][bold blue]{output_json_form}[/bold blue]")
                # last_message = "It is time to create the desired workflow python code, do you have any suggestions for creating the workflow?"
            # case "Workflow Creator Agent":
            #     suggestions = query #进来实际为""
            #     # default_value= '该阶段的系统输入是XXX，请根据输入，使用 `run_workflow` tool来执行之前生成的协作工作流程以获取该阶段的系统输出'
            #     default_value = 'Come up with a task for the workflow to test your created workflow, and use `run_workflow` tool to test your created workflow.'  # 这里设置你想要的默认值 
            #     task = ""
            #     # session.prompt(
            #     # 'It is time to create the desired workflow, what task do you want to complete with the workflow? (Press Enter if none): ',
            #     # )
            #     task = default_value if not task.strip() else task
            #     agent_response, messages = workflow_editing(workflow_creator_agent, client, messages, context_variables, workflow_form, output_json_form, requirements, task, debug, suggestions)
            #     if agent_response.startswith("Case not resolved"):
            #         # console.print(f"[bold red][bold magenta]@{agent_name}[/bold magenta] has not created workflow successfully with the following error: {agent_response}[/bold red]")
            #         console.print(f"[bold red][bold magenta]@{agent_name}[/bold magenta] 驱动后台执行失败，原因如下: {agent_response}[/bold red]")
            #         agent = workflow_creator_agent
            #     else:
            #         # console.print(f"[bold green][bold magenta]@{agent_name}[/bold magenta] has created workflow successfully with the following details:\n[/bold green][bold blue]{agent_response}[/bold blue]")
            #         # last_message = "Tell me what do you want to create with `Workflow Chain` next?"
            #         console.print(f"[bold green][bold magenta]@{agent_name}[/bold magenta] 已经驱动后台执行:\n[/bold green][bold blue]{agent_response}[/bold blue]")
            #         last_message = "请输入exit退出"
    
    
    