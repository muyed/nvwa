from flask import g
import requests
import json


def send_deploy_msg(project, env):
    url = 'https://oapi.dingtalk.com/robot/send?' \
          'access_token=c860555f9e33c15d15f14f550ce241db09301b7d6a9b285fb5aa2e65168bd65e'

    body = {
        'msgtype': 'text',
        'text': {
            "content": '{} 正在发布项目：{} 至 {}, 请知悉！'.format(g.user['username'], project, env)
        }
    }

    headers = {'Content-Type': 'application/json;charset=UTF-8'}

    requests.post(url=url, headers=headers, data=json.dumps(body))


