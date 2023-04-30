from flask import Flask, render_template_string, request
from flask_socketio import SocketIO, emit
import os
import json

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret_key'
socketio = SocketIO(app)
filename = "notepad.json"

def load_data():
    if os.path.exists(filename):
        with open(filename, 'r') as f:
            return json.load(f)
    else:
        return {"note_content": ""}

def save_data(data):
    with open(filename, 'w') as f:
        json.dump(data, f)

@app.route('/')
def index():
    data = load_data()
    return render_template_string(html_string, note=data['note_content'])

@socketio.on('update_content')
def update_content(content):
    data = load_data()
    data['note_content'] = content
    save_data(data)
    emit('content_update', content, broadcast=True)

html_string = '''
<!DOCTYPE html>
<html lang="zh">
<head>
    <meta charset="UTF-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <script src="https://cdnjs.cloudflare.com/ajax/libs/socket.io/4.0.1/socket.io.min.js"></script>
    <script>
        document.addEventListener('DOMContentLoaded', function() {
            const note = document.getElementById('note');
            const socket = io();
            note.focus();

            let previousContent = note.innerHTML;
            let timeout;

            function broadcastUpdate() {
                const currentContent = note.innerHTML;
                if (previousContent !== currentContent) {
                    socket.emit('update_content', currentContent);
                    previousContent = currentContent;
                }
            }

            note.addEventListener('input', function() {
                clearTimeout(timeout);
                timeout = setTimeout(broadcastUpdate, 500);
            });

            socket.on('content_update', function(content) {
                if (previousContent !== content) {
                    previousContent = content;
                    note.innerHTML = content;
                    note.focus();
                }
            });
        });
    </script>
    <style>
        body, html {
            height: 100%;
            margin: 0;
        }
        #note {
            width: 100%;
            height: 100%;
            border: none;
            outline: none;
            overflow-wrap: break-word;
            resize: none;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            font-size: 16px;
            line-height: 1.5;
            padding: 16px;
        }
    </style>
</head>
<body>
    <div id="note" contenteditable="true">{{ note | safe }}</div>
</body>
</html>
'''

if __name__ == '__main__':
    socketio.run(app, debug=True, port=6000)
