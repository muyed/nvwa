from flask import g
import requests
import json


def send_deploy_msg(project, env):
    url = 'https://oapi.dingtalk.com/robot/send?' \
          'access_token=7be81ff47551d835b9761d6e772db3fea0b0dc08a32cbc2ecff72b56a8227795'

    body = {
        'msgtype': 'text',
        'text': {
            "content": '{} 正在发布项目：{} 至 {}, 请知悉！'.format(g.user['username'], project, env)
        }
    }

    headers = {'Content-Type': 'application/json;charset=UTF-8'}

    requests.post(url=url, headers=headers, data=json.dumps(body))


