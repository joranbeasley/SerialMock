import functools

import time


class QueryStore(object):
    """
    >>> @QueryStore.register("show")
    ... def show_info():
    ...    return "MyDevice v0.0.1 SN123456"
    ...
    
    """
    __registered_routes = {

    }
    @staticmethod
    def find(cmd):
        for key in QueryStore.__registered_routes:
            if cmd.startswith(key):
                method= QueryStore.__registered_routes[key],cmd.split(key,1)[-1].split()
                if method.delay:
                    time.sleep(method.delay)
                return method

        raise KeyError
    @staticmethod
    def register(func,route=None,delay=None):
        if route is None:
            route = func.__name__
        func.delay = delay
        QueryStore.__registered_routes[route] = func
        return func

    def __new__(cls,*args,**kwargs):
        print args,kwargs
        route=delay = None
        if isinstance(args[0],basestring):
            route=args[0]
        elif "route" in kwargs:
            route = kwargs["route"]
        if not isinstance(args[0],basestring) and isinstance(args[0],(int,float)):
            delay = args[0]
        elif isinstance(args[0],basestring) and len(args) >= 2 and isinstance(args[1],(int,float)):
            delay = args[1]
        elif "delay" in kwargs:
            delay = kwargs['delay']
        if route or delay:
            return functools.partial(cls.register,route=route,delay=delay)
        return cls.register(args[0])

serial_query = QueryStore
