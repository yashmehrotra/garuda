from django.http import *
from django.shortcuts import render, redirect
import json
import pdb

#============================================================================#
# Checks whether user is logged in or not, if not , redirects to login page  #
#============================================================================#

# The above #=# boxes are fun to make

def login_required(f):
    
    def wrap(request,*args,**kwargs):

        user_logged_in = request.session.get('logged_in',False)
        
        if user_logged_in:
            return f(request, *args, **kwargs)
        else:
            return HttpResponseRedirect('/login')

    wrap.__doc__ = f.__doc__
    wrap.__name__ = f.__name__
    return wrap

# Do study about *args,**kwargs, wraps etc. etc.