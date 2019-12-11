import json
from urllib import request as client
from app import config
from ..util.ras_util import encrypt


def exec_sql(url, username, password, sql, sid):

    params = json.dumps({'url': url, 'username': username, 'password': password,
                         'sql': [encrypt(sql[i:i+100]) for i in range(0, len(sql), 100)]})
    headers = {'Content-Type': 'application/json', 'Cookie': 'sid=%s' % sid}
    try:
        exec_req = client.Request(config.DB_EXEC_URL, data=bytes(params, 'utf-8'), headers=headers)
        exec_resp = client.urlopen(exec_req)
        if exec_resp.code != 200:
            return 'request umc failed, resp code: %d' % exec_resp.code
        result = json.loads(str(exec_resp.read(), 'utf-8'))
        if result['errCode']:
            return result['errCode']
        data = result['data']
        if data['status'] == -1:
            return data['errMsg']
        exec_result_list = data['resultList']
        result_str = ''
        for line in exec_result_list:
            result_str = result_str + '行号：%d, 执行状态：%s, 错误信息：%s \n' % \
                         (line['lineNum'], '成功' if(line['status'] == 0) else '失败', line['errMsg'])
        return [result_str]
    except Exception as e:
        return str(e)


