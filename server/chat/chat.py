from flask import Blueprint, render_template, request, session, current_app, url_for
from flask_socketio import emit
from .work import Work

class ChatBlueprint(Blueprint):
    def __init__(self, socketio, context_variables: dict):
        print("ChatBlueprint init")
        super().__init__("chat", __name__, static_folder='static', template_folder='templates')
        
        self.socketio = socketio
        self.namespace = '/chat'
        self.work = Work(context_variables) 
        # on_emit_message(self.work.last_message)

        # 注册路由
        @self.route('/')
        def index():
            """Return the client application."""
            chat_url = current_app.config.get('CHAT_URL') or url_for('chat.index', _external=True)
            print("############### chat index  ", chat_url)

            # 打印模板加载器的路径
            loader = current_app.jinja_loader  
            if loader:
                print("Template paths:")
                for path in loader.list_templates():
                    print(path)
            else:
                print("No template loader found.")
            return render_template('chat/main.html', chat_url=chat_url)

        # 定义事件处理器
        def on_connect():
            print("############### chat on_connect")
            """A new user connects to the chat."""
            if request.args.get('username') is None:
                return False
            print("############### chat on_connect ", request.args['username'])
            session['username'] = request.args['username']
            emit('message', {'message': session['username'] + ' has joined.'}, broadcast=True)
            emit('message', {'message': '现在是状态确定阶段,请输入开始。'}, broadcast=True)
            

        def on_disconnect():
            print("############### chat on_disconnect")
            """A user disconnected from the chat."""
            emit('message', {'message': session['username'] + ' has left.'}, broadcast=True)

        def on_login(message):    
            print("############### chat on_login")
            emit('message', {'message': session['username'] + ' has logined.'}, broadcast=True) 
            # session['work'] = Work() 
            
        def on_emit_message(message):
            emit('message', {'user': 'system', 'message': message}, broadcast=True)
    
        def on_post_message(message):
            print("############### chat on_post_message ", message)
            """A user posted a message to the chat."""
            emit('message', {'user': session['username'], 'message': message['message']}, broadcast=True)
            self.work.query(message['message'], on_emit_message)


        # 注册事件处理器
        self.socketio.on_event('connect', on_connect, namespace=self.namespace)
        self.socketio.on_event('disconnect', on_disconnect, namespace=self.namespace)
        self.socketio.on_event('post-message', on_post_message, namespace=self.namespace)
        self.socketio.on_event('login', on_login, namespace=self.namespace)






