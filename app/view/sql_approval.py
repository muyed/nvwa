from .login import *
from ..util.email_util import send
from ..util.ras_util import encrypt
from ..util.db_exec_util import exec_sql, explain
import json

sql_approval_service = SqlApprovalService()
db_info_service = DbInfoService()


@app.route('/sql/approval/list.html', methods=['GET'])
@auth(['开发', '测试', '运维'])
def approval_list():
    query = {}
    page = {}
    status = request.args.get('status')
    title = request.args.get('title')
    current_page = request.args.get('current')
    if status:
        query['status'] = status
    if title:
        query['title'] = title
    if current_page:
        page['current_page'] = current_page

    approvals = sql_approval_service.my_list(query, page)

    return render_template('sqlapproval/approval_list.html', user=g.user, approvals=approvals, query=query, page=page)


@app.route('/sql/approval/add.html', methods=['GET'])
@auth(['开发', '测试', '运维'])
def to_approval_add():
    managers = role_service.query_list({'role': '开发', 'is_manager': 1}, {'size': 2000})
    dbs = db_info_service.query_list({}, {'size': 1000})

    return render_template('sqlapproval/approval_add.html', user=g.user, approval={}, managers=managers, dbs=dbs)


@app.route('/sql/approval/add.html', methods=['POST'])
@auth(['开发', '测试', '运维'])
def approval_add():
    approval = create_model(SqlApproval, request.form.to_dict())

    msg = None
    if not getattr(approval, 'title', None) or not getattr(approval, 'approver', None) \
            or not getattr(approval, 'sql', None) or not getattr(approval, 'cause', None):
        msg = '标题、SQL脚本、发起原因、审批人必填，请填写完整'
    if msg:
        managers = role_service.query_list({'role': '开发', 'is_manager': 1}, {'size': 2000})
        return render_template('sqlapproval/approval_add.html', user=g.user, approval=approval, msg=msg,
                               managers=managers)

    setattr(approval, 'status', 0)
    setattr(approval, 'promoter', g.user['username'])

    sql_approval_service.add(approval)

    subject = '【线上SQL执行申请】%s' % getattr(approval, 'title')
    body = '''
        发起人：%s
        
        线上SQL执行原因：
            %s
        
        执行SQL脚本为：
            %s
        
        请 %s 审核脚本 并指定执行人
    ''' % (getattr(approval, 'promoter'), getattr(approval, 'cause'), getattr(approval, 'sql'),
           getattr(approval, 'approver'))

    manager = role_service.query_list({'username': getattr(approval, 'approver')})[0]

    send(subject, body, [getattr(manager, 'email')], ['yunzaocenter@3songshu.com'])

    return redirect('/sql/approval/list.html')


@app.route('/sql/approval/update/<id>.html', methods=['GET'])
@auth(['开发', '测试', '运维'])
def to_approval_update(id):
    approval = sql_approval_service.get_by_id(id)
    managers = role_service.query_list({'role': '开发', 'is_manager': 1}, {'size': 2000})
    dbs = db_info_service.query_list({}, {'size': 1000})
    return render_template('sqlapproval/approval_update.html', user=g.user, approval=approval, managers=managers,
                           dbs=dbs)


@app.route('/sql/approval/update.html', methods=['POST'])
@auth(['开发', '测试', '运维'])
def approval_update():
    approval = create_model(SqlApproval, request.form.to_dict())

    msg = None
    if not getattr(approval, 'title', None) or not getattr(approval, 'approver', None) \
            or not getattr(approval, 'sql', None) or not getattr(approval, 'cause', None):
        msg = '标题、SQL脚本、发起原因、审批人必填，请填写完整'

    if msg:
        managers = role_service.query_list({'role': '开发', 'is_manager': 1}, {'size': 2000})
        return render_template('sqlapproval/approval_update.html', user=g.user, approval=approval, msg=msg,
                               managers=managers)

    old = sql_approval_service.get_by_id(getattr(approval, 'id'))

    if getattr(old, 'status') != 0 and getattr(old, 'status') != 2:
        msg = '只有状态为待审核和审核未通过可以再次编辑'
    if msg:
        return render_template('sqlapproval/approval_update.html', user=g.user, approval=approval, msg=msg)

    setattr(approval, 'status', 0)
    setattr(approval, 'promoter', g.user['username'])

    sql_approval_service.update(approval)

    subject = '【线上SQL执行申请】%s' % getattr(approval, 'title')
    body = '''
            发起人：%s

            线上SQL执行原因：
                %s

            执行SQL脚本为：
                %s

            请 %s 审核脚本 并指定执行人
        ''' % (getattr(approval, 'promoter'), getattr(approval, 'cause'), getattr(approval, 'sql'),
               getattr(approval, 'approver'))

    manager = role_service.query_list({'username': getattr(approval, 'approver')})[0]

    send(subject, body, [getattr(manager, 'email')], ['yunzaocenter@3songshu.com'])

    return redirect('/sql/approval/list.html')


