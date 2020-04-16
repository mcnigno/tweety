from flask import render_template
from flask_appbuilder.models.sqla.interface import SQLAInterface
from flask_appbuilder import ModelView, BaseView
from .models import Project, Matrix, Transmittal
from . import appbuilder, db
from flask_appbuilder.models.sqla.filters import FilterContains, FilterRelationManyToManyEqual, FilterInFunction, FilterEqualFunction, FilterContains
from flask import g
from .sec_models import Myuser
from flask import flash
from flask_appbuilder import expose

def get_user(): 
    #session = db.session
    return g.user

"""
    Application wide 404 error handler
"""
def get_prj():
    return [x.name for x in g.user.project]
from flask import redirect
from flask_appbuilder.fields import AJAXSelectField
from flask_appbuilder.fieldwidgets import Select2AJAXWidget
from wtforms.validators import DataRequired   
from flask import abort, Response

class TransmittalView(ModelView):

    datamodel = SQLAInterface(Transmittal)
    list_columns = ['tweety_code','subject','date','created_by','locked']
    show_columns = ['code','date','created_by','subject','locked']
    edit_columns = ['code','date','subject','locked']
    add_columns = ['date','project','quantity'] 
    base_order = ('id','desc')
    add_form_query_rel_fields = {'project':[['name', FilterInFunction, get_prj]]}
    base_filters = [['created_by', FilterEqualFunction, get_user]]
    
    
    def pre_add(self,item):
        print('PRE ADD TRASMITTAL FUNCTION *************')
        session = db.session
        
        
        # Generate new transmittal
        for i in range(item.quantity):
            # Search for unlockef transmittal first
            unlocked = session.query(Transmittal).filter(
            Transmittal.project_id == item.project.id,
            Transmittal.locked == False
            ).first()
            if unlocked is not None:
                unlocked.subject = 'Pending'
                unlocked.locked = True
                session.commit()
                flash('Unlocked Transmittal Available | Created by ' + str(unlocked.created_by) + ' on '+ str(unlocked.created_on), category='info')
                flash(unlocked.code, category='code')
                  
                continue
            #session = db.session
            matrix_code = session.query(Matrix).filter(Matrix.code == item.project.base_code).first()
            new_t = Transmittal()
            new_t.subject = "Pending"
            new_t.project = item.project
            new_t.created_by_fk = item.created_by_fk
            if matrix_code is not None:
                if matrix_code.prog + 1 < item.project.stop_prog:
                    matrix_code.prog += 1
                    new_t.code = "-".join([item.project.base_code, str(matrix_code.prog).zfill(item.project.prog_digits)])
                    #session.commit()
                else:
                    return flash('Project Range Completed', category='warning')
            else:
                new_matrix = Matrix(code=item.project.base_code, prog=item.project.start_prog)
                new_t.code = "-".join([item.project.base_code, str(item.project.start_prog).zfill(item.project.prog_digits)])
                session.add(new_matrix)
            
            session.add(new_t)
            flash(new_t.code, category='code') 
            session.commit()
        raise Exception('All Codes Released and Locked')    
          

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

class TweetyDashboardView(BaseView):
    default_view = 'dash_dras'
    @expose('/tweety_dash', methods=['POST', 'GET'])
    def dash_dras(self):
        return self.render_template('tweety_dash.html')

#### Tweety REST API
from flask_appbuilder.api import BaseApi, expose, rison, safe
from flask import request
#### Check if user is allowed

from .helpers import projects, tweety_new
class TweetyApi(BaseApi):

    ## http://localhost:5000/api/v1/tweetyapi/ask?q=(proj:BMP-TRA-TRA,subj:subject)
    
    @expose('/ask', methods=['POST', 'GET'])
    #@rison()
    @safe 
    def ask_tweety(self, **kwargs):
        user = request.args.get('user') 
        proj = request.args.get('proj')
        subj = request.args.get('subj')
        #print('USER:', user,'PROJ:',proj,'SUB:',subj) 
        if proj == 'list':
            return self.response(
                200,
                #message="Hello {}".format(kwargs['rison']['name'])
                projects=projects()
            )
        if proj and subj:     
            message = tweety_new(user,proj,subj)
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
        icon="fa-briefcase",
        category="System",
        category_icon='fa-cubes'
    )

appbuilder.add_view(
        TweetyDashboardView,
        "Dashboard",
        icon="fa-tachometer",
        category="System",
        category_icon='fa-cubes'
    )

appbuilder.add_link('New','/transmittalview/add',
        icon="fa-file-archive-o",
        category="Transmittal",
        category_icon='fa-folder')

appbuilder.add_view(
        TransmittalView,
        "List",
        icon="fa-folder-open-o",
        category="Transmittal",
        category_icon='fa-folder'
    )


appbuilder.add_view(
        MatrixView,
        "Matrix List",
        icon="fa-folder-open-o",
        category="System",
        category_icon='fa-envelope'
    )



db.create_all()

from tweety_mail import mail_scheduler
mail_scheduler()