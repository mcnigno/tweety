from app import db
from .models import Project, Transmittal, Matrix
from .sec_models import Myuser
# Find user by mail
def find_user_by_mail(recipients):
    try:
        last_word = recipients.split(' ')[-1]
    except:
        last_word = recipients
    
    if last_word[0] == '<':
        email_addr = last_word[1:-1]
    else:
        email_addr = last_word
    
    session = db.session
    user = session.query(Myuser).filter(Myuser.email==email_addr).first()
    
    if user is not None:
        return user.username
    return 'undefined'


# List of projects
def projects():
    session = db.session
    return [(x.name,x.base_code) for x in session.query(Project)]

#### Check if user is allowed
def is_allowed(user,proj):
    session = db.session
    u = session.query(Myuser).filter(Myuser.username==user).first()
    if u is not None:
        projects = u.project
        if proj in [x.base_code for x in projects]:
            return True
    return False

# New tranmittal by request (Chat or Mail)
def tweety_new(user, base_code, subject):
    session = db.session
        
    if is_allowed(user,base_code):
        usr = session.query(Myuser).filter(Myuser.username==user).first()
        prj = session.query(Project).filter(Project.base_code==base_code).first()
        # Search for unlockef transmittal first
        unlocked = session.query(Transmittal).filter(
            Transmittal.project_id == prj.id,
            Transmittal.locked == False
        ).first()
        if unlocked is not None:
            unlocked.subject = subject
            unlocked.locked = True
            unlocked.changed_by_fk = usr.id
            session.commit()
            return unlocked.code

        # Generate new transmittal
        matrix_code = session.query(Matrix).filter(Matrix.code == base_code).first()
        item = Transmittal()
        if matrix_code is not None:
            if matrix_code.prog + 1 < prj.stop_prog:
                user_id = str(usr.id)
                prj_id = str(prj.id)
                matrix_code.prog += 1
                matrix_code.changed_by_fk = user_id
                item.code = "-".join([prj.base_code, str(matrix_code.prog).zfill(prj.prog_digits)]) 
                item.project_id = prj_id
                item.subject = subject
                item.created_by_fk = user_id
                item.changed_by_fk = user_id
                
                session.add(item) 
                session.commit()
                return item.code
            else:
                return 'Project Range Completed'
        else:
            new_matrix = Matrix(code=prj.base_code, prog=prj.start_prog)
            new_matrix.created_by_fk = user_id
            new_matrix.changed_by_fk = user_id
            item.code = "-".join([prj.base_code, str(prj.start_prog).zfill(prj.prog_digits)])
            item.project_id = prj_id
            item.subject = subject
            item.created_by_fk = user_id
            item.changed_by_fk = user_id
            session.add(new_matrix)
            session.add(item) 
            session.commit()
            return item.code
    else:
        return 'You are not Allowed or this project does not exist!' 