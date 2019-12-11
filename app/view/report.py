from .login import *
import json

task_log_service = TaskLogService()
sql_approval_service = SqlApprovalService()


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


@app.route("/report/sql/db", methods=['GET'])
def sql_by_db():
    result = sql_approval_service.group_by_db()
    return json.dumps(result, ensure_ascii=False)


@app.route("/report/sql/promoter", methods=['GET'])
def sql_by_promoter():
    result = sql_approval_service.group_by_promoter()
    return json.dumps(result, ensure_ascii=False)
