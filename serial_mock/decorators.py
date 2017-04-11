import functools
import re

import time
import traceback



class QueryStore(object):
    """
    >>> @QueryStore.register("show")
    ... def show_info(self):
    ...    return "MyDevice v0.0.1 SN123456"
    ...
    
    """
    target=None
    __keybinds__ = {

    }
    __registered_routes__ = {

    }
    @staticmethod
    def _find(cmd):
        for key in QueryStore.__registered_routes__:
            if (isinstance(key,basestring) and cmd.startswith(key)) or isinstance(key,re._pattern_type) and key.match(cmd):
                method,rest= QueryStore.__registered_routes__[key], cmd.split(key, 1)[-1].split() if isinstance(key, basestring) else key.match(cmd).groups()
                if method.delay:
                    time.sleep(method.delay)
                return method,rest

        raise KeyError
    @staticmethod
    def register(func,route=None,delay=None):
        '''
        Register acts as our decorator function typically it is imported as serial_query
        :seealso: serial_query
        
        :param func: the function instance to register to the given route 
        :param route: the serial command to listen to
        :param delay: how long to wait before responding to a given command
        :return: 
        '''
        if route is None:
            route = re.sub("([a-z])([A-Z])",lambda m:" ".join(m.groups()).lower(),re.sub("_"," ",func.__name__))

        func.delay = delay
        QueryStore.__registered_routes__[route] = func
        return func
    @staticmethod
    def bind_key_down(key):
        def _inner(fn):
            QueryStore.__keybinds__[key] = fn
            return fn
        return _inner
    @staticmethod
    def _find_key_binding(key):
        try:
            return QueryStore.__keybinds__[key]
        except:
            traceback.print_exc()
            return None
    @staticmethod
    def _on_key_down_event(key):
        try:
            fn = QueryStore._find_key_binding(key)
        except:
            traceback.print_exc()
        try:
            fn(QueryStore.target)
        except:
            traceback.print_exc()
    def __new__(cls,*args,**kwargs):
        route=delay = None
        if isinstance(args[0],(basestring,re._pattern_type)):
            route=args[0]
        elif "route" in kwargs:
            route = kwargs["route"]
        if not isinstance(args[0],(basestring,re._pattern_type)) and isinstance(args[0],(int,float)):
            delay = args[0]
        elif isinstance(args[0],(basestring,re._pattern_type)) and len(args) >= 2 and isinstance(args[1],(int,float)):
            delay = args[1]
        elif "delay" in kwargs:
            delay = kwargs['delay']
        if route or delay:
            return functools.partial(cls.register,route=route,delay=delay)
        return cls.register(args[0])

serial_query = QueryStore
bind_key_down = QueryStore.bind_key_down
