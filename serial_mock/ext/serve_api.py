import os

import pickle
from flask import Flask, request, render_template, session
from functools import partial

from serial_mock.aq1_mock import AQ1Base

registered_routes = {}
def register_route(route=None):
    #simple decorator for class based views
    def inner(fn):
        registered_routes[route] = fn
        return fn
    return inner

class FlaskServer(Flask):
    def __init__(self,*args,**kwargs):
        if not args:
            kwargs.setdefault('import_name',__name__)
        Flask.__init__(self,*args ,**kwargs)
        # register the routes from the decorator
        for route,fn in registered_routes.items():
            partial_fn = partial(fn,self)
            partial_fn.__name__ = fn.__name__
            self.route(route)(partial_fn)

class SerialMockAPI(FlaskServer):
    def __init__(self,serial_mock_cls,*args,**kwargs):
        FlaskServer.__init__(self,*args,**kwargs)
        self.secret_key = "ASDASDKYS"
        self.cls = serial_mock_cls
    @register_route("/")
    def index(self):
        query = request.form.get('query', request.args.get('query', None))
        if query is None:
            return render_template("api_terminal.html")
        return self.do_query(query)
    def get_from_session(self):
        #session.pop(self.cls.__name__)
        data = session.get(self.cls.__name__,None)
        if not data:
            print "CREATE NEW SESSION DATA"
            data = pickle.dumps(self.cls("DEBUG"))
        return pickle.loads(data)

    def do_query(self,query):
        inst = self.get_from_session()
        print "INST:",inst
        result = inst.process_cmd(query)
        session[self.cls.__name__] = pickle.dumps(inst)
        print "SAVED:",session[self.cls.__name__]
        return result




if __name__ == "__main__":

    SerialMockAPI(AQ1Base,template_folder=os.path.dirname(__file__)).run(debug=True)