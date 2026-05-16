import cv2
import numpy as np
from mss import mss
import pyautogui
from flask import Flask, Response, request, jsonify
import time
import threading


video_app = Flask(__name__)

# サーバー統計情報（グローバル変数）
server_stats = {
    "fps": 0,
    "bps": 0,
    "last_update": time.time()
}

def generate_frames(token, target_token, quality=50, scale=0.5, fps_limit=30, show_mouse=True):
    with mss() as sct:
        monitor = sct.monitors[1]
        
        # 統計計算用
        frame_count = 0
        byte_count = 0
        last_stat_time = time.time()
        
        while True:
            loop_start = time.time()

            if token != target_token: return

            # 画面キャプチャ
            sct_img = sct.grab(monitor)
            img = np.array(sct_img)
            frame = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)

            # マウスカーソルの描画
            if show_mouse:
                mx, my = pyautogui.position()
                # mssの座標系と合う前提での簡易描画
                cv2.circle(frame, (mx, my), 8, (0, 0, 255), -1) 

            # リサイズ (Scale)
            if scale != 1.0:
                frame = cv2.resize(frame, (0, 0), fx=scale, fy=scale)
            
            # JPEGエンコード (Quality)
            ret, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, quality])
            if not ret: continue
            
            frame_bytes = buffer.tobytes()
            size_bytes = len(frame_bytes)

            # 統計更新 (1秒ごとに計算)
            current_time = time.time()
            frame_count += 1
            byte_count += size_bytes
            
            if current_time - last_stat_time >= 1.0:
                server_stats["fps"] = frame_count / (current_time - last_stat_time)
                server_stats["bps"] = (byte_count * 8) / (current_time - last_stat_time)
                server_stats["last_update"] = current_time
                frame_count = 0
                byte_count = 0
                last_stat_time = current_time
            
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n'
                   b'Content-Length: ' + str(size_bytes).encode() + b'\r\n\r\n' + 
                   frame_bytes + b'\r\n')

            # FPS制限 (処理時間を差し引いて待機)
            process_time = time.time() - loop_start
            wait_time = (1.0 / fps_limit) - process_time
            if wait_time > 0:
                time.sleep(wait_time)

# 1. フル機能・閲覧用 (設定変更可能)
@video_app.route('/video_feed')
def video_feed():
    token = request.args.get('t')
    
    # URLパラメータの取得とバリデーション
    try:
        quality = int(request.args.get('q', 50))
        scale = float(request.args.get('s', 0.5))
        fps = int(request.args.get('fps', 30))
    except ValueError:
        quality, scale, fps = 50, 0.5, 30

    # 範囲制限
    quality = max(10, min(100, quality))
    scale = max(0.1, min(1.0, scale))
    fps = max(1, min(60, fps))

    return Response(generate_frames(token, video_app.config['ACCESS_TOKEN'], 
                                    quality=quality, scale=scale, fps_limit=fps),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

# 2. 低負荷・プレビュー用
@video_app.route('/preview_feed')
def preview_feed():
    token = request.args.get('t')
    return Response(generate_frames(token, video_app.config['ACCESS_TOKEN'], 
                                    quality=40, scale=0.4, fps_limit=10, show_mouse=True),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

# 3. テレメトリ用API (CORS対応)
@video_app.route('/telemetry')
def telemetry():
    data = {
        "server_time": time.time(),
        "fps": round(server_stats["fps"], 1),
        "bps": int(server_stats["bps"])
    }
    resp = jsonify(data)
    # 異なるポート(5001)からのアクセスを許可
    resp.headers.add('Access-Control-Allow-Origin', '*')
    return resp

def start_video_server(token):
    video_app.config['ACCESS_TOKEN'] = token
    # threaded=Trueで並列処理を有効化
    video_app.run(host='0.0.0.0', port=5002, threaded=True, use_reloader=False)

if __name__ == "__main__":
    start_video_server("test_token")