import os
import argparse
from flask import Flask, render_template
from flask_socketio import SocketIO
from chat import ChatBlueprint  
from rztree import rztree


class Server(Flask):
    def __init__(self, context_variables: dict, host='0.0.0.0', port=5000):
        super().__init__(__name__)
        self.host = host
        self.port = port  
        self.socketio = SocketIO(self)
        self._setup_app(context_variables)
        print("Server init success! host: ", host, " port ", port)

    def _setup_app(self, context_variables: dict):
        # 配置应用
        self.config['DEBUG'] = False 
        self.config['FILEDIR'] = 'static/_files/'
        self.config['CHAT_URL'] = os.environ.get('CHAT_URL')

        # 注册蓝图
        chat_bp = ChatBlueprint(self.socketio, context_variables)
        self.register_blueprint(chat_bp, url_prefix='/chat')

        # 添加路由
        @self.route('/')
        def index():
            return render_template('index.html')

    def start(self):
        # 启动应用
        self.socketio.run(self, host=self.host, port=self.port, debug=self.config['DEBUG'])


parser = argparse.ArgumentParser(description='argparse')
parser.add_argument('--container_name', type=str, default='autoagent', help='the function to get the agent')
parser.add_argument('--port', type=int, default=12347, help='the port to run the container')
parser.add_argument('--test_pull_name', type=str, default='autoagent_mirror', help='the name of the test pull')
parser.add_argument('--git_clone', type=bool, default=True, help='whether to clone a mirror of the repository')
parser.add_argument('--local_env', type=bool, default=True, help='whether to use local environment')
parser.add_argument('--workflow_name', default='math_problem_solving_workflow_flow', help='the name of the workflow')
parser.add_argument('--system_input', default='Find $k$, if ${(3^k)}^6=3^6$.', help='the user query to the agent')

args = parser.parse_args()

# 启动  
if __name__ == '__main__':
    context_variables = rztree(args.container_name, args.port, args.test_pull_name, args.git_clone, args.local_env)
    
    server = Server(context_variables, host='0.0.0.0', port=5000)

    server.start()

