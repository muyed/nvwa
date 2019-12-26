from .login import *


app_info_service = AppInfoService()


@app.route("/index.html", methods=['GET'])
@app.route("/", methods=['GET'])
@auth(['管理员', '开发', '测试', '运维'])
def index():
    apps = app_info_service.query_list({}, {'size': 2000})
    return render_template('index.html', user=g.user, apps=apps)

