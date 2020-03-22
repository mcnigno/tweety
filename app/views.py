from flask import render_template
from flask_appbuilder.models.sqla.interface import SQLAInterface
from flask_appbuilder import ModelView
from .models import Project, Matrix, Transmittal
from . import appbuilder, db
from flask_appbuilder.models.sqla.filters import FilterContains, FilterRelationManyToManyEqual, FilterInFunction, FilterEqualFunction, FilterContains
from flask import g
from .sec_models import Myuser
from flask import flash

def get_user():
    #session = db.session
    return g.user.id

"""
    Application wide 404 error handler
"""
def get_prj():
    return [x.name for x in g.user.project]
from flask import redirect

class TransmittalView(ModelView):

    datamodel = SQLAInterface(Transmittal)
    list_columns = ['tweety_code','subject','date','created_by','locked']
    show_columns = ['code','date','created_by','subject','locked']
    edit_columns = ['code','date','created_by','subject','locked']
    add_columns = ['project','date','subject']
    base_order = ('id','desc')

    def pre_add(self,item):
        session = db.session
        
        # Search for unlockef transmittal first
        unlocked = session.query(Transmittal).filter(
            Transmittal.project_id == item.project.id,
            Transmittal.locked == False
        ).first()
        if unlocked is not None:
            unlocked.subject = item.subject
            unlocked.locked = True
            session.commit()
            flash(unlocked.code, category='code')
            raise Exception('Unlocked Transmittal Available | Created by ' + str(unlocked.created_by) + ' on '+ str(unlocked.created_on))  

        # Generate new transmittal
        matrix_code = session.query(Matrix).filter(Matrix.code == item.project.base_code).first()
        if matrix_code is not None:
            if matrix_code.prog + 1 < item.project.stop_prog:
                matrix_code.prog += 1
                item.code = "-".join([item.project.base_code, str(matrix_code.prog).zfill(item.project.prog_digits)])
                session.commit()
            else:
                return flash('Project Range Completed', category='warning')
        else:
            new_matrix = Matrix(code=item.project.base_code, prog=item.project.start_prog)
            item.code = "-".join([item.project.base_code, str(item.project.start_prog).zfill(item.project.prog_digits)])
            session.add(new_matrix)
            session.commit()
        flash(item.code, category='code')
      

class ProjectView(ModelView):
    datamodel = SQLAInterface(Project)
    list_columns = ['name','base_code','start_prog','stop_prog','prog_digits']
    show_columns = ['name']
    edit_columns = ['name','base_code','start_prog','stop_prog','prog_digits']
    add_columns = ['name','base_code','start_prog','stop_prog','prog_digits']
    #base_filters = [['users',FilterRelationManyToManyEqual, 1]]
    base_filters = [['name', FilterInFunction, get_prj]]
    
    related_views = [TransmittalView]
    show_template = 'appbuilder/general/model/show_cascade.html'
    
    
        
class MatrixView(ModelView):
    datamodel = SQLAInterface(Matrix)
    list_columns = ['code','prog']
    show_columns = ['code','prog']
    edit_columns = ['code','prog']
    add_columns = ['code','prog']

#### Tweety REST API
from flask_appbuilder.api import BaseApi, expose, rison, safe
from flask import request
def apitrn(base_code, subject):
    session = db.session
    prj = session.query(Project).filter(Project.base_code==base_code).first()
    if prj is not None:
        # Search for unlockef transmittal first
        unlocked = session.query(Transmittal).filter(
            Transmittal.project_id == prj.id,
            Transmittal.locked == False
        ).first()
        if unlocked is not None:
            unlocked.subject = subject
            unlocked.locked = True
            session.commit()
            return unlocked.code

        # Generate new transmittal
        matrix_code = session.query(Matrix).filter(Matrix.code == base_code).first()
        item = Transmittal()
        if matrix_code is not None:
            if matrix_code.prog + 1 < prj.stop_prog:
                matrix_code.prog += 1
                
                item.code = "-".join([prj.base_code, str(matrix_code.prog).zfill(prj.prog_digits)]) 
                item.project_id = prj.id
                item.subject = subject
                item.created_by_fk = '1'
                item.changed_by_fk = '1'
                matrix_code.changed_by_fk='1'
                session.add(item) 
                session.commit()
                return item.code
            else:
                return 'Project Range Completed'
        else:
            new_matrix = Matrix(code=item.project.base_code, prog=item.project.start_prog)
            new_matrix.created_by_fk = '1'
            new_matrix.changed_by_fk = '1'
            item.code = "-".join([prj.base_code, str(prj.start_prog).zfill(prj.prog_digits)])
            item.project_id = prj.id
            item.subject = subject
            item.created_by_fk = '1'
            item.changed_by_fk = '1'
            session.add(new_matrix)
            session.add(item) 
            session.commit()
            return item.code
    else:
        return 'This project does not exist!' 


import urllib.parse
class TweetyApi(BaseApi):

    #base_route = '/tweetyapi/v2/nice'

    @expose('/greeting')
    def greeting(self):
        return self.response(200, message="Hello")

    @expose('/greeting2', methods=['POST', 'GET'])
    def greeting2(self):
        if request.method == 'GET':
            return self.response(200, message="Hello (GET)")
        return self.response(201, message="Hello (POST)")

    ## http://localhost:5000/api/v1/tweetyapi/ask?q=(proj:BMP-TRA-TRA,subj:subject)
    @expose('/ask', methods=['POST', 'GET'])
    @rison()
    @safe 
    def greeting3(self, **kwargs):
        if 'proj' and 'subj' in kwargs['rison']: 
            
            proj = kwargs['rison']['proj']
            subj = kwargs['rison']['subj']  
            
            message = apitrn(proj,subj)
            return self.response(
                200,
                #message="Hello {}".format(kwargs['rison']['name'])
                transmittal=message 
            )
        return self.response_400(message="Please send your name")

    # without rison
    @expose('/ask2', methods=['POST', 'GET'])
    #@rison()
    @safe 
    def get_transmittal(self, **kwargs): 
        proj = request.args.get('proj')
        subj = request.args.get('subj')
        print(proj,subj) 
        if proj and subj:     
            message = apitrn(proj,subj)
            return self.response(
                200,
                #message="Hello {}".format(kwargs['rison']['name'])
                transmittal=message 
            )
        return self.response_400(message="Please send the Project code base (es. BMP-V-TRA) and your Subject.")



appbuilder.add_api(TweetyApi)

@appbuilder.app.errorhandler(404)
def page_not_found(e):
    return (
        render_template(
            "404.html", base_template=appbuilder.base_template, appbuilder=appbuilder
        ),
        404,
    )

appbuilder.add_view(
        ProjectView,
        "Project List",
        icon="fa-folder-open-o",
        category="System",
        category_icon='fa-envelope'
    )

appbuilder.add_view(
        TransmittalView,
        "Transmittal List",
        icon="fa-folder-open-o",
        category="System",
        category_icon='fa-envelope'
    )

appbuilder.add_view(
        MatrixView,
        "Matrix List",
        icon="fa-folder-open-o",
        category="System",
        category_icon='fa-envelope'
    )



db.create_all()
