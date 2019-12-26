from app import g
from .model import *
import math
import datetime


class BaseService(object):
    def __init__(self, table_cls):
        self.table_cls = table_cls

    def get_by_id(self, id):
        result = g.db.query(self.table_cls).filter_by(**{'id': id, 'row_status': 0}).one_or_none()
        if result:
            result = create_model(self.table_cls, result.to_dict(True))
        return result

    def update(self, obj):
        if not isinstance(obj, self.table_cls):
            raise Exception('update value type mismatch')
        old = self.get_by_id(obj.id)
        if not old:
            return False
        obj.row_version = getattr(old, 'row_version', 0) + 1
        obj.gmt_modified = datetime.datetime.now()
        try:
            result = g.db.query(self.table_cls).\
                filter_by(**{'id': obj.id, 'row_version': getattr(old, 'row_version', 0)}).update(obj.to_dict(True))
        except Exception as e:
            print(e)
            return False
        if not result:
            return False
        return True

    def add(self, new):
        if not isinstance(new, self.table_cls):
            raise Exception('add value type mismatch')
        g.db.add(new)
        g.db.flush()

    def query_list(self, query, page={'current': 1}):
        if 'current' not in page or page['current'] < 1:
            page['current'] = 1
        if 'size' not in page:
            page['size'] = 20

        query['row_status'] = 0

        offset = (page['current'] - 1) * page['size']

        result = g.db.query(self.table_cls).filter_by(**query).order_by('-id').offset(offset).limit(page['size'])
        if not result:
            page['total'] = 0
            return []
        page['total'] = int(math.ceil(g.db.query(self.table_cls).filter_by(**query).count() / page['size']))
        return [create_model(self.table_cls, r.to_dict(True)) for r in result]

    def del_by_id(self, id):
        if not id:
            return
        g.db.query(self.table_cls).filter_by(id=id).first().row_status = -1


class RoleService(BaseService):
    def __init__(self):
        super(RoleService, self).__init__(Role)


class SysConfigService(BaseService):
    def __init__(self):
        super(SysConfigService, self).__init__(SysConfig)

    def get_value_by_key(self, key):
        result = g.db.query(self.table_cls.value).filter_by(**{'key': key, 'row_status': 0}).one_or_none()
        if result:
            return result[0]
        return result

    def get_by_key(self, key):
        result = g.db.query(self.table_cls).filter_by(**{'key': key, 'row_status': 0}).one_or_none()
        if result:
            result = create_model(self.table_cls, result.to_dict(True))
        return result

    def add_or_update(self, key, value):
        config = self.get_by_key(key)
        if config:
            config.value = value
            self.update(config)
        else:
            config = create_model(SysConfig, {'key': key, 'value': value})
            self.add(config)


class TaskService(BaseService):
    def __init__(self):
        super(TaskService, self).__init__(Task)

    def my_task(self, status, page={'current': 1}):
        if 'current' not in page or page['current'] < 1:
            page['current'] = 1
        if 'size' not in page:
            page['size'] = 20

        username = g.user['username']
        user_task_list = g.db.query(RelUserTask).filter_by(**{'username': username, 'row_status': 0}).all()
        if not user_task_list:
            page['total'] = 0
            return []

        ids = [user_task.task_id for user_task in list(user_task_list)]
        offset = (page['current'] - 1) * page['size']

        query = {'row_status': 0}

        result = g.db.query(self.table_cls).filter(Task.id.in_(ids)).filter(Task.status.in_(status)).filter_by(**query)\
            .order_by('-id').offset(offset).limit(page['size'])

        if not result:
            page['total'] = 0
            return []
        page['total'] = int(math.ceil(g.db.query(self.table_cls).filter(Task.id.in_(ids))
                                      .filter(Task.status.in_(status)).filter_by(**query).count() / page['size']))

        return [create_model(self.table_cls, r.to_dict(True)) for r in list(result)]

    def query_list(self, query, page={'current': 1}):
        if 'current' not in page or page['current'] < 1:
            page['current'] = 1
        if 'size' not in page:
            page['size'] = 20

        ids = []
        username = ''
        if 'username' in query:
            username = query.pop('username')
            user_task_list = g.db.query(RelUserTask).filter_by(**{'username': username, 'row_status': 0}).all()
            if not user_task_list:
                page['total'] = 0
                return []
            ids = [user_task.task_id for user_task in list(user_task_list)]

        offset = (page['current'] - 1) * page['size']
        query['row_status'] = 0

        if ids:
            result = g.db.query(self.table_cls).filter(Task.id.in_(ids)).filter_by(**query).order_by('-id')\
                .offset(offset).limit(page['size'])
        else:
            result = g.db.query(self.table_cls).filter_by(**query).order_by('-id').offset(offset).limit(page['size'])

        if not result:
            page['total'] = 0
            return []

        if ids:
            page['total'] = int(math.ceil(g.db.query(self.table_cls).filter(Task.id.in_(ids))
                                          .filter_by(**query).count() / page['size']))
        else:
            page['total'] = int(math.ceil(g.db.query(self.table_cls).filter_by(**query).count() / page['size']))

        query['username'] = username
        return [create_model(self.table_cls, r.to_dict(True)) for r in list(result)]


