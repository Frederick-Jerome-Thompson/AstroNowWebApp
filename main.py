from flask import Flask, render_template, flash, request, jsonify, Markup



import logging, io, os, sys





import pytz
import Planet_Tools, pyEph_Tools, ephem, astroNow
import datetime as dt

import random



app = Flask(__name__)
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = False #needed to stop errors...
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0 #no caching because of image stuff




@app.before_first_request
def startup():
  global QR
  QR = ephem.Observer()
  QR.lon, QR.lat = '-83:09:31', '42:31:26'



@app.route("/")
def hello():

    return render_template( 'index.html')



#moon report
@app.route("/moon_report")
def getMoonData():
    #default timezone to det for now
    timezone = pytz.timezone("America/Detroit")

# read in lat and lon

    hasLatLon = False

    reqLat = request.args.get('lat')
    reqLon = request.args.get('lon')

    if ((reqLat != None) and (reqLon != None)):
      QR.lon = reqLon
      QR.lat = reqLat

#read time in    
    hasTime=False
    reqTime = request.args.get('time')
    if (reqTime != None):

      hasTime = True
      try:
          reqTime = dt.datetime.strptime(reqTime, '%Y%m%d_%H:%M:%S')
      except ValueError:
          hasTime = False


    theNow = astroNow.utcnow()    
    theHereTime = astroNow.detnow()

    if (hasTime):
      theHereTime = timezone.localize(reqTime, is_dst=None)
      theNow = theHereTime.astimezone(pytz.utc)
    

    MR = astroNow.moonReport(QR,timezone)
    

    return  jsonify(astroNow.fndMoonPeaks(MR))


#data section

@app.route("/data")
def getData():
    #default timezone to det for now
    timezone = pytz.timezone("America/Detroit")

# read in lat and lon

    hasLatLon = False

    reqLat = request.args.get('lat')
    reqLon = request.args.get('lon')

    if ((reqLat != None) and (reqLon != None)):
      QR.lon = reqLon
      QR.lat = reqLat

#read time in    
    hasTime=False
    reqTime = request.args.get('time')
    if (reqTime != None):

      hasTime = True
      try:
          reqTime = dt.datetime.strptime(reqTime, '%Y%m%d_%H:%M:%S')
      except ValueError:
          hasTime = False


    theNow = astroNow.utcnow()    
    theHereTime = astroNow.detnow()

    if (hasTime):
      theHereTime = timezone.localize(reqTime, is_dst=None)
      theNow = theHereTime.astimezone(pytz.utc)
    
    #planets as list
    planets = [ephem.Sun(),ephem.Moon(),ephem.Mars(),ephem.Mercury(),ephem.Jupiter(),ephem.Venus(),ephem.Saturn()]
    planetData = [astroNow.planetData(QR,thePlanet) for thePlanet in planets]

    return  jsonify(planetData)


# uses query string to get time, (lat,lon) if either is available 
@app.route('/background_process', methods=['POST', 'GET'])
def background_process():

    #default timezone to det for now
    timezone = pytz.timezone("America/Detroit")

# read in lat and lon

    hasLatLon = False

    reqLat = request.args.get('lat')
    reqLon = request.args.get('lon')

    if ((reqLat != None) and (reqLon != None)):
      QR.lon = reqLon
      QR.lat = reqLat





#read time in    
    hasTime=False
    reqTime = request.args.get('time')
    if (reqTime != None):

      hasTime = True
      try:
          reqTime = dt.datetime.strptime(reqTime, '%Y%m%d_%H:%M:%S')
      except ValueError:
          hasTime = False


    theNow = astroNow.utcnow()    
    theHereTime = astroNow.detnow()

    if (hasTime):
      theHereTime = timezone.localize(reqTime, is_dst=None)
      theNow = theHereTime.astimezone(pytz.utc)



    theYear = theHereTime.year
    theMonth = theHereTime.month
    theDay = theHereTime.day

    #local noon
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

    return jsonify({"request": reqTime, "utc" : theNow, "hereTime": theHereTime, "MST": theMST, "SunDial": theDialTime,
                      "EqOfTime": deltaEqOfTime, "Ascending" : zodiacs['ascending'], "Descending" : zodiacs['descending'],
                      "UnequalHours" : EqualTimeFormat,'header':s})

	# values stroed in list later to be passed as df while prediction


if __name__ == '__main__':
    app.run()
