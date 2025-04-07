import click
import importlib
from autoagent import MetaChain
from autoagent.util import debug_print
import asyncio
from constant import DOCKER_WORKPLACE_NAME
from autoagent.io_utils import read_yaml_file, get_md5_hash_bytext, read_file
from autoagent.environment.utils import setup_metachain
from autoagent.types import Response
from autoagent import MetaChain
from autoagent.util import ask_text, single_select_menu, print_markdown, debug_print, UserCompleter
from prompt_toolkit import PromptSession
from prompt_toolkit.completion import Completer, Completion
from prompt_toolkit.formatted_text import HTML
from prompt_toolkit.styles import Style
from rich.progress import Progress, SpinnerColumn, TextColumn
import json
import argparse
from datetime import datetime
from autoagent.agents.meta_agent import tool_editor, agent_editor
from autoagent.tools.meta.edit_tools import list_tools
from autoagent.tools.meta.edit_agents import list_agents
from loop_utils.font_page import MC_LOGO, version_table, NOTES, GOODBYE_LOGO
from rich.live import Live
from autoagent.environment.docker_env import DockerEnv, DockerConfig, check_container_ports
from autoagent.environment.local_env import LocalEnv
from autoagent.environment.browser_env import BrowserEnv
from autoagent.environment.markdown_browser import RequestsMarkdownBrowser
from evaluation.utils import update_progress, check_port_available, run_evaluation, clean_msg
import os
import os.path as osp
# from autoagent.agents import get_system_triage_agent
from autoagent.logger import LoggerManager, MetaChainLogger 
from rich.console import Console
from rich.markdown import Markdown
from rich.table import Table
from rich.columns import Columns
from rich.text import Text
from rich.panel import Panel
import re
from autoagent.cli_utils.metachain_meta_agent import meta_agent
from autoagent.cli_utils.metachain_meta_workflow_rag import meta_workflow
from autoagent.cli_utils.file_select import select_and_copy_files
from evaluation.utils import update_progress, check_port_available, run_evaluation, clean_msg
from constant import COMPLETION_MODEL


# @click.group()
# def cli():
#     """The command line interface for autoagent"""
#     pass


# @cli.command()
# @click.option('--workflow_name', default='math_problem_solving_workflow', help='the name of the workflow')
# @click.option('--system_input', default='Find $k$, if ${(3^k)}^6=3^6$.', help='the user query to the agent')
def workflow(workflow_name: str):#, system_input: str):
    style = Style.from_dict({
        'bottom-toolbar': 'bg:#333333 #ffffff',
    })
    session = PromptSession(
        style=style
    )
    system_input = session.prompt(
        '工作流的输入(type "exit" to quit, press "Enter" to continue): '
    )
    if system_input == "exit":
        return
    """命令行函数的同步包装器"""
    return asyncio.run(async_workflow(workflow_name, system_input))

async def async_workflow(workflow_name: str, system_input: str):
    """异步实现的workflow函数"""
    workflow_module = importlib.import_module(f'autoagent.workflows')
    try:
        workflow_func = getattr(workflow_module, workflow_name)
    except AttributeError:
        raise ValueError(f'Workflow function {workflow_name} not found...')
    
    result = await workflow_func(system_input)  # 使用 await 等待异步函数完成
    debug_print(True, result, title=f'Result of running {workflow_name} workflow', color='pink3')
    return result

def clear_screen():
    console = Console()
    console.print("[bold green]Coming soon...[/bold green]")
    print('\033[u\033[J\033[?25h', end='')  # Restore cursor and clear everything after it, show cursor
def get_config(container_name, port, test_pull_name="main", git_clone=False):
    container_name = container_name
    
    port_info = None#ccheck_container_ports(container_name)
    if port_info:
        port = port_info[0]
    else:
        # while not check_port_available(port):
        #     port += 1
        # 使用文件锁来确保端口分配的原子性
        import filelock
        lock_file = os.path.join(os.getcwd(), ".port_lock")
        lock = filelock.FileLock(lock_file)
        
        with lock:
            port = port
            while not check_port_available(port):
                port += 1
                print(f'{port} is not available, trying {port+1}')
            # 立即标记该端口为已使用
            with open(os.path.join(os.getcwd(), f".port_{port}"), 'w') as f:
                f.write(container_name)
    local_root = os.path.join(os.getcwd(), f"workspace_meta_showcase", f"showcase_{container_name}")
    os.makedirs(local_root, exist_ok=True)
    docker_config = DockerConfig(
        workplace_name=DOCKER_WORKPLACE_NAME,
        container_name=container_name,
        communication_port=port,
        conda_path='/root/miniconda3',
        local_root=local_root,
        test_pull_name=test_pull_name,
        git_clone=git_clone
    )
    return docker_config
