import json
import time
import random
import psutil
import requests

from pathlib import Path
from svr import parse_ps, ps_to_str


class TaskWatcher:
    def __init__(self, ps_path=None):
        self.current_dir = Path(__file__).parent.resolve()
        if not ps_path:
            ps_path = Path.home() / 'ps.lst'
        self.ps_path = ps_path
        self.URL = 'http://10.65.3.17:1075'
        self.API_GET_PS = f'{self.URL}/get_ps'
        self.API_UPDATE_PS = f'{self.URL}/update_ps'
        if self.ps_path.exists():
            with self.ps_path.open('r', encoding='utf-8') as fr:
                self.ps, self.ban_ps = parse_ps(fr.read())
        
    def get_remote_ps(self):
        result = requests.get(self.API_GET_PS)
        if result.ok:
            j = result.json()
            self.ps = j['ps']
            self.ban_ps = j['ban_ps']
        else:
            self.ps = {}
            self.ban_ps = {}
        with self.ps_path.open('w', encoding='utf-8') as fw:
            fw.write(ps_to_str(self.ps, self.ban_ps))

    def update_ps(self):
        for pid in psutil.pids():
            if pid == 0: continue
            try:
                p = psutil.Process(pid)
                name = p.name().lower()
                if not name: continue
                if not self.ps.get(name):
                    self.ps[name] = []
                if p.exe() not in self.ps[name]:
                    self.ps[name].append(p.exe())
            except Exception as e:
                print(e)
        r = requests.post(self.API_UPDATE_PS, json={'ps': self.ps}) 
        return r.ok
    
    def kill_ps(self):
        for pid in psutil.pids():
            if pid == 0: continue
            try:
                p = psutil.Process(pid)
                if p.name() in self.ban_ps:
                    # print(f'kill {p.name()}')
                    p.kill()
            except Exception as e:
                print(e)

    def run(self):
        while True:
            self.get_remote_ps()
            self.update_ps()
            self.kill_ps()
            time.sleep(random.randint(1, 30))


if __name__ == '__main__':
    taskwatcher = TaskWatcher()
    taskwatcher.run()
