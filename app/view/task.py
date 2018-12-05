from .login import *
import app.view.gitlab as gitlab
import app.view.jenkins as jenkins
import json
import requests


task_service = TaskService()
task_log_service = TaskLogService()
rel_user_task_service = RelUserTaskService()
project_config_service = ProjectConfigService()
sys_config_service = SysConfigService()


@app.route('/task/current.html', methods=['GET'])
@auth(['开发', '测试', '运维'])
def current_task():
    page = {'size': 9}

    current_page = request.args.get('current')
    if current_page:
        page['current'] = int(current_page)

    tasks = task_service.my_task([0, 1, 2, 3, 4, 5, 6], page)

    for task in tasks:
        developers = rel_user_task_service.query_list({'task_id': task.id, 'role': '开发'})
        testers = rel_user_task_service.query_list({'task_id': task.id, 'role': '测试'})
        logs = task_log_service.query_list({'task_id': task.id})
        setattr(task, 'logs', logs)
        setattr(task, 'test_count', 0)
        setattr(task, 'preview_count', 0)
        setattr(task, 'online_count', 0)
        if logs:
            for log in logs:
                if log.task_status == 1:
                    setattr(task, 'test_count', getattr(task, 'test_count') + 1)
                    if not hasattr(task, 'desc'):
                        setattr(task, 'desc', log.log)
                if log.task_status == 4:
                    setattr(task, 'preview_count', getattr(task, 'preview_count') + 1)
                if log.task_status == 6:
                    setattr(task, 'online_count', getattr(task, 'online_count') + 1)
                log.task_status = config.TASK_STATUS[log.task_status]

        if not hasattr(task, 'desc'):
            setattr(task, 'desc', task.discription)

        setattr(task, 'developers', developers)
        setattr(task, 'testers', testers)
        task.status = config.TASK_STATUS[task.status]

        task.desc = task.desc.replace('\n', '<br>')
        if task.properties:
            task.properties = task.properties.replace('\n', '<br>')
        if task.sql_script:
            task.sql_script = task.sql_script.replace('\n', '<br>')

    return render_template('task/current_task.html', user=g.user, tasks=tasks, page=page)


@app.route('/task/hist.html', methods=['GET'])
@auth(['开发', '测试', '运维'])
def my_hist_task():
    page = {'size': 9}

    current_page = request.args.get('current')
    if current_page:
        page['current'] = int(current_page)

    tasks = task_service.my_task([7], page)

    for task in tasks:
        developers = rel_user_task_service.query_list({'task_id': task.id, 'role': '开发'})
        testers = rel_user_task_service.query_list({'task_id': task.id, 'role': '测试'})
        logs = task_log_service.query_list({'task_id': task.id})
        setattr(task, 'logs', logs)
        setattr(task, 'test_count', 0)
        setattr(task, 'preview_count', 0)
        setattr(task, 'online_count', 0)
        if logs:
            for log in logs:
                if log.task_status == 1:
                    setattr(task, 'test_count', getattr(task, 'test_count') + 1)
                    if not hasattr(task, 'desc'):
                        setattr(task, 'desc', log.log)
                if log.task_status == 4:
                    setattr(task, 'preview_count', getattr(task, 'preview_count') + 1)
                if log.task_status == 6:
                    setattr(task, 'online_count', getattr(task, 'online_count') + 1)
                log.task_status = config.TASK_STATUS[log.task_status]

        if not hasattr(task, 'desc'):
            setattr(task, 'desc', task.discription)

        setattr(task, 'developers', developers)
        setattr(task, 'testers', testers)
        task.status = config.TASK_STATUS[task.status]

        task.desc = task.desc.replace('\n', '<br>')
        if task.properties:
            task.properties = task.properties.replace('\n', '<br>')
        if task.sql_script:
            task.sql_script = task.sql_script.replace('\n', '<br>')

    return render_template('task/hist_task.html', user=g.user, tasks=tasks, page=page)


