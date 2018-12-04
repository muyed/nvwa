from .login import *


@app.route("/index.html", methods=['GET'])
@app.route("/", methods=['GET'])
@auth(['管理员', '开发', '测试', '运维'])
def index():
    return render_template('index.html', user=g.user)