@app.route('/sql/approval/del/<id>.html')
@auth(['开发', '测试', '运维'])
def approval_del(id):
    approval = sql_approval_service.get_by_id(id)
    if not approval:
        return redirect('/sql/approval/list.html')

    msg = None

    if getattr(approval, 'status', 0) == 3:
        msg = '已执行的sql记录不能删除'
    if getattr(approval, 'promoter') != g.user['username']:
        msg = '只能删除自己发起的审核记录'

    if msg:
        return redirect('/sql/approval/list.html', msg=msg)

    sql_approval_service.del_by_id(id)

    return redirect('/sql/approval/list.html')


@app.route('/sql/approval/<id>.html', methods=['GET'])
@auth(['开发', '测试', '运维'])
def to_approval(id):
    approval = sql_approval_service.get_by_id(id)
    owner = role_service.query_list({'role': '开发', 'is_owner': 1}, {'size': 2000})

    return render_template("/sqlapproval/approval.html", user=g.user, approval=approval, owner=owner)


@app.route('/sql/approval.html', methods=['POST'])
@auth(['开发', '测试', '运维'])
def approval():
    param = create_model(SqlApproval, request.form.to_dict())

    msg = None

    status = getattr(param, 'status')
    opinion = getattr(param, 'approval_opinion')
    executor = getattr(param, 'executor')

    approval = sql_approval_service.get_by_id(getattr(param, 'id'))

    if not status or not opinion:
        msg = '审核状态、审核意见必填'

    status = int(status)

    if status == 1 and not executor:
        msg = '没有指定执行人'
    if getattr(approval, 'status') != 0:
        msg = '状态必须为待审核'
    if getattr(approval, 'approver') != g.user['username']:
        msg = '你不是审核人'

    setattr(approval, 'status', status)
    setattr(approval, 'approval_opinion', opinion)
    setattr(approval, 'executor', executor)

    promoter = role_service.query_list({'username': getattr(approval, 'promoter')})[0]

    if msg:
        owner = role_service.query_list({'role': '开发', 'is_owner': 1}, {'size': 2000})
        return render_template("/sqlapproval/approval.html", user=g.user, approval=approval, msg=msg, owner=owner)

    if status == 2:
        delattr(approval, 'executor')

    sql_approval_service.update(param)

    subject = '【线上SQL审核结果】%s' % getattr(approval, 'title')

    if status == 1:
        db_info = db_info_service.query_by_name(getattr(approval, 'db_name'))
        plain = explain(getattr(db_info, 'db_url'), getattr(db_info, 'username'), getattr(db_info, 'password'),
                        getattr(approval, 'sql'))
        executor = role_service.query_list({'username': getattr(approval, 'executor')})[0]
        body = '''
                发起人：%s

                线上SQL执行原因：
                    %s

                执行SQL脚本为：
                    %s
                
                执行计划为：
                    %s

                已由 %s 审核通过，审核意见：
                    %s
                
                请 %s执行上线
                ''' \
               % (getattr(approval, 'promoter'), getattr(approval, 'cause'), getattr(approval, 'sql'), plain,
                  getattr(approval, 'approver'), getattr(approval, 'approval_opinion'), getattr(approval, 'executor'))
        send(subject, body, [getattr(promoter, 'email'), getattr(executor, 'email')], ['yunzaocenter@3songshu.com'])
    else:
        body = '''
                发起人：%s

                线上SQL执行原因：
                    %s

                执行SQL脚本为：
                    %s

                已被 %s 审核驳回，审核意见：
                    %s
                ''' % (getattr(approval, 'promoter'), getattr(approval, 'cause'), getattr(approval, 'sql'),
                       getattr(approval, 'approver'), getattr(approval, 'approval_opinion'))

        send(subject, body, [getattr(approval, 'email')], ['yunzaocenter@3songshu.com'])

    return redirect('/sql/approval/list.html')


