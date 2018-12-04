from .login import *
import gitlab
import json


sys_config_service = SysConfigService()
task_service = TaskService()
project_config_service = ProjectConfigService()


def __get_gl__():
    gitlab_url = sys_config_service.get_value_by_key('gitlab_url')
    gitlab_token = sys_config_service.get_value_by_key('gitlab_token')
    return gitlab.Gitlab(gitlab_url, private_token=gitlab_token, api_version=4)


@app.route('/gitlab/manage.html', methods=['GET'])
@auth(['管理员'])
def gitlab_manage_page():
    gitlab_url = sys_config_service.get_value_by_key('gitlab_url')
    gitlab_token = sys_config_service.get_value_by_key('gitlab_token')
    return render_template('gitlab/gitlab_manage.html', user=g.user, gitlab_url=gitlab_url, gitlab_token=gitlab_token)


@app.route('/gitlab/manage.html', methods=['POST'])
@auth(['管理员'])
def gitlab_manage():
    sys_config_service.add_or_update('gitlab_url', request.form.to_dict()['gitlabUrl'])
    sys_config_service.add_or_update('gitlab_token', request.form.to_dict()['gitlabToken'])
    return redirect('/gitlab/manage.html')


@app.route('/gitlab/testcon', methods=['GET'])
@auth(['管理员'])
def gitlab_test_con():

    gitlab_url = request.args.get('gitlabUrl')
    gitlab_token = request.args.get('gitlabToken')

    msg = None

    if not gitlab_url:
        msg = 'not found gitlab_url'

    if not gitlab_token:
        msg = 'not found gitlab_token'

    if not msg:
        try:
            with __get_gl__() as gl:
                gl.projects.list()
                msg = 'connect successful'
        except Exception as e:
            msg = 'connect fail, e:' + str(e)

    return render_template('gitlab/gitlab_manage.html', user=g.user, gitlab_url=gitlab_url, gitlab_token=gitlab_token,
                           msg=msg)


@app.route('/gitlab/projects/<group_id>', methods=['GET'])
@auth(['开发'])
def projects_by_group(group_id):
    with __get_gl__() as gl:
        return json.dumps([{'id': p.id, 'name': p.name} for p in gl.projects.list(all=True) if p.namespace['id'] == int(group_id)])


@app.route('/gitlab/branch/exist/<branch_name>/<project_id>')
@auth(['开发'])
def exist_branch_view(branch_name, project_id):
    return json.dumps(available_branch(branch_name, project_id))


@app.route('/gitlab/project/config/list.html', methods=['GET'])
@auth(['管理员'])
def project_config_list():
    query = {}
    page = {}
    project_name = request.args.get('project_name')
    current_page = request.args.get('current')
    if project_name:
        query['project_name'] = project_name
    if current_page:
        page['current'] = int(current_page)
    configs = project_config_service.query_list(query, page)
    return render_template('gitlab/project_config_list.html', user=g.user, configs=configs, query=query, page=page)


@app.route('/gitlab/project/config/add.html', methods=['GET'])
@auth(['管理员'])
def to_project_config_add():
    groups = get_groups()
    return render_template('gitlab/add_project_config.html', user=g.user, groups=groups)


@app.route('/gitlab/project/config/add.html', methods=['POST'])
@auth(['管理员'])
def project_config_add():
    project_config = create_model(ProjectConfig)
    project_config.project_id = request.form.to_dict()['project_id']
    project_config.test_job = request.form.to_dict()['testJob']
    project_config.pre_job = request.form.to_dict()['preJob']
    project_config.pro_job = request.form.to_dict()['proJob']
    project_config.project_name = project_by_id(project_config.project_id).name_with_namespace

    if len(project_config_service.query_list({'project_id': project_config.project_id})) > 0:
        raise Exception('项目已经存在了')

    project_config_service.add(project_config)
    return redirect('/gitlab/project/config/list.html')


@app.route('/gitlab/project/config/edit/<id>.html', methods=['GET'])
@auth(['管理员'])
def to_project_config_edit(id):
    project_config = project_config_service.get_by_id(id)
    if not project_config:
        raise Exception('not found config: ' + id)
    return render_template('/gitlab/edit_project_config.html', user=g.user, config=project_config)


@app.route('/gitlab/project/config/edit.html', methods=['POST'])
@auth(['管理员'])
def project_config_edit():
    d = request.form.to_dict()
    d['id'] = int(d['id'])
    project_config = create_model(ProjectConfig, d)
    project_config_service.update(project_config)
    return redirect('/gitlab/project/config/list.html')


@app.route('/gitlab/project/config/delete/<id>.html', methods=['GET'])
def del_project_config(id):
    project_config_service.del_by_id(id)
    return redirect('/gitlab/project/config/list.html')


def get_groups():
    with __get_gl__() as gl:
        return gl.groups.list(all=True)


def available_branch(branch_name, project_id):
    if task_service.query_list({'project_branch': branch_name, 'project_id': project_id}):
        return False

    with __get_gl__() as gl:
        p = gl.projects.get(project_id)
        if not p:
            return False
        return branch_name not in [b.name for b in p.branches.list(all=True)]


def create_branch(project_id, branch_name, ref='master'):
    with __get_gl__() as gl:
        p = gl.projects.get(project_id)
        if not p:
            raise Exception('project not exist')

        return p.branches.create({'branch': branch_name, 'ref': ref})


def project_by_id(project_id):
    with __get_gl__() as gl:
        return gl.projects.get(project_id)
