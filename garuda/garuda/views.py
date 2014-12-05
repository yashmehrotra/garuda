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

    except MySQLdb.Error, e:
        errors.append(str(e))

    if errors:
        response.append({'error':errors})
        return response

    if not errors:
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
        'tweets':get_following_tweets(request)
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

    #response = 'logged out'
    #return HttpResponse(json.dumps(response),content_type = "application/json")
    return HttpResponseRedirect('/login')

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

            query = "SELECT * FROM users WHERE user_email LIKE '%s' " % (user_email)

            cursor.execute(query)

            rows = cursor.fetchall()

            if rows:
                response = {
                    'status':'failed',
                    'reason':'email already exists'
                }

                return HttpResponse(json.dumps(response),content_type = "application/json")

        except MySQLdb.Error, e:
            errors.append(str(e))

        try:
            db = getDBObject()
            cursor = db.cursor()

            query = "SELECT * FROM users WHERE user_handle LIKE '%s' " % (user_handle)

            cursor.execute(query)

            rows = cursor.fetchall()

            if rows:
                response = {
                    'status':'failed',
                    'reason':'user handle already exists'
                }

                return HttpResponse(json.dumps(response),content_type = "application/json")

        except MySQLdb.Error, e:
            errors.append(str(e))
        
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

def get_user_tweets(user_id):
    
    table = 'user_' + user_id

    #pdb.set_trace()

    errors = []

    try:
        db = getDBObject()
        cursor = db.cursor()

        query = "SELECT user_handle FROM users WHERE user_id = '{0}' ".format(user_id)
        cursor.execute(query)

        row = cursor.fetchone()

        if row:
            user_handle = str(row[0])
        else:
            # You are dead if it comes in here
            pass

    except MySQLdb.Error, e:
        errors.append(str(e))

    tweets = []

    try:
        db = getDBObject()
        cursor = db.cursor()
        sql_statement = "SELECT * FROM {0}".format(table) 
        cursor.execute(sql_statement)
        
        rows = cursor.fetchall()

        #pdb.set_trace()

        if rows:
            for row in rows:
                tweet_id    = row[0]
                tweet_value = row[1]
                starred_by  = row[2]
                tags        = row[3]
                post_time   = row[4]

                if not starred_by:
                    starred_by = ''

                tweets.append({
                    'tweet_id':tweet_id,
                    'tweet_value':tweet_value,
                    'stars':len(starred_by),          # Fix
                    'tags':json.loads(tags),
                    'post_time':post_time,
                    'posted_by':user_handle
                })

        else:
            # No rows return empty set
            pass
    
        db.close()

    except MySQLdb.Error, e:
        errors.append(e)


    # get all the users that the parent follows
    # append them to the user's tweet list -- seperate user's tweet from the tweet feed

    return tweets

def get_following_tweets(request):

    #pdb.set_trace()
    
    user_id = request.session['user_id']
    table = 'user_' + user_id + '_follow'

    tweets = []
    user_following = []

    errors = []

    try:
        db = getDBObject()
        cursor = db.cursor()

        query = "SELECT user_id FROM {0} WHERE user_status LIKE 'following' ".format(table)

        cursor.execute(query)

        rows = cursor.fetchall()

        if rows:
            for row in rows:
                following_id = str(row[0])

                user_following.append(following_id)

        else:
            # Add exception
            pass

    except MySQLdb.Error, e:
        errors.append(str(e))

    for following in user_following:
        tweets += get_user_tweets(following)

    # Below is a Little Magic Trick that shows you your feed in the correct time orders , Also reverse is faster than splice in an average case
    tweets = sorted(tweets, key=lambda k: k['post_time'])
    tweets.reverse() 

    return tweets

@csrf_exempt
@login_required
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

            tweet_id = cursor.lastrowid

            db.commit()
            db.close()

            for tag in json.loads(tags):
                fill_tag_table(user_id, tag, tweet_id)

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