@app.route('/sql/approval/detail/<id>.html', methods=['GET'])
@auth(['开发', '测试', '运维'])
def approval_detail(id):
    approval = sql_approval_service.get_by_id(id)
    return render_template("/sqlapproval/approval_detail.html", user=g.user, approval=approval)


@app.route('/sql/approval/exec/<id>.html', methods=['GET'])
@auth(['开发', '测试', '运维'])
def approval_exec(id):
    approval = sql_approval_service.get_by_id(id)

    msg = None

    if getattr(approval, 'status') != 1:
        msg = '只有状态为审核通过才能更新为已执行'
    if getattr(approval, 'executor') != g.user['username']:
        msg = '你不是执行人，不能执行该操作'
    if not hasattr(approval, 'db_name'):
        msg = '请指定执行库'

    db_info = db_info_service.query_by_name(getattr(approval, 'db_name'))
    if db_info:
        exec_result = exec_sql(getattr(db_info, 'db_url'), getattr(db_info, 'username'), getattr(db_info, 'password'),
                               getattr(approval, 'sql'), g.sid)
        if type(exec_result) == str:
            msg = exec_result
    else:
        msg = '执行库不存在，请联系管理员'

    if msg:
        return render_template("/sqlapproval/approval_detail.html", user=g.user, approval=approval, msg=msg)

    setattr(approval, 'status', 3)

    sql_approval_service.update(approval)

    promoter = role_service.query_list({'username': getattr(approval, 'promoter')})[0]
    approver = role_service.query_list({'username': getattr(approval, 'approver')})[0]

    subject = '【线上SQL执行结果反馈】%s' % getattr(approval, 'title')
    body = '''
            发起人：%s

            线上SQL执行原因：
                %s

            执行SQL脚本为：
                %s
            
            执行结果为:
                %s

            已被 %s 执行上线，请验证结果
            ''' % (getattr(approval, 'promoter'), getattr(approval, 'cause'), getattr(approval, 'sql'),
                   exec_result[0], getattr(approval, 'executor'))
    send(subject, body, [getattr(promoter, 'email'), getattr(approver, 'email')], ['yunzaocenter@3songshu.com'])
    print(body)

    return redirect('/sql/approval/list.html')


@app.route('/sql/approval/explain/<id>.html', methods=['GET'])
@auth(['开发', '测试', '运维'])
def sql_explain(id):
    approval = sql_approval_service.get_by_id(id)
    if not hasattr(approval, 'db_name'):
        return json.dumps({'errMsg': '请指定执行库'}, ensure_ascii=False)

    db_info = db_info_service.query_by_name(getattr(approval, 'db_name'))
    if not db_info:
        return json.dumps({'errMsg': '数据库不存在，请联系管理员'}, ensure_ascii=False)
    result = explain(getattr(db_info, 'db_url'), getattr(db_info, 'username'), getattr(db_info, 'password'),
                     getattr(approval, 'sql'))

    return json.dumps({'data': result}, ensure_ascii=False)


@app.route('/db/list.html', methods=['GET'])
@auth(['管理员'])
def db_info_list():
    query = {}
    page = {}
    db_name = request.args.get('db_name')
    current_page = request.args.get('current')
    if db_name:
        query['db_name'] = db_name
    if current_page:
        page['current_page'] = current_page

    infos = db_info_service.query_list(query, page)

    return render_template("/sqlapproval/db_list.html", user=g.user, infos=infos, query=query, page=page)


@app.route('/db/add.html', methods=['GET'])
@auth(['管理员'])
def to_db_add():
    return render_template('sqlapproval/db_add.html', user=g.user, info={})


@app.route('/db/add.html', methods=['POST'])
@auth(['管理员'])
def db_add():
    info = create_model(DbInfo, request.form.to_dict())
    setattr(info, 'password', encrypt(getattr(info, 'password')))
    db_info_service.add(info)
    return redirect('/db/list.html')


@app.route('/db/del/<id>.html')
@auth(['管理员'])
def del_db(id):
    db_info_service.del_by_id(id)
    return redirect('/db/list.html')