class TaskLogService(BaseService):
    def __init__(self):
        super(TaskLogService, self).__init__(TaskLog)

    group_daily_sql = '''
        select count(tl.task_status), t.project_name 
        from task_log tl, task t 
        where t.id = tl.task_id and t.project_name != '' and tl.task_status = 2 and tl.gmt_create >= '%s'
        group by t.project_name;
    '''

    group_pre_sql = '''
        select count(tl.task_status), t.project_name 
        from task_log tl, task t 
        where t.id = tl.task_id and t.project_name != '' and tl.task_status = 4 and tl.gmt_create >= '%s'
        group by t.project_name;
    '''

    group_prod_sql = '''
        select count(tl.task_status), t.project_name 
        from task_log tl, task t
        where t.id = tl.task_id and t.project_name != '' and tl.task_status = 7 and tl.gmt_create >= '%s'
        group by t.project_name;
    '''

    def group_daily(self):
        start = datetime.date.today()
        one_day = datetime.timedelta(days=1)
        while start.weekday() != 0:
            start -= one_day
        result = g.db.execute(self.group_daily_sql % str(start)).fetchall()
        return [{'project': i[1], 'count': i[0]} for i in result]

    def group_pre(self):
        start = datetime.date.today()
        one_day = datetime.timedelta(days=1)
        while start.weekday() != 0:
            start -= one_day
        result = g.db.execute(self.group_pre_sql % str(start)).fetchall()
        return [{'project': i[1], 'count': i[0]} for i in result]

    def group_prod(self):
        start = datetime.date.today()
        one_day = datetime.timedelta(days=1)
        while start.weekday() != 0:
            start -= one_day
        result = g.db.execute(self.group_prod_sql % str(start)).fetchall()
        return [{'project': i[1], 'count': i[0]} for i in result]


class RelUserTaskService(BaseService):
    def __init__(self):
        super(RelUserTaskService, self).__init__(RelUserTask)


class ProjectConfigService(BaseService):
    def __init__(self):
        super(ProjectConfigService, self).__init__(ProjectConfig)

    def get_by_project(self, project_id):
        result = g.db.query(self.table_cls).filter_by(**{'project_id': project_id, 'row_status': 0}).one_or_none()
        if result:
            result = create_model(self.table_cls, result.to_dict(True))
        return result


class AppInfoService(BaseService):
    def __init__(self):
        super(AppInfoService, self).__init__(AppInfo)


class SqlApprovalService(BaseService):
    def __init__(self):
        super(SqlApprovalService, self).__init__(SqlApproval)

    _group_by_db_sql = '''
        select count(id), db_name from sql_approval where db_name is not null and gmt_create >= '%s' group by db_name
    '''

    _group_by_promoter_sql = '''
        select count(id), promoter from sql_approval where db_name is not null and gmt_create >= '%s' group by promoter
    '''

    def my_list(self, query, page={'current': 1}):
        if 'current' not in page or page['current'] < 1:
            page['current'] = 1
        if 'size' not in page:
            page['size'] = 20

        query['row_status'] = 0
        offset = (page['current'] - 1) * page['size']

        username = g.user['username']
        conditions = [SqlApproval.promoter == username, SqlApproval.approver == username, SqlApproval.executor == username]

        result = g.db.query(self.table_cls).filter(or_(*conditions)).filter_by(**query).order_by('-id').offset(offset)\
            .limit(page['size'])

        if not result:
            page['total'] = 0
            return []
        page['total'] = int(math.ceil(g.db.query(self.table_cls).filter(or_(*conditions)).filter_by(**query)
                                      .count() / page['size']))

        return [create_model(self.table_cls, r.to_dict(True)) for r in list(result)]

    def group_by_db(self):
        start = datetime.date.today()
        one_day = datetime.timedelta(days=1)
        while start.weekday() != 0:
            start -= one_day
        result = g.db.execute(self._group_by_db_sql % str(start)).fetchall()
        return [{'db': i[1], 'count': i[0]} for i in result]

    def group_by_promoter(self):
        start = datetime.date.today()
        one_day = datetime.timedelta(days=1)
        while start.weekday() != 0:
            start -= one_day
        result = g.db.execute(self._group_by_promoter_sql % str(start)).fetchall()
        return [{'promoter': i[1], 'count': i[0]} for i in result]


class DbInfoService(BaseService):
    def __init__(self):
        super(DbInfoService, self).__init__(DbInfo)

    def query_by_name(self, db_name):
        query = {'row_status': 0, 'db_name': db_name}
        result = self.query_list(query)
        if result:
            return result[0]
        return None




