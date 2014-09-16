from django.http import *
import json

def login_required(f):
    def wrap(request,*args,**kwargs):
        user_logged_in = request.session['logged_in']
        if user_logged_in:
            return f(request, *args, **kwargs)
        else:
            ####
            ####    REDIRECT THE BELOW TO A PLEASE LOGIN PAGE
            ####
            ####
            return HttpResponse(json.dumps({'status':'failed' , 'reason':'user not logged in'}),content_type="application/json")

    wrap.__doc__ = f.__doc__
    wrap.__name__ = f.__name__
    return wrap

