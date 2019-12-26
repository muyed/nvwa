from .login import *


@app.route('/role/list.html', methods=['GET'])
@auth(['管理员'])
def get_list():
    query = {}
    page = {}
    username = request.args.get('username')
    current_page = request.args.get('current')
    if username:
        query['username'] = username
    if current_page:
        page['current'] = int(current_page)

    roles = role_service.query_list(query, page)

    return render_template('role/role_list.html', user=g.user, roles=roles, query=query, page=page)


@app.route('/role/add.html', methods=['GET'])
@auth(['管理员'])
def to_add():
    return render_template('role/role_add.html', user=g.user, role={})


@app.route('/role/add.html', methods=['POST'])
@auth(['管理员'])
def add():
    role = create_model(Role, request.form.to_dict())
    msg = None
    if not role or not getattr(role, 'username', None):
        msg = '鼠名必填'
    if not hasattr(role, 'role') or role.role not in ['管理员', '开发', '测试', '运维']:
        msg = '角色不正确'

    if len(role_service.query_list(request.form.to_dict())) > 0:
        msg = '用户角色已经存在'

    if not getattr(role, 'is_manager'):
        msg = '是否负责人比选'

    if not getattr(role, 'is_owner'):
        msg = '是否owner比选'

    if not getattr(role, 'email'):
        msg = '邮箱必填'

    if msg:
        return render_template('role/role_add.html', user=g.user, role=role, msg=msg)

    role_service.add(role)
    return redirect('/role/list.html')


@app.route('/role/update/<id>.html', methods=['GET'])
@auth(['管理员'])
def to_role_update(id):
    role = role_service.get_by_id(id)
    return render_template("/role/role_update.html", user=g.user, role=role)


@app.route('/role/update.html', methods=['POST'])
@auth(['管理员'])
def role_update():
    role = create_model(Role, request.form.to_dict())

    msg = None
    if not role or not getattr(role, 'username', None):
        msg = '鼠名必填'
    if not hasattr(role, 'role') or role.role not in ['管理员', '开发', '测试', '运维']:
        msg = '角色不正确'

    if len(role_service.query_list(request.form.to_dict())) > 0:
        msg = '用户角色已经存在'

    if not getattr(role, 'is_manager'):
        msg = '是否负责人比选'

    if not getattr(role, 'is_owner'):
        msg = '是否owner比选'

    if not getattr(role, 'email'):
        msg = '邮箱必填'

    if msg:
        return render_template('role/role_update.html', user=g.user, role=role, msg=msg)

    role_service.update(role)

    return redirect('/role/list.html')


@app.route('/role/del/<id>')
@auth(['管理员'])
def del_by_id(id):
    role_service.del_by_id(id)
    return redirect('/role/list.html')
