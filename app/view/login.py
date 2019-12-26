import json
import javaobj
import functools
from app import app, config, redis, JavaToJSONEncoder
from app.exception import *
from flask import render_template
from flask import request, redirect
from urllib import request as client
from app.db.mapper import *


role_service = RoleService()


def auth(auth=None):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kw):
            sid = request.cookies.get('sid')
            g.sid = sid
            try:
                session = redis.get(sid)
                if not session:
                    return render_template('login.html')
                session = json.loads(json.dumps(javaobj.loads(session), cls=JavaToJSONEncoder))
                user = {'username': session['loginId']}
                roles = list(map(lambda r: r.role, role_service.query_list(user)))
                user['roles'] = roles
                g.user = user
                if auth and len(auth) > 1:
                    if len([r for r in roles if r in auth]) == 0:
                        raise Exception('no permission')
            except Exception as e:
                print(e)
                return render_template('login.html', msg=str(e))
            try:
                return func(*args, **kw)
            except NoLoginException as e:
                return render_template('login.html')
        return wrapper
    return decorator


@app.route('/login.html', methods=['GET'])
def login_page():
    return render_template('login.html')


@app.route('/login', methods=['POST'])
def login():
    params = json.dumps({'loginId': request.form.get('username'), 'password': request.form.get('password')})
    headers = {'Content-Type': 'application/json'}
    try:
        uic_req = client.Request(config.LOGIN_URL, data=bytes(params, 'utf-8'), headers=headers)
        uic_resp = client.urlopen(uic_req)
        if uic_resp.code != 200:
            msg = 'request uic failed, resp code: %d' % uic_resp.code
        else:
            result = json.loads(str(uic_resp.read(), 'utf-8'))
            if result['success'] and not hasattr(result, 'errCode'):
                resp = redirect('index.html')
                resp.set_cookie('sid', result['data'])
                return resp
            msg = result['errMsg']
    except Exception as e:
        msg = 'request uic failed, err: %s' % (str(e))

    return render_template('/login.html', msg=msg)



