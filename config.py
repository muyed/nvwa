from os import environ


APP_ENV = environ.get('appEnv')
if not APP_ENV:
    APP_ENV = 'local'


class Config(object):
    SQLALCHEMY_COMMIT_NO_TEARDOWN = True
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    TASK_STATUS = {
        0: '开发中',
        1: '已提测',
        2: '测试中',
        3: '待发预发',
        4: '预发测试中',
        5: '待发线上',
        6: '已上线',
        7: '已完成'
    }


class LocalConfig(Config):
    DB_URL = 'mysql+mysqlconnector://sntuic:1qaz!QAZ@snt-test-pub.mysql.rds.aliyuncs.com:3306/nvwa'
    REDIS_CONFIG = {'host': '47.99.215.186', 'port': 6379, 'password': '3edc#EDC'}
    LOGIN_URL = 'http://uic-daily.3songshu.com/login'
    DB_EXEC_URL = 'http://umc-daily.3songshu.com:7021/tools/db/exec'
    DB_EXPLAIN_ERL = 'http://umc-daily.3songshu.com:7021/tools/db/explain'


class DailyConfig(Config):
    DB_URL = 'mysql+mysqlconnector://sntuic:1qaz!QAZ@snt-daily-pub.mysql.rds.aliyuncs.com:3306/nvwa'
    REDIS_CONFIG = {'host': '47.99.215.186', 'port': 6379, 'password': '3edc#EDC'}
    LOGIN_URL = 'http://uic-daily.3songshu.com/login'
    DB_EXEC_URL = 'http://umc.3songshu.com/tools/db/exec'
    DB_EXPLAIN_ERL = 'http://umc.3songshu.com/tools/db/explain'


class ProdConfig(Config):
    DB_URL = 'mysql+mysqlconnector://snt-schedule:3edc#EDC@rm-bp1coa5g348j9w2pcto.mysql.rds.aliyuncs.com:3306/nvwa'
    REDIS_CONFIG = [
        {'host': '10.10.0.47', 'port': 7001},
        {'host': '10.10.0.47', 'port': 7002},
        {'host': '10.10.0.48', 'port': 7001},
        {'host': '10.10.0.48', 'port': 7002},
        {'host': '10.10.0.49', 'port': 7001},
        {'host': '10.10.0.49', 'port': 7002}
    ]
    LOGIN_URL = 'http://uic.3songshu.com/login'


configs = {
    'local': LocalConfig,
    'daily': DailyConfig,
    'prod': ProdConfig
}
