var input_field = document.getElementById('message');
var chat_field = document.getElementById('chat');

// create a random username
var username = 'user' + parseInt(Math.random() * 10000);

var socketio = io.connect(location.origin + '/chat',
    {query: 'username=' + username, 'transports': ['websocket']});

// 监听连接成功事件
socketio.on('connect', () => {
    console.log('Connected to server');
    // 可以在这里执行其他初始化操作，比如发送初始数据
    socketio.emit('login', { username: username });
});

// event handler when ENTER is pressed on the chat input field
input_field.onchange = function() {
    socketio.emit('post-message', { message: this.value });
    this.value = '';
}

// the server is sending a message to display in the chat window
socketio.on('message', function(message) {
    msg = document.createElement('p');
    if (message.user) {
        // this is a message written by a user
       // msg.innerHTML = '<span class="user">' + message.user + '</span>: ' +
       //     '<span class="message">' + message.message + "</span>";

       const uspan = document.createElement('span');
       uspan.className = "user"; 
       uspan.textContent = message.user + ": ";
       msg.appendChild(uspan);

       const mspan = document.createElement('span');
       mspan.className = "message"; 
       mspan.textContent = message.message;
       msg.appendChild(mspan);
    }
    else {
        // this is a control message that comes from the server itself
        msg.innerHTML = '<span class="control-message">' + message.message + '</span>';
    }
    chat_field.appendChild(msg);
    chat_field.scrollTop = chat.scrollHeight; // scroll to bottom
});

input_field.focus();