@app.route('/task/query.html', methods=['GET'])
@auth(['管理员'])
def task_query():
    page = {'size': 9}
    current_page = request.args.get('current')
    if current_page:
        page['current'] = int(current_page)

    query = request.args.to_dict()
    for k in list(query):
        if not query[k]:
            query.pop(k)

    tasks = task_service.query_list(query, page)

    for task in tasks:
        developers = rel_user_task_service.query_list({'task_id': task.id, 'role': '开发'})
        testers = rel_user_task_service.query_list({'task_id': task.id, 'role': '测试'})
        logs = task_log_service.query_list({'task_id': task.id})
        setattr(task, 'logs', logs)
        setattr(task, 'test_count', 0)
        setattr(task, 'preview_count', 0)
        setattr(task, 'online_count', 0)
        if logs:
            for log in logs:
                if log.task_status == 1:
                    setattr(task, 'test_count', getattr(task, 'test_count') + 1)
                    if not hasattr(task, 'desc'):
                        setattr(task, 'desc', log.log)
                if log.task_status == 4:
                    setattr(task, 'preview_count', getattr(task, 'preview_count') + 1)
                if log.task_status == 6:
                    setattr(task, 'online_count', getattr(task, 'online_count') + 1)
                log.task_status = config.TASK_STATUS[log.task_status]

        if not hasattr(task, 'desc'):
            setattr(task, 'desc', task.discription)

        setattr(task, 'developers', developers)
        setattr(task, 'testers', testers)
        task.status = config.TASK_STATUS[task.status]

        task.desc = task.desc.replace('\n', '<br>')
        if task.properties:
            task.properties = task.properties.replace('\n', '<br>')
        if task.sql_script:
            task.sql_script = task.sql_script.replace('\n', '<br>')

    return render_template('task/query_task.html', user=g.user, tasks=tasks, page=page, query=query)


@app.route('/task/add.html', methods=['GET'])
@auth(['开发'])
def to_add_task():
    task = create_model(Task)
    setattr(task, 'groups', gitlab.get_groups())
    setattr(task, 'developers', role_service.query_list(query={'role': '开发'}, page={'size': 1000}))
    setattr(task, 'testers', role_service.query_list(query={'role': '测试'}, page={'size': 1000}))
    setattr(task, 'branch_suf', '_' + datetime.datetime.now().strftime('%Y%m%d'))
    return render_template('task/add_task.html', user=g.user, task=task)


@app.route('/task/add.html', methods=['POST'])
@auth(['开发'])
def add_task():
    task = request.form.to_dict()
    developers = task['developers'].split(',')
    testers = task['testers'].split(',')
    if not developers or not testers:
        raise Exception('developers or testers is must')

    task = create_model(Task, task)

    if not gitlab.available_branch(task.project_branch, task.project_id):
        raise Exception('branch is exist')

    project = gitlab.project_by_id(task.project_id)

    task.project_name = project.name_with_namespace
    task.status = 0
    task_service.add(task)

    task_log = create_model(TaskLog)
    task_log.task_id = task.id
    task_log.log = '新建任务'
    task_log.task_status = 0
    task_log.operator = g.user['username']
    task_log_service.add(task_log)

    for username in testers:
        rel_user_task = create_model(RelUserTask)
        rel_user_task.task_id = task.id
        rel_user_task.username = username
        rel_user_task.role = '测试'
        rel_user_task_service.add(rel_user_task)

    for username in developers:
        rel_user_task = create_model(RelUserTask)
        rel_user_task.task_id = task.id
        rel_user_task.username = username
        rel_user_task.role = '开发'
        rel_user_task_service.add(rel_user_task)

    gitlab.create_branch(task.project_id, task.project_branch)

    return redirect('/task/current.html')


@app.route('/task/edit/<id>.html', methods=['GET'])
@auth(['开发'])
def to_edit_task(id):
    task = task_service.get_by_id(id)
    s_developers = [v.username for v in rel_user_task_service.query_list({'task_id': id, 'role': '开发'}, {'size': 1000})]
    s_testers = [v.username for v in rel_user_task_service.query_list({'task_id': id, 'role': '测试'}, {'size': 1000})]
    setattr(task, 'developers', role_service.query_list({'role': '开发'}, {'size': 1000}))
    setattr(task, 's_developers', s_developers)
    setattr(task, 'testers', role_service.query_list({'role': '测试'}, {'size': 1000}))
    setattr(task, 's_testers', s_testers)

    return render_template('task/edit_task.html', user=g.user, task=task)


@app.route('/task/edit.html', methods=['POST'])
@auth(['开发'])
def edit_task():
    task = request.form.to_dict()
    developers = task['developers'].split(',')
    testers = task['testers'].split(',')
    if not developers or not testers:
        raise Exception('developers or testers is must')

    task = create_model(Task, task)

    task_service.update(task)

    old_developers = rel_user_task_service.query_list({'task_id': task.id, 'role': '开发'}, {'size': 1000})
    for old in old_developers:
        if old.username in developers:
            developers.remove(old.username)
        else:
            rel_user_task_service.del_by_id(old.id)

    old_testers = rel_user_task_service.query_list({'task_id': task.id, 'role': '测试'}, {'size': 1000})
    for old in old_testers:
        if old.username in testers:
            testers.remove(old.username)
        else:
            rel_user_task_service.del_by_id(old.id)

    for username in testers:
        rel_user_task = create_model(RelUserTask)
        rel_user_task.task_id = task.id
        rel_user_task.username = username
        rel_user_task.role = '测试'
        rel_user_task_service.add(rel_user_task)

    for username in developers:
        rel_user_task = create_model(RelUserTask)
        rel_user_task.task_id = task.id
        rel_user_task.username = username
        rel_user_task.role = '开发'
        rel_user_task_service.add(rel_user_task)

    return redirect('/task/current.html')


