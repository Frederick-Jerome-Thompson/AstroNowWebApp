from flask import Flask, render_template, flash, request, jsonify, Markup



import logging, io, os, sys
# import pandas as pd
# import numpy as np

import scipy


from flask_ngrok import run_with_ngrok

import pytz
import Planet_Tools, pyEph_Tools, ephem, astroNow
import datetime as dt
# import matplotlib.pyplot as plt

import random



app = Flask(__name__)
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = False #needed to stop errors...
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0 #no caching because of image stuff


run_with_ngrok(app)  # Start ngrok when app is run


@app.before_first_request
def startup():
  global QR
  QR = ephem.Observer()
  QR.lon, QR.lat = '-83:09:31', '42:31:26'



@app.route("/")
def hello():

    return render_template( 'index.html')


# accepts either deafult values or user inputs and outputs prediction 
@app.route('/background_process', methods=['POST', 'GET'])
def background_process():

    theNow = astroNow.utcnow()
    theHereTime = astroNow.detnow()

    theYear = theHereTime.year
    theMonth = theHereTime.month
    theDay = theHereTime.day

    #default timezone to det for now
    timezone = pytz.timezone("America/Detroit")
    localNoon = timezone.localize(dt.datetime(theYear,theMonth,theDay,12))

    #set date to get MST
    QR.date =  ephem.Date(dt.datetime(theYear,theMonth,theDay,0))
    theMST = astroNow.MST(QR,now=theNow)

    #sun dial time
    QR.date =  ephem.Date(dt.datetime(theYear,theMonth,theDay,0))
    theDialTime = astroNow.dialTime(QR,now=theNow)
    deltaEqOfTime = astroNow.eqOfTime(QR)

    #unequal hour time
    QR.date =  ephem.Date(dt.datetime(theYear,theMonth,theDay,0))
    EqualTime = astroNow.unEqualTime(QR,now=theHereTime)
    EqualTimeFormat = '%s (planet: %s)' % (astroNow.formatFracHour(EqualTime['time']),EqualTime['planet'])

    QR.date = theNow
    zodiacs = astroNow.getAscendDescend(QR)

    #formated date and time
    s = astroNow.formatedNow(theHereTime)

    return jsonify({"utc" : theNow, "hereTime": theHereTime, "MST": theMST, "SunDial": theDialTime,
                      "EqOfTime": deltaEqOfTime, "Ascending" : zodiacs['ascending'], "Descending" : zodiacs['descending'],
                      "UnequalHours" : EqualTimeFormat,'header':s})

	# values stroed in list later to be passed as df while prediction


if __name__ == '__main__':
    app.run()
