import MySQLdb
import MySQLdb.cursors
import json
import time
import os
import hashlib
import urllib2
import requests
import pdb
import re
from datetime import datetime

from django.http import * #(HttpResponse, HttpResponseRedirect)
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from django.core.context_processors import csrf

from auth import *
from settings import *

def about(request):
    return render(request,'about.html')

def test(request):
    response = {'Hello':'Yash'}
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

    return HttpResponse(json.dumps(response),content_type = "application/json")

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

            # Improve the below shit into something good looking
            sql_statement = "INSERT INTO users (user_email,user_name,user_password,user_handle,user_bio) VALUES (%s, %s, %s, %s, %s)"

            vals = (str(user_email),str(user_name),str(user_password),str(user_handle),str(user_bio))
            cursor.execute(sql_statement, vals)
            
            user_id = cursor.lastrowid
            
            db.commit()
            db.close()

            create_user_table(user_id)
        
        except MySQLdb.Error, e:
            errors.append(str(e))

        # Create user_id_table u fucktard

        #pdb.set_trace()
        user_valid = validate_user(user_email, user_password)

        response = {}
        
        if user_valid['status'] == 'success':
            
            request.session['user_id']     = user_valid['user_id']
            request.session['user_email']  = user_valid['user_email']
            request.session['user_handle'] = user_valid['user_handle']
            request.session['logged_in']   = True
            
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
    user_id = request.session['user_id']

    table = 'user_' + user_id

    errors = []

    try:
        db = getDBObject()
        cursor = db.cursor()
        sql_statement = "SELECT * FROM {0}".format(table) 
        cursor.execute(sql_statement)
        
        rows = cursor.fetchall()

        if rows:
            for row in rows:
                # Add rows here
                pass

            pass
    
        #db.close()

    except MySQLdb.Error, e:
        errors.append(e)

    tweets = []

    #for row in rows:
        # get tweets here
        #pass

    # get all the users that the parent follows
    # append them to the user's tweet list -- seperate user's tweet from the tweet feed

    return tweets

@csrf_exempt
def post_tweet(request):

    errors = []
    #pdb.set_trace()

    if request.method == "POST":
        
        tweet_value = str(request.POST.get('tweet_value'))
        tags        = re.findall(r"#(\w+)", tweet_value)      # The tag extractor - Epic Shit
        post_time   = str(datetime.now())

        user_id = request.session['user_id']
        tags = json.dumps(tags)

        try:
            db = getDBObject()
            cursor = db.cursor()
            table = 'user_' + str(user_id)

            query = "INSERT INTO %s (tweet_value, tags, post_time) VALUES ('%s', '%s', '%s')" % (table, tweet_value, tags, post_time)
            cursor.execute(query)

            db.commit()
            db.close()

        except MySQLdb.Error, e:
            errors.append(str(e))

        if not errors:
            response = {
                'status':'success',
                'message':'Tweet successfully added',
                'tweet':tweet_value,
                'tags':tags
            }

    else:
        response = {
            'failed':'Not a POST request'
        }

    return HttpResponse(json.dumps(response),content_type = "application/json")

def see_followers(request):
    # Create a html page
    # Get all the Followers, and those who follow in a tab manner
    pass

# Also start create group etc, like , star

def create_user_table(user_id):
    
    #pdb.set_trace()
    errors = []
    
    try:
        db = getDBObject()
        user_id = 'user_' + str(user_id)

        cursor = db.cursor()

        # For creating user table for tweets
        query = "CREATE TABLE IF NOT EXISTS {0} (`tweet_id` int(11) NOT NULL AUTO_INCREMENT,`tweet_value` text NOT NULL,`starred_by` text,`tags` text,`post_time` datetime NOT NULL,`hide` int(1) NOT NULL DEFAULT '0' COMMENT '0-show , 1 - hide',`spam_count` int(11) NOT NULL DEFAULT '0',`group_tweet` int(11) NOT NULL DEFAULT '0' COMMENT '0-no , 1 yes',PRIMARY KEY (`tweet_id`)) ENGINE=InnoDB DEFAULT CHARSET=latin1 AUTO_INCREMENT=1".format(user_id)
        cursor.execute(query)

        # For creating user table followers
        user_follow = user_id + '_follow'
        
        query = "CREATE TABLE IF NOT EXISTS {0} (`user_id` int(200) NOT NULL,`user_status` varchar(200) NOT NULL COMMENT 'follower - following our parent/following - our parent following the user') ENGINE=InnoDB DEFAULT CHARSET=latin1;".format(user_follow)
        cursor.execute(query)

        db.commit()
        db.close

    except MySQLdb.Error, e:
        errors.append(e)

