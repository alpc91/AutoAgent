from autoagent import MetaChain
from autoagent.util import ask_text, single_select_menu, print_markdown, debug_print, UserCompleter
from prompt_toolkit.styles import Style
from autoagent.logger import LoggerManager, MetaChainLogger 
from rich.console import Console
from autoagent.agents.meta_agent.workflow_generator import get_workflow_generator_agent
from autoagent.agents.meta_agent.workflow_former import get_workflow_former_agent
from autoagent.agents.meta_agent.workflow_creator import get_workflow_creator_agent
from autoagent.agents.meta_agent.worklow_form_complie import parse_workflow_form, WorkflowForm
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
from ultrarag.modules.reranker import RerankerClient, RerankerServer, BCERerankServer
from ultrarag.modules.knowledge_managment.doc_index import text_index
import json

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

class Work:
    def __init__(self, context_variables: dict):
        self.context_variables = context_variables
        self.logger = LoggerManager.get_logger()
        self.workflow_generator = get_workflow_generator_agent("openai/qwen-plus")
        self.workflow_former = get_workflow_former_agent("openai/qwen-plus")
        self.workflow_creator_agent = get_workflow_creator_agent("openai/qwen-plus")

        self.path_kb_csv = "/home/crf/workspace/AutoAgent/rag_db/manage_table/knowledge_base_manager.csv"

        # 初始化流水线
        embedding_model_name = "OpenBMB/MiniCPM-Embedding-Light"
        self.chunk_size = 512
        self.overlap = 10
        embedding_model_path = "/home/crf/workspace/UltraRAG/resource/models/minicpm-embedding-light"
        self.embedding = load_model(embedding_model_path, "cuda")


        reranker_model_path = "/home/crf/workspace/UltraRAG/resource/models/minicpm-reranker-light"
        self.reranker = RerankerServer(model_path=reranker_model_path, device="cuda")

        
        kb_config_id = generate_kb_config_id(embedding_model_name)
        qdrant_dir = f"/home/crf/workspace/AutoAgent/rag_db_qdrant"

        os.makedirs("/home/crf/workspace/AutoAgent/rag_db", exist_ok=True)
        os.makedirs(qdrant_dir, exist_ok=True)

        # 检查并删除 .lock 文件（todo）
        lock_file_path = os.path.join(qdrant_dir, '.lock')
        if os.path.exists(lock_file_path):
            logger.info(f"Removing .lock file at: {lock_file_path}")
            os.remove(lock_file_path)
        
        self.qdrant_index = QdrantIndex(url=qdrant_dir, encoder=self.embedding)

        kb_name = "knowledge_base"
        file_list = ["/home/crf/workspace/AutoAgent/rag_docs/21-F-0520_JP_3-60_9-28-2018.pdf"]#"/home/crf/workspace/AutoAgent/rag_docs/base_info.txt", "/home/crf/workspace/AutoAgent/rag_docs/history.txt", "/home/crf/workspace/AutoAgent/rag_docs/trick.txt", 
        self.kb_id = generate_knowledge_base_id(kb_name, kb_config_id, file_list, self.chunk_size, self.overlap, None)
        self.kb_path = f"/home/crf/workspace/AutoAgent/rag_db/{self.kb_id}.jsonl"
        kb_df = None


        kb_df = asyncio.run(Knowledge_Managment.index(self.qdrant_index,kb_config_id,kb_name,embedding_model_name,embedding_model_path,qdrant_dir,self.kb_path,self.kb_id,file_list,self.embedding,self.chunk_size,self.overlap,None,kb_df))
        os.makedirs(os.path.dirname(self.path_kb_csv), exist_ok=True)
        kb_df.to_csv(self.path_kb_csv, index=False)

        # # 初始化流水线
        # self.rag = RAGPipeline("../rag_db")

        # # 处理文档（示例路径）
        # print(self.rag.process_input(
        #     input_path="../rag_docs/base_info.txt",
        #     collection_name="base_info",
        #     overwrite=True
        # ))

        # print(self.rag.process_input(
        #     input_path="../rag_docs/history.txt",
        #     collection_name="history",
        #     overwrite=True
        # ))

        # print(self.rag.process_input(
        #     input_path="../rag_docs/trick.txt",
        #     collection_name="trick",
        #     overwrite=True
        # ))

        self.agent = self.workflow_generator
        self.agents = {
            self.workflow_generator.name.replace(' ', '_'): self.workflow_generator, 
            self.workflow_former.name.replace(' ', '_'): self.workflow_former, 
            self.workflow_creator_agent.name.replace(' ', '_'): self.workflow_creator_agent
        }
        self.style = Style.from_dict({
            'bottom-toolbar': 'bg:#333333 #ffffff',
        })
        # 创建会话

        self.client = MetaChain(log_path=self.logger)
        self.console = Console()
        self.messages = []

        self.stage = 0
        self.sys_messages = ["状态确定阶段", "目标分析阶段", "任务分配阶段", "方案计划阶段"]
        searcher = Knowledge_Managment.get_searcher(
            embedding_model=self.embedding,
            knowledge_id=[self.kb_id],
            knowledge_stat_tab_path=self.path_kb_csv
        )
        recalls = asyncio.run(searcher.search(query=self.sys_messages[self.stage % 4], topn=25))
        scores, reranks = asyncio.run(self.reranker.rerank(query=self.sys_messages[self.stage % 4], nodes=recalls, func=lambda x: x.content))
        reranks = reranks[:5]

        self.rag_content = "\n".join([item.content for item in reranks])
        print(self.rag_content)

        self.last_message = self.sys_messages[self.stage % 4]+"。请告诉我您对创建MCT节点实例还有什么具体需求？"#请告诉我您想要创建什么实例（选择哪些智能代理，形成什么工作流）？"#"Tell me what do you want to create with `Workflow Chain`?"
        self.workflow = None
        self.workflow_form = None
        print("############### work init success")

    def query(self, message, callback, debug: bool = True):
        print("message",message)
        print("workflow_form",self.workflow_form)
        if message=="ok" and self.workflow_form:
            print("xxxxxxxxxxxxxx",message)
            # 将当前阶段信息和工作流添加到历史记录文件中
            with open("/home/crf/workspace/AutoAgent/rag_docs/history.txt", "a", encoding="utf-8") as history_file:
                history_file.write("\n\n** " + self.sys_messages[self.stage % 4] + "\n" + self.workflow)
            
            # 更新RAG数据库
            # print(self.rag.add_text(self.sys_messages[self.stage % 4]+"\n"+self.workflow, "history"))
            # asyncio.run(text_index(
            #     qdrant_index=self.qdrant_index,
            #     knowledge_id=self.kb_id,
            #     text="\n\n** "+self.sys_messages[self.stage % 4]+"\n\n** 该阶段的协作流程如下：\n"+self.workflow,
            #     chunk_size=self.chunk_size,
            #     chunk_overlap=self.overlap,
            #     text_chunks_save_path=self.kb_path
            # ))


            self.agent = self.workflow_generator
            self.stage += 1
            self.messages = []
            searcher = Knowledge_Managment.get_searcher(
                embedding_model=self.embedding,
                knowledge_id=[self.kb_id],
                knowledge_stat_tab_path=self.path_kb_csv
            )
            recalls = asyncio.run(searcher.search(query=self.sys_messages[self.stage % 4], topn=25))
            scores, reranks = asyncio.run(self.reranker.rerank(query=self.sys_messages[self.stage % 4], nodes=recalls, func=lambda x: x.content))
            reranks = reranks[:5]

            self.rag_content = "\n".join([item.content for item in reranks])
            print(self.rag_content)

            self.last_message = self.sys_messages[self.stage % 4]+"。请告诉我您对创建MCT节点实例还有什么具体需求？"
            self.workflow = None
            self.workflow_form = None
            message = ""
             

        requestStr = f"{self.sys_messages[self.stage % 4]+message}"
        self.console.print(f"[bold green]{requestStr}[/bold green]", end=" ")
        callback(requestStr)

        # for word in words:
        #     if word.startswith('@') and word[1:] in agents.keys():
        #         # print(f"[bold magenta]{word}[bold magenta]", end=' ') 
        #         agent = agents[word.replace('@', '')]
        #     else:
        #         # print(word, end=' ')
        #         pass
        print()
        agent_name = self.agent.name
        agenttips = f"请耐心等待，系统级智能体规划器正在为您实例化rztree的{self.sys_messages[self.stage % 4]}节点"
        self.console.print(f"[bold green][bold magenta]{agenttips}[/bold magenta][/bold green]")
        callback(agenttips)

        match agent_name:
            case "Workflow Generator Agent":
                # if message == "":
                #     console.print(f"[bold red]必须输入实例要求。[/bold red]")#f"[bold red]There MUST be a request to create the agent form.[/bold red]")
                #     continue
                if self.workflow_form:
                    requirements = message
                else:
                    requirements = '** 这是向量数据库中检索出来的相关信息：\n'+self.rag_content+'\n\n** 这是当前的阶段和需求：'+self.sys_messages[self.stage % 4]+'\n'+message
                
                # print(f"实例要求:\n {requirements}\n\n")

                reasoning_content, self.workflow, messages = self.workflow_generating(self.workflow_generator, self.client, self.messages, self.context_variables, requirements, debug)
                # workflow = "这是一个节点实例的语言描述"
                self.agent = self.workflow_former

                chainStr = f"@{agent_name} 思维链:"
                self.console.print(f"[bold green][bold magenta]{chainStr}\n[/bold green][bold blue]{reasoning_content}[/bold blue]")
                callback(f"思维链:")  
                callback(f"{reasoning_content}")

                self.console.print(f"[bold green][bold magenta]@{agent_name}[/bold magenta] 生成的MCT节点实例语言描述:\n[/bold green][bold blue]{self.workflow}[/bold blue]")
                callback(f"生成的MCT节点实例语言描述:")
                callback(f"{self.workflow}")

                self.messages = messages
                self.workflow_form, output_json_form, messages = self.workflow_profiling(self.workflow_former, self.client, self.messages, self.context_variables, debug)

                if self.workflow_form is None:
                    self.console.print(f"[bold red][bold magenta]@{agent_name}[/bold magenta] json文件生成失败, 请给出修改建议.[/bold red]")
                    callback(f"json文件生成失败, 请给出修改建议.")
                    
                    last_message = "请提出具体修改建议或告诉我您想要创建MCT节点实例的需求是什么？"
                    # console.print(f"[bold red][bold magenta]@{agent_name}[/bold magenta] has not created workflow form successfully, please modify your requirements again.[/bold red]")
                    # last_message = "Tell me what do you want to create with `Workflow Chain`?"
                    return
                self.agent = self.workflow_generator 
                self.context_variables["workflow_form"] = self.workflow_form

                self.console.print(f"[bold green][bold magenta]@{agent_name}[/bold magenta] 生成的json为:\n[/bold green][bold blue]{output_json_form}[/bold blue]")
                self.last_message = '如果前端展示的工作流符合你的要求，请输入"ok"；否则，请提出具体修改建议。'
                self.messages = messages
                callback(f"生成的json为:")
                callback(f"{output_json_form}")
                callback(self.last_message)


    def workflow_generating(self, workflow_generator, client, messages, context_variables, requirements, debug):
        messages.append({"role": "user", "content": requirements})
    #     + """
    # Directly output the form in the XML format without ANY other text.
    # """})
        response = client.run(workflow_generator, messages, context_variables, debug=debug)
        workflow = response.messages[-1]["content"]
        if "reasoning_content" in response.messages[-1] or (hasattr(response.messages[-1], 'reasoning_content') and response.messages[-1].reasoning_content):
            reasoning_content = response.messages[-1]["reasoning_content"]
        else:
            reasoning_content = "No reasoning content available"
        messages.extend(response.messages)

        return reasoning_content, workflow, messages

    def workflow_profiling(self, workflow_former, client, messages, context_variables, debug):
        messages.append({"role": "user", "content": """
    Directly output the form in the json format without ANY other text.
    """})
        response = client.run(workflow_former, messages, context_variables, debug=debug)
        output_json_form = response.messages[-1]["content"]
        messages.extend(response.messages)

        MAX_RETRY = 3
        for i in range(MAX_RETRY):
            workflow_form = self.parse_json_form(output_json_form)
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




    def parse_json_form(self, json_str: str) -> str:
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
        


