from flask import g
import requests
import json


def send_deploy_msg(project, env):
    url = 'https://oapi.dingtalk.com/robot/send?' \
          'access_token=b1c43045a5e537cb3e05c079a9b5e61988fd2030801f51e10e36b510fa46f156'

    body = {
        'msgtype': 'text',
        'text': {
            "content": '{} 正在发布项目：{} 至 {}, 请知悉！'.format(g.user['username'], project, env)
        }
    }

    headers = {'Content-Type': 'application/json;charset=UTF-8'}

    requests.post(url=url, headers=headers, data=json.dumps(body))


