#from flask_appbuilder import IndexView
from flask_appbuilder import BaseView, expose
import random


class IndexView(BaseView):
    """
        A simple view that implements the index for the site
    """
    
    
    route_base = ""
    default_view = "index"
    index_template = "appbuilder/index.html"
    #param=random_line(afile) 

    @expose("/")
    def index(self):
        afile = open("app/static/img/tweety_quotes.txt")

        def random_line(afile):     
            line = next(afile)
            for num, aline in enumerate(afile, 2):
                if random.randrange(num): continue
                line = aline
                return line
        self.update_redirect()
        return self.render_template(self.index_template, 
                    appbuilder=self.appbuilder,
                    param =random_line(afile))


class MyIndexView(IndexView):
    index_template = 'my_index.html'
    