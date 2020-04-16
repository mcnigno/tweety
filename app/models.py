from flask_appbuilder import Model
from sqlalchemy import Column, Integer, String, ForeignKey, Date, Table, Boolean
from sqlalchemy.orm import relationship, backref
from flask_appbuilder.models.mixins import AuditMixin
from flask_appbuilder.security.sqla.models import User
import datetime
from flask import g
#from . import db

#from .sec_models import Myuser

def get_user():
    

    return g.user.project
"""

You can use the extra Flask-AppBuilder fields and Mixin's

AuditMixin will add automatic timestamp of created and modified by who


"""


def today():
    return datetime.datetime.today().strftime('%Y-%m-%d')
    #return datetime.datetime.today().strftime('%d-%m-%Y')

#from .sec_models import Myuser

from flask import Markup
class Project(Model,AuditMixin):
    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique = True, nullable=False)
    base_code = Column(String(100), unique = True, nullable=False)
    prog_digits = Column(Integer, nullable=False)
    start_prog = Column(Integer, nullable=False)
    stop_prog = Column(Integer, nullable=False)
    
    def user(self):
        return g.user.id
    

    def __repr__(self):
        return self.name

#from .sec_models import Myuser
class Transmittal(Model,AuditMixin):
    id = Column(Integer, primary_key=True)
    project_id = Column(Integer, ForeignKey('project.id'), nullable=False)
    project = relationship("Project")
    date = Column(Date, default=today)
    code = Column(String(150), unique = True, nullable=False)
    subject = Column(String(255), nullable=False)
    locked = Column(Boolean, default=True)
    quantity = Column(Integer, default=1, nullable=False)

    def __repr__(self):
        return self.code
    
    def tweety_code(self):
        return Markup('<label id="lbtnx">'+self.code+'</label><button class="btnx" data-clipboard-text="'+self.code+'"><img id="btnx" src="/static/img/clippy.svg" alt="Copy to clipboard"></button>')

class Matrix(Model,AuditMixin):
    id = Column(Integer, primary_key=True)
    code = Column(String(150), unique = True, nullable=False)
    prog = Column(Integer)

    def __repr__(self):
        return "-".join(self.code, str(self.prog))



#from flask_appbuilder.security.sqla.models import User

