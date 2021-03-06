from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import *
import datetime


Base = declarative_base()


def create_model(cls, d=None):
    model = cls()
    model.gmt_create = datetime.datetime.now()
    model.row_status = 0
    model.row_version = 0
    if d:
        for k in d.keys():
            if hasattr(model, k):
                setattr(model, k, d[k])
    return model


class BaseModel(object):
    id = Column(BigInteger(), primary_key=True, autoincrement=True)
    gmt_create = Column(DateTime())
    gmt_modified = Column(DateTime())
    row_status = Column(Integer())
    row_version = Column(Integer())

    def to_dict(self, removal_none=False):
        d = self.__dict__
        r = dict()
        for k in list(d):
            if removal_none and d[k] is None:
                continue
            if k != '_sa_instance_state':
                r[k] = d[k]
        return r


class Role(Base, BaseModel):
    __tablename__ = 'role'
    username = Column(String(50))
    role = Column(String(50))
    is_manager = Column(Integer())
    is_owner = Column(Integer())
    email = Column(String())


class SysConfig(Base, BaseModel):
    __tablename__ = 'sys_config'
    key = Column(String(50))
    value = Column(String(1024))


class Task(Base, BaseModel):
    __tablename__ = 'task'
    title = Column(String(256))
    project_id = Column(Integer())
    project_name = Column(String(256))
    project_branch = Column(String(128))
    project_tag = Column(String(128))
    properties = Column(Text())
    sql_script = Column(Text())
    sql_files = Column(String(2048))
    status = Column(Integer())
    discription = Column(String(2048))
    last_run_job = Column(String(256))


class TaskLog(Base, BaseModel):
    __tablename__ = 'task_log'
    task_id = Column(BigInteger())
    log = Column(String(2048))
    operator = Column(String(50))
    task_status = Column(Integer())


class RelUserTask(Base, BaseModel):
    __tablename__ = 'rel_user_task'
    task_id = Column(BigInteger())
    username = Column(String(50))
    role = Column(String(50))


class ProjectConfig(Base, BaseModel):
    __tablename__ = 'project_config'
    project_id = Column(Integer())
    project_name = Column(String(128))
    test_job = Column(String(128))
    pre_job = Column(String(128))
    pro_job = Column(String(128))
    is_seal = Column(Integer())


class AppInfo(Base, BaseModel):
    __tablename__ = 'app_info'
    app_name = Column(String(128))
    app_desc = Column(String(512))
    url = Column(String(512))
    env = Column(Integer())


class SqlApproval(Base, BaseModel):
    __tablename__ = 'sql_approval'
    title = Column(String(256))
    sql = Column(Text())
    cause = Column(String(1024))
    promoter = Column(String(45))
    approver = Column(String(45))
    executor = Column(String(45))
    status = Column(Integer())
    approval_opinion = Column(String(1024))
    db_name = Column(String(45))


class DbInfo(Base, BaseModel):
    __tablename__ = 'db_info'
    db_name = Column(String(45))
    db_url = Column(String(128))
    username = Column(String(45))
    password = Column(String(1024))