@login_required
def get_followers(request):
    # Create a html page
    # Get all the Followers, and those who follow in a tab manner
    user_id = request.session['user_id']
    table = 'user_' + user_id + '_follow'

    followers_list = []
    errors = []

    try:
        db = getDBObject()
        cursor = db.cursor()

        query = "SELECT {0}.user_id, `users`.user_handle, `users`.user_name FROM {0},users WHERE {0}.user_status LIKE 'follower' AND `users`.user_id = `{0}`.user_id ".format(table) # Improve query so that we get his user details like handle , name etc.
        cursor.execute(query)

        rows = cursor.fetchall()

        if rows:
            for row in rows:
                user_follower_id = row[0]
                user_handle = row[1]
                user_name = row[2]

                followers_list.append({
                        'follower_id':user_follower_id,
                        'user_handle':user_handle,
                        'user_name':user_name
                    })

        else:
            pass

    except MySQLdb.Error, e:
        errors.append(str(e))

    page_data = {
        'user_handle':request.session['user_handle'],
        'user_id':request.session['user_id'],
        'followers_list':followers_list
    }

    if not errors:
        return render(request,'followers.html',page_data)


@login_required
def get_following(request):
    # Create a html page
    # Get all the Followers, and those who follow in a tab manner
    user_id = request.session['user_id']
    table = 'user_' + user_id + '_follow'

    following_list = []
    errors = []

    #pdb.set_trace()

    try:
        db = getDBObject()
        cursor = db.cursor()

        query = "SELECT {0}.user_id, `users`.user_handle, `users`.user_name FROM {0},users WHERE {0}.user_status LIKE 'following' AND `users`.user_id = `{0}`.user_id ".format(table) # Improve query so that we get his user details like handle , name etc.
        cursor.execute(query)

        rows = cursor.fetchall()

        db.close()

        if rows:
            for row in rows:
                user_following_id = row[0]
                user_handle = row[1]
                user_name = row[2]

                following_list.append({
                        'following_id':user_following_id,
                        'user_handle':user_handle,
                        'user_name':user_name
                    })

        else:
            pass

    except MySQLdb.Error, e:
        errors.append(str(e))

    page_data = {
        'user_handle':request.session['user_handle'],
        'user_id':request.session['user_id'],
        'following_list':following_list
    }

    # If followers list is empty see case
    # return render(request,'home.html',user_details)
    return render(request,'following.html',page_data)


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
        
        query = "CREATE TABLE IF NOT EXISTS {0} (`user_id` int(200) NOT NULL,`user_status` varchar(200) NOT NULL COMMENT 'follower - following our parent/following - our parent following the user' ) ENGINE=InnoDB DEFAULT CHARSET=latin1;".format(user_follow)
        cursor.execute(query)

        db.commit()
        db.close

    except MySQLdb.Error, e:
        errors.append(e)

@login_required
def follow(request):
    return render(request,'follow.html')

@csrf_exempt
@login_required
def add_follower(request):

    if request.method == 'POST':
    
        user_id = request.session['user_id']
        user_to_follow = str(request.POST.get('user_to_follow'))

        table_parent = 'user_' + user_id + '_follow'
        table_following = 'user_' + user_to_follow + '_follow'

        errors = []

        try:
            db = getDBObject()
            cursor = db.cursor()

            query = "INSERT INTO %s (user_id, user_status) VALUES ('%s', 'following') " % (table_parent, user_to_follow)
            cursor.execute(query)

            query = "INSERT INTO %s (user_id, user_status) VALUES ('%s', 'follower') " % (table_following, user_id)
            cursor.execute(query)

            db.commit()
            db.close()

        except MySQLdb.Error, e:
            errors.append(str(e))

        if not errors:
            response = {
                'status':'success',
                'result':'{0} is following {1}'.format(user_id,user_to_follow)
            }

        else:
            response = {
                'status':'failed',
                'error':errors
            }

    else:
        response = {
            'status':'failed',
            'error':'Not a POST request'
        }

    return HttpResponse(json.dumps(response),content_type = "application/json")

