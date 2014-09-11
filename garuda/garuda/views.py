import MySQLdb
import MySQLdb.cursors
import json
import time
import os
import hashlib
import urllib2
import requests
import settings
import pdb

from django.http import * #(HttpResponse, HttpResponseRedirect)
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from django.core.context_processors import csrf

def about(request):
    return render(request,'about.html')

def getDBObject(db_name):
    db = MySQLdb.connect("localhost","root","44rrff",db_name)
    return db

def testdb(request):
    db = getDBObject('garuda')
    cursor = db.cursor()
    cursor.execute("INSERT INTO test (text) VALUES ('YASH')")
    db.commit()
    db.close()
    return HttpResponse("Done")