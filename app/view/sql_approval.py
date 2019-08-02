from .login import *

sql_approval_service = SqlApprovalService()


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
    return render_template('sqlapproval/approval_add.html', user=g.user, approval={})


@app.route('/sql/approval/add.html', methods=['POST'])
@auth(['开发', '测试', '运维'])
def approval_add():
    approval = create_model(SqlApproval, request.form.to_dict())

    msg = None
    if not getattr(approval, 'title', None) or not getattr(approval, 'approver', None) \
            or not getattr(approval, 'sql', None) or not getattr(approval, 'cause', None):
        msg = '标题、SQL脚本、发起原因、审批人必填，请填写完整'
    if msg:
        return render_template('sqlapproval/approval_add.html', user=g.user, approval=approval, msg=msg)

    setattr(approval, 'status', 0)
    setattr(approval, 'promoter', g.user['username'])

    sql_approval_service.add(approval)

    return redirect('/sql/approval/list.html')


@app.route('/sql/approval/update/<id>.html', methods=['GET'])
@auth(['开发', '测试', '运维'])
def to_approval_update(id):
    approval = sql_approval_service.get_by_id(id)
    return render_template('sqlapproval/approval_update.html', user=g.user, approval=approval)


@app.route('/sql/approval/update.html', methods=['POST'])
@auth(['开发', '测试', '运维'])
def approval_update():
    approval = create_model(SqlApproval, request.form.to_dict())

    msg = None
    if not getattr(approval, 'title', None) or not getattr(approval, 'approver', None) \
            or not getattr(approval, 'sql', None) or not getattr(approval, 'cause', None):
        msg = '标题、SQL脚本、发起原因、审批人必填，请填写完整'

    if msg:
        return render_template('sqlapproval/approval_update.html', user=g.user, approval=approval, msg=msg)

    old = sql_approval_service.get_by_id(getattr(approval, 'id'))

    if getattr(old, 'status') != 0 or getattr(old, 'status') != 2:
        msg = '只有状态为待审核和审核未通过可以再次编辑'
    if msg:
        return render_template('sqlapproval/approval_update.html', user=g.user, approval=approval, msg=msg)


    setattr(approval, 'status', 0)
    setattr(approval, 'promoter', g.user['username'])

    sql_approval_service.update(approval)
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

    return render_template("/sqlapproval/approval.html", user=g.user, approval=approval)


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

    if msg:
        return render_template("/sqlapproval/approval.html", user=g.user, approval=approval, msg=msg)

    if status == 2:
        delattr(approval, 'executor')

    sql_approval_service.update(param)

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
        msg = '你不是执行人，不知执行该操作'

    if msg:
        return render_template("/sqlapproval/approval_detail.html", user=g.user, approval=approval, msg=msg)

    setattr(approval, 'status', 3)

    sql_approval_service.update(approval)

    return redirect('/sql/approval/list.html')