@csrf_exempt
@login_required
def search(request,search_term):
    # get the search term here , search for tags and users
    if True:

        #search_term = request.POST.get('search_term')

        try:
            db = getDBObject()
            cursor = db.cursor()

            query = "SELECT user_tweet_id FROM tags WHERE tag_value = '{0}' ".format(search_term)
            cursor.execute(query)

            row = cursor.fetchone()

            if row:
                user_tweet_id = row[0]
            
            else:
                response = {
                    'status':'success',
                    'result':'no term'
                }

                return HttpResponse(json.dumps(response),content_type = "application/json")

            user_tweet_id = json.loads(user_tweet_id)

            user_tweet_list = []

            for tweet in user_tweet_id:
                tweet = tweet.split('-')

                user_id  = tweet[0]
                tweet_id = tweet[1]

                user_tweet_list.append({
                    'tweet_id':tweet_id,
                    'user_id':user_id
                })

            all_tweets = []

            for tweet in user_tweet_list:
                # Get details directly from the db
                user_id = tweet['user_id']
                tweet_id = tweet['tweet_id']

                table_tweet = 'user_' + str(user_id)

                ##
                ## Add MySQL Queries here 
                ##
                try:
                    db = getDBObject()
                    cursor = db.cursor()

                    query = "SELECT tweet_value,post_time FROM {0} WHERE tweet_id = '{1}' ".format(table_tweet, tweet_id)
                    cursor.execute(query)

                    row = cursor.fetchone()

                    if row:
                        tweet_value = row[0]
                        post_time = row[1]

                    query = "SELECT user_handle FROM users WHERE user_id = '{0}' ".format(user_id)
                    cursor.execute(query)

                    row2 = cursor.fetchone()

                    if row2:
                        user_handle = row2[0]

                    all_tweets.append({
                            'user_id':user_id,
                            'user_handle':user_handle,
                            'tweet':tweet_value,
                            'post_time':post_time
                        })

                except MySQLdb.Error, e:
                    errors.append(str(e))

            all_tweets = sorted(all_tweets, key=lambda k: k['post_time'])
            all_tweets.reverse()

            page_data = {
                'user_id':request.session['user_id'],
                'user_handle':request.session['user_handle'],
                'tweets':all_tweets,
                'search_term':search_term
            }

            return render(request,'search.html',page_data)


        except MySQLdb.Error, e:
            errors.append(str(e))

    else:
        response = {
            'status':'failed',
            'error':'not a post request'
        }

        return HttpResponse(json.dumps(response),content_type = "application/json")

@login_required
def user_page(request, user_name):
    # Intelligently add it to the urls link such that host/user redirects to this
    user_id_parent = request.session['user_id']
    user_handle_parent = request.session['user_handle']

    user_data = {}

    errors = []
    
    try:
        db = getDBObject()
        cursor = db.cursor()

        query = "SELECT user_handle, user_bio, user_email, user_name, user_id FROM users WHERE user_handle = '{0}' ".format(user_name)
        cursor.execute(query)

        row = cursor.fetchone()

        db.close()

        if row:
            user_handle = row[0]
            user_bio = row[1]
            user_email = row[2]
            user_name = row[3]
            user_id = row[4]

            user_data['user_handle_p'] = user_handle
            user_data['user_bio_p']    = user_bio
            user_data['email_p']       = user_email
            user_data['user_name_p']   = user_name

        else:
            pass

    except MySQLdb.Error, e:
        errors.append(str(e))

    tweets_user = get_user_tweets(str(user_id))

    tweets_user = sorted(tweets_user, key=lambda k: k['post_time'])
    tweets_user.reverse()

    user_data['tweets'] = tweets_user
    user_data['user_id'] = request.session['user_id']
    user_data['user_handle'] = request.session['user_handle']

    return render(request,'userpage.html',user_data)


@login_required
def my_tweets(request):

    user_id = request.session['user_id']
    user_handle = request.session['user_handle']

    table = 'user_' + user_id

    errors = []

    tweets = []

    try:
        db = getDBObject()
        cursor = db.cursor()

        query = "SELECT * FROM  {0} ".format(table)
        cursor.execute(query)

        rows = cursor.fetchall()

        db.close()
        
        if rows:
            for row in rows:
                tweet_id    = row[0]
                tweet_value = row[1]
                starred_by  = row[2]
                tags        = row[3]
                post_time   = row[4]

                if not starred_by:
                    starred_by = ''

                tweets.append({
                    'tweet_id':tweet_id,
                    'tweet_value':tweet_value,
                    'stars':len(starred_by),          # Fix
                    'tags':json.loads(tags),
                    'post_time':post_time
                })

        else:
            # No rows return empty set
            pass

    except MySQLdb.Error, e:
        errors.append(str(e))

    tweets = sorted(tweets, key=lambda k: k['post_time'])
    tweets.reverse() 

    page_data = {
        'user_id':user_id,
        'user_handle':user_handle,
        'tweets':tweets
    }

    return render(request,'mytweets.html',page_data)

