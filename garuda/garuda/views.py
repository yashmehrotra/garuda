import MySQLdb
import MySQLdb.cursors
import json
import time
import os
import hashlib
import urllib2
import requests
import pdb

from django.http import * #(HttpResponse, HttpResponseRedirect)
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from django.core.context_processors import csrf

from auth import *
from settings import *

def about(request):
    return render(request,'about.html')

def getDBObject():
    db = MySQLdb.connect(MYSQL_HOST,MYSQL_USER,"44rrff",GARUDA_DATABASE)
    return db

def validate_user(user_email, user_password):
    #pdb.set_trace()
    errors = []

    try:
        db = getDBObject()
        cursor = db.cursor()
        cursor.execute("SELECT user_id,handle FROM user_data WHERE email LIKE '%s' AND password LIKE '%s'" % (user_email, user_password))
        row = cursor.fetchone()
        db.close()

    except MySQLdb.Error, e:
        errors.append(str(e))

    if row:
        user_id = str(row[0])
        user_handle = str(row[1])
        response = {
            'status':'success',
            'user_id':user_id,
            'user_email':user_email,
            'user_handle':user_handle
        }
    else:
        response = { 
            'status':'failed',
            'reason':'username password combo doesnt match'    #Change the English
        }

    if errors:
        response.append({'error':errors})

    return response

def login_page(request):
    return render(request,'login.html')

@csrf_exempt
def login_user(request):
    #pdb.set_trace()
    if request.method == "POST":
        
        user_email = request.POST.get('user_email')
        user_password = request.POST.get('user_password')
        user_password = hashlib.md5(user_password).hexdigest() #Convert to md5
        user_valid = validate_user(user_email, user_password)
        
        if user_valid['status'] == 'success':
            request.session['user_id'] = user_valid['user_id']
            request.session['user_email'] = user_valid['user_email']
            request.session['user_handle'] = user_valid['user_handle']
            request.session['logged_in'] = True
            response = {
                'status':'success',
                'email':request.session['user_email'],
                'user_id':request.session['user_id'],
                'user_handle':request.session['user_handle']
            }
        else:
            response = {
                'status':'failed',
                'reason':user_valid['reason']
            }
    else:
        response = {
            'status':'failed',
            'error':'not a post request'
        }
    return HttpResponse(json.dumps(response),content_type = "application/json")

@login_required
def welcome_temp(request):
    user_details = {
        'user_handle':request.session['user_handle'],
        'user_email':request.session['user_email']
    }
    return render(request,'welcome.html',user_details)

@login_required
def logout(request):
    request.session.flush()
    request.session['logged_in'] = False
    request.session.modified = True

    response = 'logged out'
    return HttpResponse(json.dumps(response),content_type = "application/json")
