import MySQLdb
import MySQLdb.cursors
import json
import time
import os
import hashlib
import urllib2
import requests
import pdb
#from __future__ import print_function

from django.http import * #(HttpResponse, HttpResponseRedirect)
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from django.core.context_processors import csrf

from auth import *
from settings import *

def about(request):
    return render(request,'about.html')

def test(request):
    response = {'Hello':'yash'}
    return HttpResponse(json.dumps(response),content_type = "application/json")

def getDBObject():
    db = MySQLdb.connect(MYSQL_HOST,MYSQL_USERNAME,MYSQL_PASSWORD,'test')
    return db

def validate_user(user_email, user_password):
    #pdb.set_trace()
    errors = []

    try:
        db = getDBObject()
        cursor = db.cursor()
        cursor.execute("SELECT user_id,user_handle FROM users WHERE user_email LIKE '%s' AND user_password LIKE '%s'" % (user_email, user_password))
        row = cursor.fetchone()
        db.close()

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

        return response

    except MySQLdb.Error, e:
        errors.append(str(e))

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

    #pdb.set_trace()

    #return HttpResponse(json.dumps(response), content_type = "application/json")
    return HttpResponse(json.dumps(response),content_type = "application/json")
    #return HttpResponse("HEllo")

@login_required
def home_page(request):
    #user_tweets = get_user_tweets()  - Uncomment when get_user_tweets is ready
    user_details = {
        'user_handle':request.session['user_handle'],
        'user_email':request.session['user_email'],
        'tweets':get_user_tweets(request)
    }
    return render(request,'home.html',user_details)

def logout(request):
    # pdb.set_trace()

    #Check if the user is logged in or not.
    # Do not use @login_required
    # If the user is not logged in , redirect him to the signup page or tell him that he is not logged in
    request.session.flush()
    request.session['logged_in'] = False
    request.session.modified = True

    response = 'logged out'
    return HttpResponse(json.dumps(response),content_type = "application/json")

def dbms(request):
    return render(request,'dbms.html')

def signup(request):
    return render(request,'signup.html')

@csrf_exempt
def signupuser(request):
    #pdb.set_trace()
    if request.method == 'POST':
        user_email    = request.POST.get('user_email')
        user_name     = request.POST.get('user_name')
        user_password = request.POST.get('user_password')
        user_handle   = request.POST.get('user_handle')
        user_bio      = request.POST.get('user_bio')

        # Ethical
        user_password = hashlib.md5(user_password).hexdigest()
        errors = []
        
        try:
            db = getDBObject()
            cursor = db.cursor()
            # Insert statement not working , Jasdeep to fix
            sql_statement = """INSERT INTO users (user_email,user_name,user_password,user_handle,user_bio) VALUES (%s, %s, %s, %s, %s) """

            vals = (str(user_email),str(user_name),str(user_password),str(user_handle),str(user_bio))
            #sql_statement = "INSERT INTO users (user_name) VALUES ('Yash M') "
            #sql_statement = "INSERT users "
            cursor.execute(sql_statement,vals)
        
            db.commit()
            db.close()

        except MySQLdb.Error, e:
            errors.append(str(e))

        #pdb.set_trace()
        user_valid = validate_user(user_email, user_password)

        response = {}
        
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
                'reason':'Not a POST request'
            }

    #pdb.set_trace()

    return HttpResponse(json.dumps(response),content_type = "application/json")

def get_user_tweets(request):
    
    user_handle = request.session['user_handle']

    #db = getDBObject()
    #cursor = db.cursor()
    #sql_statement = ""   -- SELECT tweets for the corresponding user_handle , or user_id 
    #cursor.execute(sql_statement)
    #row = cursor.fetchall()
    #db.close()

    tweets = []

    #for row in rows:
        # get tweets here
        #pass

    return tweets
    