from flask import g
import requests
import json


def send_deploy_msg(project, env):
    url = 'https://oapi.dingtalk.com/robot/send?' \
          'access_token=bf9f34210af450667c156d84ef79b931ea07eb6b139be87fa445848009fb5b0d'

    body = {
        'msgtype': 'text',
        'text': {
            "content": '{} 正在发布项目：{} 至 {}, 请知悉！'.format(g.user['username'], project, env)
        }
    }

    headers = {'Content-Type': 'application/json;charset=UTF-8'}

    #requests.post(url=url, headers=headers, data=json.dumps(body))


