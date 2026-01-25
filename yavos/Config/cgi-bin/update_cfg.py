#!/usr/bin/env python3
import os, sys, cgi, time, json
from Config.cfg import Config

response_obj = {"result":"fail", "reason":"bad json", "data":""}

content_len = os.environ.get('CONTENT_LENGTH', '0')
body = sys.stdin.read(int(content_len))
res = None
try:
    res = json.loads(body)
except:
    res = None

if res is not None:
    # if valid json recvd
    cfg = Config("./")
    for key in res.keys():
        cfg.cfg[key] = res[key]

    cfg.save_cfg()
    response_obj['result'] = "success"
    response_obj['reason'] = "updated"
    response_obj['data'] = cfg.cfg

res_json = json.dumps(response_obj)
print("Content-Type: application/json\n")
print(res_json)

