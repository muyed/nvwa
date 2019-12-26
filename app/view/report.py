from .login import *
from ..util import db_exec_util
from flask import Response
import json

task_log_service = TaskLogService()
sql_approval_service = SqlApprovalService()
db_info_server = DbInfoService()


@app.route("/report/deploy/daily", methods=['GET'])
def deploy_daily():
    result = task_log_service.group_daily()
    return Response(json.dumps(result, ensure_ascii=False), mimetype='application/json')


@app.route("/report/deploy/pre", methods=['GET'])
def deploy_pre():
    result = task_log_service.group_pre()
    return Response(json.dumps(result, ensure_ascii=False), mimetype='application/json')


@app.route("/report/deploy/prod", methods=['GET'])
def deploy_prod():
    result = task_log_service.group_prod()
    return Response(json.dumps(result, ensure_ascii=False), mimetype='application/json')


@app.route("/report/sql/db", methods=['GET'])
def sql_by_db():
    result = sql_approval_service.group_by_db()
    return Response(json.dumps(result, ensure_ascii=False), mimetype='application/json')


@app.route("/report/sql/promoter", methods=['GET'])
def sql_by_promoter():
    result = sql_approval_service.group_by_promoter()
    return Response(json.dumps(result, ensure_ascii=False), mimetype='application/json')


@app.route("/report/db/information", methods=['GET'])
def db_information():
    infos = db_info_server.query_list(query={}, page={'pageSize': 1000})
    params = [[getattr(i, 'db_url'), getattr(i, 'username'), getattr(i, 'password'), getattr(i, 'db_name')]
              for i in infos]
    result = db_exec_util.information(params)
    return Response(json.dumps(result, ensure_ascii=False), mimetype='application/json')