@app.route('/task/submittest.html', methods=['POST'])
@auth(['开发'])
def submit_test():
    params = request.form.to_dict()

    task = task_service.get_by_id(params['id'])
    task.status = 1
    task.project_tag = params['tag']
    task_service.update(task)

    task_log = create_model(TaskLog)
    task_log.task_id = task.id
    task_log.log = params['desc']
    task_log.task_status = 1
    task_log.operator = g.user['username']
    task_log_service.add(task_log)

    project = gitlab.project_by_id(task.project_id)
    try:
        project.tags.create({'tag_name': task.project_tag, 'ref': task.project_branch})
    except Exception as e:
        return json.dumps({'ok': False, 'msg': str(e)})

    return json.dumps({'ok': True})


@app.route('/task/test/deploy.html', methods=['POST'])
@auth(['测试', '开发'])
def test_deploy():
    task = task_service.get_by_id(int(request.form.to_dict()['id']))
    project_config = project_config_service.get_by_project(task.project_id)
    if not project_config:
        return json.dumps({'ok': False, 'msg': '项目还未配置部署配置，请联系管理员添加'})

    project = gitlab.project_by_id(task.project_id)
    clean = request.form.to_dict()['cleanBranch'] == 'true'
    test_branch_name = 'unified-test'
    test_branch = None

    if clean:
        try:
            project.branches.delete(test_branch_name)
        except Exception as e:
            if e.response_code != 404:
                return json.dumps({'ok': False, 'msg': str(e)})

    try:
        test_branch = project.branches.get(test_branch_name)
    except Exception as e:
        if e.response_code != 404:
            return json.dumps({'ok': False, 'msg': str(e)})

    if not test_branch:
        project.branches.create({'branch': test_branch_name, 'ref': 'master'})

    try:
        dev_branch = project.branches.create({'branch': task.project_branch + '_' + task.project_tag,
                                              'ref': task.project_tag})
    except Exception as e:
        return json.dumps({'ok': False, 'msg': str(e)})

    try:
        mr = project.mergerequests.create({'source_branch': task.project_branch + '_' + task.project_tag,
                                           'target_branch': test_branch_name,
                                           'title': '[nvwa] ' + task.project_branch + ' merge to unified-test',
                                           'labels': []})
        if mr.changes()['changes_count']:
            mr.merge()
    except Exception as e:
        print(str(e))
        return json.dumps({'ok': False, 'msg': 'merge代码失败，请联系开发解决冲突后再重试'})
    finally:
        dev_branch.delete()
        mr.delete()

    try:
        jk = jenkins.get_jk()
        jk.build_job(project_config.test_job, {'branch': test_branch_name})
    except Exception as e:
        return json.dumps({'ok': False, 'msg': str(e)})

    task.status = 2
    task.last_run_job = project_config.test_job
    task_service.update(task)

    task_log = create_model(TaskLog)
    task_log.task_id = task.id
    task_log.log = '发布测试'
    task_log.task_status = 2
    task_log.operator = g.user['username']
    task_log_service.add(task_log)

    return json.dumps({'ok': True})


@app.route('/task/<id>/deploy/console.html', methods=['GET'])
@auth(['开发', '测试', '运维'])
def last_deploy_console(id):
    try:
        task = task_service.get_by_id(id)
        if not task.last_run_job:
            return json.dumps({'ok': True, 'console': '没有发布信息'})
        jk = jenkins.get_jk()
        num = jk.get_job_info(task.last_run_job)['lastBuild']['number']

        url = sys_config_service.get_value_by_key('jenkins_url') + '/job/' + task.last_run_job + "/" + str(num) + '/logText/progressiveHtml'

        req = requests.Request(method='get', url=url)
        resp = jk.jenkins_request(req)
        result = resp.text.replace('new Ajax.Request', 'reqAjax')

        return json.dumps({'ok': True, 'console': result})
    except Exception as e:
        return json.dumps({'ok': False, 'msg': str(e)})


@app.route('/task/<id>/test/pass.html', methods=['POST'])
@auth(['测试'])
def pass_test(id):
    task = task_service.get_by_id(id)
    task.status = 3
    task_service.update(task)

    task_log = create_model(TaskLog)
    task_log.task_id = task.id
    task_log.log = '测试通过'
    task_log.task_status = 3
    task_log.operator = g.user['username']
    task_log_service.add(task_log)

    return json.dumps({'ok': True})


