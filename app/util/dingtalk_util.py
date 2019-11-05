from flask import g
import json


def send_deploy_msg(project, env):
    url = 'https://oapi.dingtalk.com/robot/send?' \
          'access_token=a2e8a14bbc0b7018f2c3b5dab2ce90ddffdc2cae485aa708edea2ebe7057bb26'

    body = {
        'msgtype': 'text',
        'text': {
            "content": '{} 正在发布项目：{} 至 {}, 请知悉！'.format(g.user['username'], project, env)
        }
    }

    headers = {'Content-Type': 'application/json;charset=UTF-8'}

    requests.post(url=url, headers=headers, data=json.dumps(body))