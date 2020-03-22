from flask_appbuilder.security.sqla.models import User
from sqlalchemy import Column, Integer, ForeignKey, String, Sequence, Table
from sqlalchemy.orm import relationship, backref
from flask_appbuilder import Model
from .models import Project

assoc_projects_users = Table('projects_users', Model.metadata,
                                      Column('id', Integer, primary_key=True),
                                      Column('project_id', Integer, ForeignKey('project.id')),
                                      Column('myuser_id', Integer, ForeignKey('ab_user.id'))
)

class Myuser(User):
    __tablename__ = 'ab_user'
    extra = Column(String(256))
    project = relationship("Project",secondary=assoc_projects_users, backref="users" )
