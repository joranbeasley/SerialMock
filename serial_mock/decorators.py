import functools
import re

import time


class QueryStore(object):
    """
    >>> @QueryStore.register("show")
    ... def show_info(self):
    ...    return "MyDevice v0.0.1 SN123456"
    ...
    
    """
    __registered_routes = {

    }
    @staticmethod
    def _find(cmd):
        for key in QueryStore.__registered_routes:
            if (isinstance(key,basestring) and cmd.startswith(key)) or isinstance(key,re._pattern_type) and key.match(cmd):
                method,rest= QueryStore.__registered_routes[key],cmd.split(key,1)[-1].split() if isinstance(key,basestring) else key.match(cmd).groups()
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
            route = func.__name__
        func.delay = delay
        QueryStore.__registered_routes[route] = func
        return func

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
