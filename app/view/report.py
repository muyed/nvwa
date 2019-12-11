from .login import *
import json

task_log_service = TaskLogService()


@app.route("/report/deploy/daily", methods=['GET'])
def deploy_daily():
    result = task_log_service.group_daily()
    return json.dumps(result, ensure_ascii=False)


@app.route("/report/deploy/pre", methods=['GET'])
def deploy_pre():
    result = task_log_service.group_pre()
    return json.dumps(result, ensure_ascii=False)


@app.route("/report/deploy/prod", methods=['GET'])
def deploy_prod():
    result = task_log_service.group_prod()
    return json.dumps(result, ensure_ascii=False)