@app.route('/task/pre/deploy.html', methods=['POST'])
@auth(['运维', '测试', '开发'])
def pre_deploy():
    task = task_service.get_by_id(int(request.form.to_dict()['id']))
    project_config = project_config_service.get_by_project(task.project_id)
    if not project_config:
        return json.dumps({'ok': False, 'msg': '项目还未配置部署配置，请联系管理员添加'})

    project = gitlab.project_by_id(task.project_id)

    # 发布预发时将master merge到当前分支上（开发过程中上线的代码merge过来）
    try:
        mr = project.mergerequests.create({'source_branch': 'master', 'target_branch': task.project_branch,
                                           'title': '[nvwa]pre merge', 'labels': []})
        if mr.changes()['changes_count']:
            mr.merge()
    except Exception as e:
        print(str(e))
        return json.dumps({'ok': False, 'msg': 'merge代码失败，请联系开发解决冲突后再重试'})
    finally:
        mr.delete()

    try:
        jk = jenkins.get_jk()
        jk.build_job(project_config.pre_job, {'branch': task.project_branch})
    except Exception as e:
        return json.dumps({'ok': False, 'msg': str(e)})

    task.status = 4
    task.last_run_job = project_config.pre_job
    task_service.update(task)

    task_log = create_model(TaskLog)
    task_log.task_id = task.id
    task_log.log = '发布预发'
    task_log.task_status = 4
    task_log.operator = g.user['username']
    task_log_service.add(task_log)

    return json.dumps({'ok': True})


@app.route('/task/<id>/pre/pass.html', methods=['POST'])
@auth(['测试'])
def pass_pre(id):
    task = task_service.get_by_id(id)
    task.status = 5
    task_service.update(task)

    task_log = create_model(TaskLog)
    task_log.task_id = task.id
    task_log.log = '预发通过'
    task_log.task_status = 5
    task_log.operator = g.user['username']
    task_log_service.add(task_log)

    return json.dumps({'ok': True})


@app.route('/task/prod/deploy.html', methods=['POST'])
@auth(['运维'])
def prod_deploy():
    task = task_service.get_by_id(int(request.form.to_dict()['id']))
    project_config = project_config_service.get_by_project(task.project_id)
    if not project_config:
        return json.dumps({'ok': False, 'msg': '项目还未配置部署配置，请联系管理员添加'})

    project = gitlab.project_by_id(task.project_id)

    # 发布线上时将master merge到当前分支上（开发过程中上线的代码merge过来）
    try:
        mr = project.mergerequests.create({'source_branch': 'master', 'target_branch': task.project_branch,
                                           'title': '[nvwa]prod merge', 'labels': []})
        if mr.changes()['changes_count']:
            mr.merge()
    except Exception as e:
        print(str(e))
        return json.dumps({'ok': False, 'msg': 'merge代码失败，请联系开发解决冲突后再重试'})
    finally:
        mr.delete()

    try:
        jk = jenkins.get_jk()
        jk.build_job(project_config.pro_job, {'branch': task.project_branch})
    except Exception as e:
        return json.dumps({'ok': False, 'msg': str(e)})

    task.status = 6
    task.last_run_job = project_config.pro_job
    task_service.update(task)

    task_log = create_model(TaskLog)
    task_log.task_id = task.id
    task_log.log = '发布线上'
    task_log.task_status = 6
    task_log.operator = g.user['username']
    task_log_service.add(task_log)

    return json.dumps({'ok': True})


@app.route('/task/pipeline/input', methods=['post'])
@auth(['开发', '测试', '运维'])
def pipeline_input():
    try:
        jk = jenkins.get_jk()
        url = request.form.to_dict()['url']
        req = requests.Request(method='post', url=url)
        resp = jk.jenkins_request(req)
        return json.dumps({'ok': True, 'result': resp.text})
    except Exception as e:
        return json.dumps({'ok': False, 'errMsg': str(e)})


@app.route('/task/<id>/merge/master', methods=['post'])
@auth(['开发'])
def merge_master(id):
    task = task_service.get_by_id(id)
    project_config = project_config_service.get_by_project(task.project_id)
    if not project_config:
        return json.dumps({'ok': False, 'msg': '项目还未配置部署配置，请联系管理员添加'})

    project = gitlab.project_by_id(task.project_id)

    try:
        mr = project.mergerequests.create({'target_branch': 'master', 'source_branch': task.project_branch,
                                           'title': '[nvwa]prod merge', 'labels': []})
        if mr.changes()['changes_count']:
            mr.merge()
    except Exception as e:
        print(str(e))
        return json.dumps({'ok': False, 'msg': 'merge代码失败，请联系开发解决冲突后再重试'})
    finally:
        mr.delete()

    task.status = 7
    task.last_run_job = project_config.pre_job
    task_service.update(task)

    task_log = create_model(TaskLog)
    task_log.task_id = task.id
    task_log.log = 'merge master'
    task_log.task_status = 7
    task_log.operator = g.user['username']
    task_log_service.add(task_log)

    return json.dumps({'ok': True})

