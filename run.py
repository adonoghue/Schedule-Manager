
from __future__ import print_function
import random
import string

import cherrypy

import httplib2
import os

from googleapiclient import discovery
from googleapiclient.discovery import build
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage

import datetime
from rfc3339 import rfc3339
import requests

#----------------------------------------------------------------------------------------
""" This section of code comes from Google's Calendar API quickstart tutorial:
https://developers.google.com/google-apps/calendar/quickstart/python"""

try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None

# If modifying these scopes, delete your previously saved credentials
# at ~/.credentials/calendar-python-quickstart.json
SCOPES = 'https://www.googleapis.com/auth/calendar'
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'Google Calendar API Python Quickstart'
#----------------------------------------------------------------------------------------

class AddEvent(object):
    @cherrypy.expose
    def index(self):
        return open('./indextab.html')

    @cherrypy.expose
    def generateEvent(self, date="01-01-2017", stime="00:00", event="None", etime="00:00", startToggle="false", endToggle="false", quickAdd="None", locationSel=""):
	#print(quickAdd)
	main(date, stime, event, etime, startToggle, endToggle, quickAdd, locationSel)
        return open('./indextab.html')
    
    @cherrypy.expose
    def generateSearchEvent(self, date="01-01-2017", stime="00:00", searchEvent="None", etime="00:00", startToggle="false", endToggle="false", quickAdd="None", locationSel="", **params):
	begin = stime[0:len(stime)-2]
	t1 = stime[-2:]
	end = etime[0:len(etime)-2]
	t2 = etime[-2:]
        #check am or pm and set start toggle accordingly
	if t1.lower() == "am":
	    startToggle = "false"
	else :
	    startToggle = "true"
	if t2.lower() == "am":
	    endToggle = "false"
	else :
	    endToggle = "true"
	main(date, begin, searchEvent, end, startToggle, endToggle, quickAdd, locationSel)
        return open('./indextab.html')
    

def main(date, stime, eventToAdd, etime, startToggle, endToggle, quickAdd, location):
    #----------------------------------------------------------------------------
    """This authentication section is another part of the same code used in the 
    get_credentials function from Google's tutorials found here: 
        https://developers.google.com/google-apps/calendar/quickstart/python"""

    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('calendar', 'v3', http=http)

    #----------------------------------------------------------------------------

    #insert a new event
    calId = 'cphan2@nd.edu'
    #calId = 'aemiledonoghue@gmail.com'
    # make sure start times are AM / PM
    stime = convertPM(stime, startToggle)
    etime = convertPM(etime, endToggle)
    # see if quick add feature is used
    if quickAdd != "None":
	eventToAdd = quickAdd
        stime = stime.split(":")
        if (len(stime[0]) < 2):
            stime[0] = "0" + stime[0]
        if ((len(stime[1])) < 2):
            stime[1] = '0' + stime[1]
        stime = ':'.join(stime)
	# set end time based on start time
	if eventToAdd == "Breakfast" or eventToAdd == "Lunch" or eventToAdd == "Dinner" \
	or eventToAdd == "Gym":
		t = stime.split(":")
		tint = int(t[0])
                tint = tint + 1
                if (len(str(tint)) < 2):
                    tstr = "0" + str(tint) + ":" + t[1]
                else:
		    tstr = str(tint) + ":" + t[1]
		etime = tstr
                etime = checkHours(etime)
	if eventToAdd == "StudyBreak":
		t = stime.split(":")
		tint = int(t[1])
		tint = tint + 10
                etime = t[0] + ":" + str(tint)
                etime = checkHours(etime)
                etime = checkMins(etime)
                etime = checkHours(etime)
	if eventToAdd == "Meeting":
		t = stime.split(":")
		tint = int(t[1])
		tint = tint + 30	
		tstr = t[0] + ":" + str(tint)
		etime = tstr 
                etime = checkMins(etime)
                etime = checkHours(etime)
	if eventToAdd == "HairApp":
		t = stime.split(":")
		tint0 = int(t[0])
		tint1 = int(t[1])
		tint0 = tint0 + 1
		tint1 = tint1 + 30	
		tstr = str(tint0) + ":" + str(tint1)
		etime = tstr
                etime = checkHours(etime)
                etime = checkMins(etime)
                etime = checkHours(etime)
    endDate = checkDate(date, stime, etime)
    event = {
      'summary' : eventToAdd,
      'start': {
        'dateTime': formatDate(date) + 'T' + stime + ':00-04:00',
        'timezone': 'America/New_York',
      },
      'end': {
        'dateTime': formatDate(endDate) + 'T' + etime + ':00-04:00',
        'timezone': 'America/New_York',
      },
      'location': location,
    }
    event = service.events().insert(calendarId=calId, body = event).execute()


def formatDate(date):
    """Convert date from mm-dd-yyyy to yyyy-mm-dd format"""
    date = date.split("-")
    formatted_date = []
    formatted_date.append(date[2])
    formatted_date.append(date[0])
    formatted_date.append(date[1])
    return '-'.join(formatted_date)

def checkDate(date, stime, etime):
    """Set proper date if event goes overnight"""
    stime = stime.split(':')
    if (len(stime[1]) < 2):
        stime[1] = stime[1] + '0'
    stime = ''.join(stime)
    etime = etime.split(':')
    if (len(etime[1]) < 2):
        etime[1] = etime[1] + '0'
    etime = ''.join(etime)
    date = date.split('-')
    print('etime: {} < {} stime'.format(int(etime), int(stime)))
    if int(etime) < int(stime):
        dateInt = int(date[1]) + 1
        date[1] = str(dateInt)
    return '-'.join(date)

def checkMins(etime):
    """Check if minutes roll over"""
    t = etime.split(":")
    hint = int(t[0])
    mint = int(t[1])
    if mint >= 60:
        mint = mint - 60
        hint = str(hint + 1)
        if mint < 10:
            mint = '0' + str(mint)
        else:
            mint = str(mint)
    return hint + ":" + mint

def checkHours(time):
    """Check if hours go past midnight"""
    time = time.split(":")
    hint = int(time[0])
    mint = int(time[1])
    if hint >= 24:
        hint = hint - 24
    tstr = str(hint) + ":" + str(mint)
    return tstr

def convertPM(time, toggle):
    """Convert hours to range from 0-23"""
    time = time.split(":")
    timeint = int(time[0])
    if toggle == "true":
        if timeint != 12:
            timeint = timeint + 12
            timestr = str(timeint) + ":" + time[1]
        else:
            timestr = ":".join(time)
    else: # AM times
        if timeint == 12:
            timeint = 0
            timestr = str(timeint) + ":" + time[1]
        else:
            timestr = ":".join(time)
    return timestr

def get_credentials():
    # THE CODE IN THIS FUNCTION COMES DIRECTLY FROM GOOGLE'S API TUTORIAL:
    # https://developers.google.com/google-apps/calendar/quickstart/python
    """Gets valid user credentials from storage.

    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth2 flow is completed to obtain the new credentials.

    Returns:
        Credentials, the obtained credential.
    """
    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, '.credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir,
                                   'calendar-python-quickstart.json')

    store = Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        if flags:
            credentials = tools.run_flow(flow, store, flags)
        else: # Needed only for compatibility with Python 2.6
            credentials = tools.run(flow, store)
        print('Storing credentials to ' + credential_path)
    return credentials


if __name__ == '__main__':
    cherrypy.config.update({'server.socket_port': 8080})
    cherrypy.quickstart(AddEvent())

