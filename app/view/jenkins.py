from .login import *
import jenkins


sys_config_service = SysConfigService()


def get_jk():
    jenkins_url = sys_config_service.get_value_by_key('jenkins_url')
    jenkins_user = sys_config_service.get_value_by_key('jenkins_user')
    jenkins_token = sys_config_service.get_value_by_key('jenkins_token')

    if not jenkins_url or not jenkins_user or not jenkins_token:
        raise Exception('not found jk config')

    return jenkins.Jenkins(jenkins_url, username=jenkins_user, password=jenkins_token)


@app.route('/jenkins/manage.html', methods=['GET'])
@auth(['管理员'])
def jenkins_manage_page():
    jenkins_url = sys_config_service.get_value_by_key('jenkins_url')
    jenkins_user = sys_config_service.get_value_by_key('jenkins_user')
    jenkins_token = sys_config_service.get_value_by_key('jenkins_token')
    return render_template('jenkins/jenkins_manage.html', user=g.user, jenkins_url=jenkins_url,
                           jenkins_token=jenkins_token, jenkins_user=jenkins_user)


@app.route('/jenkins/manage.html', methods=['POST'])
@auth(['管理员'])
def jenkins_manage():
    sys_config_service.add_or_update('jenkins_url', request.form.to_dict()['jenkinsUrl'])
    sys_config_service.add_or_update('jenkins_user', request.form.to_dict()['jenkinsUser'])
    sys_config_service.add_or_update('jenkins_token', request.form.to_dict()['jenkinsToken'])
    return redirect('/jenkins/manage.html')


@app.route('/jenkins/testcon', methods=['GET'])
@auth(['管理员'])
def jenkins_test_con():

    jenkins_url = request.args.get('jenkinsUrl')
    jenkins_user = request.args.get('jenkinsUser')
    jenkins_token = request.args.get('jenkinsToken')

    msg = None

    if not jenkins_url:
        msg = 'not found jenkins_url'

    if not jenkins_user:
        msg = 'not found jenkins_user'

    if not jenkins_token:
        msg = 'not found jenkins_token'

    if not msg:
        jk = jenkins.Jenkins(jenkins_url, username=jenkins_user, password=jenkins_token)
        try:
            jk.get_whoami()
            msg = 'connect successful'
        except Exception as e:
            msg = 'connect fail, e:' + str(e)

    return render_template('jenkins/jenkins_manage.html', user=g.user, jenkins_url=jenkins_url,
                           jenkins_user=jenkins_user, jenkins_token=jenkins_token, msg=msg)