@login_required
def view_all_users(request):

    user_id_parent = request.session['user_id']

    users_list = []

    errors = []

    table = 'user_' + user_id_parent + '_follow'

    try:
        db = getDBObject()
        cursor = db.cursor()

        query = "SELECT user_id FROM {0} WHERE user_status LIKE 'following' ".format(table)
        cursor.execute(query)

        rows = cursor.fetchall()

        users_following = []

        if rows:
            for row in rows:
                users_following.append(str(row[0]))

    except MySQLdb.Error, e:
        errors.append(str(e))

    try:
        db = getDBObject()
        cursor = db.cursor()

        query = "SELECT * FROM users WHERE user_id != '{0}' ".format(user_id_parent)
        cursor.execute(query)

        rows = cursor.fetchall()

        db.close()

        if rows:
            for row in rows:
                user_id = row[0]
                user_handle = row[1]
                user_name = row[3]

                if str(user_id) in users_following:
                    follow = True
                else:
                    follow = False

                #pdb.set_trace()
                
                users_list.append({
                    'user_id':user_id,
                    'user_handle':user_handle,
                    'user_name':user_name,
                    'follow':follow
                })

        else:
            pass

    except MySQLdb.Error, e:
        errors.append(str(e))

    #pdb.set_trace()

    page_data = {
        'user_id':request.session['user_id'],
        'user_handle':request.session['user_handle'],
        'users':users_list
    }

    return render(request,'all.html',page_data)

def fill_tag_table(user_id, tag, tweet_id):

    errors = []

    #pdb.set_trace()

    user_tweet_id = str(user_id) + '-' + str(tweet_id)

    tag = str(tag)

    try:
        db = getDBObject()
        cursor = db.cursor()

        query = "SELECT tag_id,user_tweet_id FROM tags WHERE tag_value LIKE '{0}' ".format(tag)
        cursor.execute(query)

        row = cursor.fetchone()

        if not row:
            user_tweet_list = [user_tweet_id]
            user_tweet_list = json.dumps(user_tweet_list)

            query = "INSERT INTO tags (tag_value,user_tweet_id) VALUES ('%s', '%s') " % (tag, user_tweet_list)
            cursor.execute(query)

            db.commit()

            db.close()

        else:
            tag_id = row[0]
            user_tweet_id_db = row[1]

            user_tweet_id_db = json.loads(user_tweet_id_db)
            user_tweet_id_db.append(user_tweet_id)
            user_tweet_id_db = json.dumps(user_tweet_id_db)

            query = "UPDATE tags SET `user_tweet_id` = '{0}' WHERE tag_id = '{1}' ".format(user_tweet_id_db, tag_id)
            cursor.execute(query)

            db.commit()

            db.close()

    except MySQLdb.Error, e:
        errors.append(str(e))


def dosearch(request):
    return render(request,'dosearch.html')

def remove_following(request,user_id):

    user_id_parent = request.session['user_id']

    user_id = str(user_id)

    errors = {}

    table_parent = "user_" + user_id_parent + "_follow"
    table = "user_" + user_id + "_follow"

    try:
        db = getDBObject()
        cursor = db.cursor()

        query = "DELETE FROM {0} WHERE user_status = 'following' AND user_id = '{1}' ".format(table_parent,user_id_parent)
        cursor.execute(query)

        query = "DELETE FROM {0} WHERE user_status = 'follower' AND user_id = '{1}' ".format(table,user_id)
        cursor.execute(query)

        db.commit()
        db.close()

    except MySQLdb.Error, e:
        errors.append(str(e))

    ##
    ## Add this to urls and templates
    ##
    
    pass
