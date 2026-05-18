"""Flask Web API 客户端 - 通过 HTTP 连接电脑数据库"""

import json
import os
import urllib.request
import urllib.parse
import http.cookiejar

SETTINGS_FILE = 'flet_settings.json'


class ApiClient:
    def __init__(self):
        self.base_url = ''
        self.logged_in = False
        self.cookie_file = ''
        self._opener = None

    def load_settings(self) -> bool:
        """加载保存的连接设置"""
        paths = [
            SETTINGS_FILE,
            os.path.join(os.path.dirname(os.path.abspath(__file__)), SETTINGS_FILE),
            os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data', SETTINGS_FILE),
        ]
        for p in paths:
            if os.path.exists(p):
                with open(p) as f:
                    cfg = json.load(f)
                    self.base_url = f"http://{cfg['host']}:{cfg['port']}"
                    self.cookie_file = os.path.join(os.path.dirname(p), 'cookies.txt')
                    self._setup_opener()
                    return self._login(cfg['username'], cfg['password'])
        return False

    def save_settings(self, host: str, port: int, username: str, password: str):
        """保存连接设置"""
        path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')
        os.makedirs(path, exist_ok=True)
        cfg_path = os.path.join(path, SETTINGS_FILE)
        with open(cfg_path, 'w') as f:
            json.dump({'host': host, 'port': port, 'username': username, 'password': password}, f)
        self.cookie_file = os.path.join(path, 'cookies.txt')
        self.base_url = f"http://{host}:{port}"
        self._setup_opener()
        self._login(username, password)

    def _setup_opener(self):
        cj = http.cookiejar.LWPCookieJar(self.cookie_file)
        if os.path.exists(self.cookie_file):
            cj.load()
        self._opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))

    def _login(self, username: str, password: str) -> bool:
        try:
            data = json.dumps({'username': username, 'password': password}).encode()
            req = urllib.request.Request(f'{self.base_url}/api/login', data=data,
                                        headers={'Content-Type': 'application/json'})
            resp = self._opener.open(req, timeout=5)
            self.logged_in = resp.getcode() == 200
            # 保存 cookie
            if self.cookie_file and hasattr(self._opener, 'handlers'):
                for h in self._opener.handlers:
                    if isinstance(h, urllib.request.HTTPCookieProcessor):
                        h.cookiejar.save()
            return self.logged_in
        except Exception:
            self.logged_in = False
            return False

    def api_get(self, path: str) -> dict | None:
        """调用 Flask API GET 接口"""
        try:
            req = urllib.request.Request(f'{self.base_url}{path}')
            resp = self._opener.open(req, timeout=10)
            return json.loads(resp.read().decode())
        except Exception:
            return None

    def test_connection(self, host: str, port: int) -> bool:
        """测试能否连接服务器"""
        try:
            req = urllib.request.Request(f'http://{host}:{port}/api/session')
            urllib.request.urlopen(req, timeout=3)
            return True
        except Exception:
            return False


# 全局 API 客户端实例
api = ApiClient()
