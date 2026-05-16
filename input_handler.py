import pyautogui

# 基本設定
pyautogui.FAILSAFE = False
pyautogui.PAUSE = 0 

class InputHandler:
    def __init__(self):
        self.key_map = {
            "BS": "backspace", "Enter": "enter", "Space": "space",
            "Tab": "tab", "Esc": "esc", "Del": "delete",
            "zenkakuhankaku": "kanji", "かな": "hiragana"
        }

    def register_handlers(self, socketio, token):
        """Socket.IOイベントを登録する"""
        
        @socketio.on('connect')
        def handle_connect(auth):
            if not auth or auth.get('token') != token:
                return False

        @socketio.on('mouse_move')
        def handle_mouse(data):
            # 感度調整が必要な場合はここで data['x'] * 1.5 などとする
            pyautogui.moveRel(data.get('x'), data.get('y'), _pause=False)

        @socketio.on('mouse_down')
        def handle_down(data):
            pyautogui.mouseDown(button=data.get('button'))

        @socketio.on('mouse_up')
        def handle_up(data):
            pyautogui.mouseUp(button=data.get('button'))

        @socketio.on('mouse_wheel')
        def handle_wheel(data):
            # OSにより感度が異なるため要調整
            pyautogui.scroll(int(data.get('dy')))

        @socketio.on('key_event')
        def handle_key(data):
            key = data.get('key')
            mods = data.get('mods', [])
            target_key = self.key_map.get(key, key.lower())
            
            if mods:
                pyautogui.hotkey(*[m.lower() for m in mods], target_key)
            else:
                pyautogui.press(target_key)
            #print(f"Key: {mods} + {target_key}")