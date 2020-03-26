import logging
from .sec import MySecurityManager

from flask import Flask
from flask_appbuilder import AppBuilder, SQLA
from .index import MyIndexView
from flask_mail import Mail
"""
 Logging configuration
"""

logging.basicConfig(format="%(asctime)s:%(levelname)s:%(name)s:%(message)s")
logging.getLogger().setLevel(logging.DEBUG)

app = Flask(__name__)
app.config.from_object("config")
db = SQLA(app)
mail = Mail(app)

appbuilder = AppBuilder(app, db.session, 
            security_manager_class=MySecurityManager,
            indexview=MyIndexView,
            base_template='mybase.html')
#appbuilder = AppBuilder(app, db.session)

"""
from sqlalchemy.engine import Engine
from sqlalchemy import event

#Only include this for SQLLite constraints
@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    # Will force sqllite contraint foreign keys
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()
"""

from . import views
