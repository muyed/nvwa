import json
import javaobj
from flask import Flask, request, g, render_template
from flask_cors import CORS
from datetime import timedelta
from config import configs, APP_ENV
# from rediscluster import StrictRedisCluster
from redis import StrictRedis
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import logging


config = configs[APP_ENV]


app = Flask(__name__, template_folder='static/html', static_url_path='')
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = timedelta(seconds=1)

CORS(app, resources={r"/*": {"origins": "*", "max_age": 3600, "supports_credentials": True}})


if isinstance(config.REDIS_CONFIG, list):
    #redis = StrictRedisCluster(config.REDIS_CONFIG)
    pass
else:
    redis = StrictRedis(host=config.REDIS_CONFIG['host'], port=config.REDIS_CONFIG['port'],
                        password=config.REDIS_CONFIG['password'], socket_timeout=2)


Session = sessionmaker(bind=create_engine(config.DB_URL, echo=True))


@app.before_request
def on_before_request():
    if request.path.startswith('js') or request.path.startswith('css'):
        return
    g.db = Session()


@app.teardown_appcontext
def on_teardown(exc=None):
    db = getattr(g, 'db', None)
    if db:
        if exc:
            db.rollback()
        else:
            db.commit()
        db.close()


@app.errorhandler(Exception)
def error_handler(e):
    logging.exception(e)
    db = getattr(g, 'db', None)
    if db:
        db.rollback()
    return render_template('error.html', e=str(e))


class JavaToJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, javaobj.JavaObject):
            if hasattr(obj, 'value'):
                return obj.value
            else:
                obj = obj.__dict__
                obj.pop('classdesc')
                obj.pop('annotations')
                return obj

        return super(JavaToJSONEncoder, self).default(obj)


from app.view import index, login, role, gitlab, jenkins, task, sql_approval, report
