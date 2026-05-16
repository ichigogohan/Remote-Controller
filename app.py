import socket
import secrets
import threading
import qrcode
import logging
import os
from flask import Flask, render_template, request
from flask_socketio import SocketIO
from input_handler import InputHandler
from video_server import start_video_server

app = Flask(__name__)
app.config['SECRET_KEY'] = secrets.token_hex(16)
socketio = SocketIO(app, cors_allowed_origins="*")


# Flaskのアクセスログを無効化
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

# Socket.IOの内部ログも無効化
socketio = SocketIO(app, cors_allowed_origins="*", logger=False, engineio_logger=False)


# トークン生成
ACCESS_TOKEN = secrets.token_urlsafe(16)

# 各機能の初期化
handler = InputHandler()
handler.register_handlers(socketio, ACCESS_TOKEN)

def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
    except Exception:
        ip = '127.0.0.1'
    finally:
        s.close()
    return ip

@app.route('/')
def portal():
    token = request.args.get('t')
    if token != ACCESS_TOKEN:
        return render_template('error.html'), 403
    return render_template('portal.html', token=token)

@app.route('/remote')
def remote():
    token = request.args.get('t')
    if token != ACCESS_TOKEN: return render_template('error.html'), 403
    return render_template('index.html', token=token, local_ip=local_ip)

@app.route('/viewer')
def viewer():
    token = request.args.get('t')
    if token != ACCESS_TOKEN: return render_template('error.html'), 403
    stream_url = f"http://{get_local_ip()}:5002/video_feed?t={token}"
    return render_template('viewer.html', token=token, stream_url=stream_url)

if __name__ == '__main__':
    local_ip = get_local_ip()
    main_port = 5001
    url = f"http://{local_ip}:{main_port}/?t={ACCESS_TOKEN}"
    
    # 画面を綺麗にする
    os.system('cls' if os.name == 'nt' else 'clear')
    
    # 必要最低限の「静止」情報だけを出す
    print(f"[*] Server IP: {local_ip}")
    print(f"[*] Control Port: {main_port}")
    print(f"[*] Stream  Port: 5002")
    print("\n[ QRコードをスキャンして接続してください ]")
    
    qr = qrcode.QRCode()
    qr.add_data(url)
    qr.make(fit=True)
    qr.print_ascii()

    print("\n" + "-"*50)
    print(" LOG: Errors only will be shown here.")
    print("-"*50)

    # サーバー起動
    v_thread = threading.Thread(target=start_video_server, args=(ACCESS_TOKEN,), daemon=True)
    v_thread.start()
    
    socketio.run(app, host='0.0.0.0', port=main_port)