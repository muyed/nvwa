from .login import *

task_log_service = TaskLogService()


@app.route("/report/deploy/daily", methods=['GET'])
def deploy_daily():
    pass
