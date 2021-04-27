from pathlib import Path
from fastapi import FastAPI
from pydantic import BaseModel


app = FastAPI()
list_path = Path(__file__).parent / 'ps.lst'


class PS(BaseModel):
    ps: dict


def parse_ps(ps_str):
    ps = {}
    ban_ps = {}
    for p in ps_str.split('\n'):
        p = p.strip()
        if not p: continue
        s = p.split(',')
        name, paths = s[0], s[1:]
        if not name: continue
        if name[0] == '!':
            ban_ps[name[1:]] = paths
        else:
            ps[name] = paths
    return ps, ban_ps

def ps_to_str(ps, ban_ps={}):
    lines = ''
    for k, v in ban_ps.items():
        line = '!' + k
        for i in v:
            if i:
                line += ',' + i
        lines += line + '\n'
    for k, v in ps.items():
        line = k
        for i in v:
            if i:
                line += ',' + i
        lines += line + '\n'
    return lines


@app.get('/get_ps')
def get_ps():
    with list_path.open('r', encoding='utf8') as fr:
        ps, ban_ps = parse_ps(fr.read())
    return {'ps': ps, 'ban_ps': ban_ps}


@app.post('/update_ps')
def update_ps(ps: PS):
    update_ps = ps.ps
    with list_path.open('r', encoding='utf8') as fr:
        ps, ban_ps = parse_ps(fr.read())
    flag = False
    for name in update_ps.keys():
        if name in ban_ps:
            for p in update_ps[name]:
                if p not in ban_ps[name]:
                    ban_ps[name].append(p)
                    flag = True
        elif name in ps:
            for p in update_ps[name]:
                if p not in ps[name]:
                    ps[name].append(p)
                    flag = True
        else:
            ps[name] = update_ps[name]
            flag = True
    if flag:
        with list_path.open('w', encoding='utf-8') as fw:
            fw.write(ps_to_str(ps, ban_ps))
    return ps