def create_environment(docker_config: DockerConfig):
    """
    1. create the code environment
    2. create the web environment
    3. create the file environment
    """
    code_env = DockerEnv(docker_config)
    code_env.init_container()
    
    web_env = BrowserEnv(browsergym_eval_env = None, local_root=docker_config.local_root, workplace_name=docker_config.workplace_name)
    file_env = RequestsMarkdownBrowser(viewport_size=1024 * 5, local_root=docker_config.local_root, workplace_name=docker_config.workplace_name, downloads_folder=os.path.join(docker_config.local_root, docker_config.workplace_name, "downloads"))
    
    return code_env, web_env, file_env

def create_environment_local(docker_config: DockerConfig):
    """
    1. create the code environment
    2. create the web environment
    3. create the file environment
    """
    code_env = LocalEnv(docker_config)

    web_env = None#BrowserEnv(browsergym_eval_env = None, local_root=docker_config.local_root, workplace_name=docker_config.workplace_name)
    file_env = None#RequestsMarkdownBrowser(viewport_size=1024 * 5, local_root=docker_config.local_root, workplace_name=docker_config.workplace_name, downloads_folder=os.path.join(docker_config.local_root, docker_config.workplace_name, "downloads"))
    
    return code_env, web_env, file_env

def update_guidance(context_variables): 
    console = Console()

    # print the logo
    logo_text = Text(MC_LOGO, justify="center")
    console.print(Panel(logo_text, style="bold salmon1", expand=True))
    console.print(version_table)
    console.print(Panel(NOTES,title="Important Notes", expand=True))

# @cli.command(name='main')  # 修改这里，使用连字符
# @click.option('--container_name', default='autoagent', help='the function to get the agent')
# @click.option('--port', default=12347, help='the port to run the container')
# @click.option('--test_pull_name', default='autoagent_mirror', help='the name of the test pull')
# @click.option('--git_clone', default=True, help='whether to clone a mirror of the repository')
# @click.option('--local_env', default=True, help='whether to use local environment')#True False
def main(container_name: str, port: int, test_pull_name: str, git_clone: bool, local_env: bool):
    """
    Run deep research with a given model, container name, port
    """ 
    model = COMPLETION_MODEL
    print('\033[s\033[?25l', end='')  # Save cursor position and hide cursor
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        transient=True  # 这会让进度条完成后消失
    ) as progress:
        task = progress.add_task("[cyan]Initializing...", total=None)
        
        progress.update(task, description="[cyan]Initializing config...[/cyan]\n")
        docker_config = get_config(container_name, port, test_pull_name, git_clone)
        
        progress.update(task, description="[cyan]Setting up logger...[/cyan]\n")
        log_path = osp.join("casestudy_results", 'logs', f'agent_{container_name}_{model}.log')
        LoggerManager.set_logger(MetaChainLogger(log_path = None))
        
        progress.update(task, description="[cyan]Creating environment...[/cyan]\n")
        if local_env:
            code_env, web_env, file_env = create_environment_local(docker_config)
        else:
            code_env, web_env, file_env = create_environment(docker_config)
        
        progress.update(task, description="[cyan]Setting up autoagent...[/cyan]\n")
    
    clear_screen()
    context_variables = {}#{"working_dir": docker_config.workplace_name, "code_env": code_env, "web_env": web_env, "file_env": file_env}
    print(context_variables)

    clear_screen()
    meta_workflow(model, context_variables, False)
 

parser = argparse.ArgumentParser(description='argparse')
parser.add_argument('--container_name', type=str, default='autoagent', help='the function to get the agent')
parser.add_argument('--port', type=int, default=12347, help='the port to run the container')
parser.add_argument('--test_pull_name', type=str, default='autoagent_mirror', help='the name of the test pull')
parser.add_argument('--git_clone', type=bool, default=True, help='whether to clone a mirror of the repository')
parser.add_argument('--local_env', type=bool, default=True, help='whether to use local environment')
parser.add_argument('--workflow_name', default='math_problem_solving_workflow_flow', help='the name of the workflow')
parser.add_argument('--system_input', default='Find $k$, if ${(3^k)}^6=3^6$.', help='the user query to the agent')

args = parser.parse_args()

if __name__ == '__main__':
    main(args.container_name, args.port, args.test_pull_name, args.git_clone, args.local_env)
    # workflow(args.workflow_name)