import ephem
import datetime as dt
from math import pi

import calendar
import pytz

from timezonefinder import TimezoneFinder
from pytz import timezone, utc


zodiac = {'Aries':[0,30],
          'Taurus':[30,60],
          'Gemini':[60,90],
          'Cancer':[90,120],
          'Leo':[120,150],
          'Virgo':[150,180],
          'Libra':[180,210],
          'Scorpio':[210,240],
          'Sagittarius':[240,270],
          'Capricorn':[270,300],
          'Aquarius':[300,330],
          'Picises':[330,360]
          }

zodiacName = {'Aries':'I',
          'Taurus':'II',
          'Gemini':'III',
          'Cancer':'IV',
          'Leo':'V',
          'Virgo':'VI',
          'Libra':'VII',
          'Scorpio':'VIII',
          'Sagittarius':'IX',
          'Capricorn':'X',
          'Aquarius':'XI',
          'Picises':'XII'
          }


OldHours= {
  "name": "Old Hours",
  "days": {
    "Sunday": {
      "planet": "☉",
      "hours": {
        "1": "☉",
        "2": "♀",
        "3": "☿",
        "4": "☽",
        "5": "♄",
        "6": "♃",
        "7": "♂",
        "8": "☉",
        "9": "♀",
        "10": "☿",
        "11": "☽",
        "12": "♄"
      }
    },
    "Monday": {
      "planet": "☽",
      "hours": {
        "1": "☽",
        "2": "♄",
        "3": "♃",
        "4": "♂",
        "5": "☉",
        "6": "♀",
        "7": "☿",
        "8": "☽",
        "9": "♄",
        "10": "♃",
        "11": "♂",
        "12": "☉"
      }
    },
    "Tuesday": {
      "planet": "♂",
      "hours": {
        "1": "♂",
        "2": "☉",
        "3": "♀",
        "4": "☿",
        "5": "☽",
        "6": "♄",
        "7": "♃",
        "8": "♂",
        "9": "☉",
        "10": "♀",
        "11": "☿",
        "12": "☽"
      }
    },
    "Wednesday": {
      "planet": "☿",
      "hours": {
        "1": "☿",
        "2": "☽",
        "3": "♄",
        "4": "♃",
        "5": "♂",
        "6": "☉",
        "7": "♀",
        "8": "☿",
        "9": "☽",
        "10": "♄",
        "11": "♃",
        "12": "♂"
      }
    },
    "Thursday": {
      "planet": "♃",
      "hours": {
        "1": "♃",
        "2": "♂",
        "3": "☉",
        "4": "♀",
        "5": "☿",
        "6": "☽",
        "7": "♄",
        "8": "♃",
        "9": "♂",
        "10": "☉",
        "11": "♀",
        "12": "☿"
      }
    },
    "Friday": {
      "planet": "♀",
      "hours": {
        "1": "♀",
        "2": "☿",
        "3": "☽",
        "4": "♄",
        "5": "♃",
        "6": "♂",
        "7": "☉",
        "8": "♀",
        "9": "☿",
        "10": "☽",
        "11": "♄",
        "12": "♃"
      }
    },
    "Saturday": {
      
      
      
      "planet": "♄",
      "hours": {
        "1": "♄",
        "2": "♃",
        "3": "♂",
        "4": "☉",
        "5": "♀",
        "6": "☿",
        "7": "☽",
        "8": "♄",
        "9": "♃",
        "10": "♂",
        "11": "☉",
        "12": "♀"
      }
      
    }
  }
}

#Datetime functions
#current utc time
def utcnow():
    return dt.datetime.now(tz=pytz.utc)
          
#returns inputed time in locations timezone
def hereTime_inpt(lat,lon,year,month,day,hour,minute,second):
  tzFind = TimezoneFinder()
  timezone_here = tzFind.timezone_at(lng=lon, lat=lat)
  d = dt.datetime(year, month, day, hour, minute, second)
  # e = d.astimezone(pytz.timezone(timezone_here))
  e = d.replace(tzinfo=pytz.timezone(timezone_here))

  return e

#finds timezone for place, returns time in that zone
def herenow(lat,lon):
  tzFind = TimezoneFinder()
  timezone_here = tzFind.timezone_at(lng=lon, lat=lat)
  local_here = pytz.timezone(timezone_here)

  return dt.datetime.now(local_here)

#returns current time in detroit
def detnow():
    return dt.datetime.now(tz=pytz.timezone('America/Detroit'))
          
#returns datetime with detroit timezone from another datetime
def detTime_inpt(d):

  target_timezone = pytz.timezone('US/Eastern')
  target_datetime = d.astimezone(target_timezone)

  return target_datetime

def utcTime_inpt(d):

  target_datetime = d.astimezone(pytz.utc)

  return target_datetime

#mean solar time
def MST(observerQR, now = utcnow()):
    decimalLong = convertDegMinSec2DegDec(observerQR.long)
    return localmeantime(now, decimalLong).astimezone(pytz.utc)

def dialTime(observerQR,now=utcnow()):
    decimalLong = convertDegMinSec2DegDec(observerQR.long)
    delta = eqOfTime(observerQR)
    return localmeantime(now, decimalLong).astimezone(pytz.utc) + dt.timedelta(seconds=round(delta))



def eqHour(now,beg,end,index):
    #beg is start of period, end is end e.g., set to antitransit
    #index is which period: 1:morning, 2:afternoon, 3:evening, 4: night.
    #index afternoon and night are post meridian and get 6 extra hours

    anHourIs = (end-beg) / 6
    theHourIs = ((now - beg) / anHourIs) + 6*(1- index % 2 ) +1

    return theHourIs




def localmeantime(utc, longitude):
    """
    :param utc: string Ex. '2008-12-2'
    :param longitude: longitude
    :return: Local Mean Time Timestamp
    """
    lmt = utc + dt.timedelta(seconds=round(4*60*longitude))
    lmt = lmt.replace(tzinfo=None)
    return lmt
  
def noTZDiff(aDt,bDt):
    aYear = aDt.year
    aMonth = aDt.month
    aDay = aDt.day
    aHour = aDt.hour
    aMinute = aDt.minute
    aSecond = aDt.second

    bYear = bDt.year
    bMonth = bDt.month
    bDay = bDt.day
    bHour = bDt.hour
    bMinute = bDt.minute
    bSecond = bDt.second

    return ((aYear-bYear) * 365*24*60 + (aMonth-bMonth) *30*24*60 + (aDay-bDay)*24*60 + (aHour-bHour)*60 + (aMinute-bMinute))*60 + aSecond-bSecond

def formatFracHour(delta):
    sgn = abs(delta)/delta

    delta = abs(delta)
    hrs = int(delta)
    delta = (delta - hrs)*60

    mins = int(delta)
    secs = (delta - mins) * 60

    if sgn==1:
      s ='%d:%02d:%02d' % (hrs,mins,secs)
    else:
      s = '-%d:%02d:%02d' % (hrs,mins,secs)

    return s
def mkMinSec(delta):
    sgn = 1
    if delta<0: sgn=-1
    delta = abs(delta)
    mins = int(delta / 60)
    secs = delta % 60

    if sgn==1:
      s ='%d:%02d' % (mins,secs)
    else:
      s = '-%d:%02d' % (mins,secs)

    return s

def mkHrMinSec(delta):
    sgn = 1
    if delta<0: sgn=-1
    delta = abs(delta)
    hrs = int(delta/3600)
    delta = delta % 3600
    mins = int(delta / 60)
    secs = delta % 60

    if sgn==1:
      s ='%d:%d:%02d' % (hrs,mins,secs)
    else:
      s = '-%d:%d:%02d' % (hrs,mins,secs)

    return s


def convertDegMinSec2DegDec(observerLong):
    decimalLong = 0.0
    splitLong = str(observerLong).split(":")
    for i,a in enumerate(splitLong):
      a = float(a)
      if i == 0 : b = a / abs(a)
      decimalLong = decimalLong + abs(a)*(60)**(-1*i)
    
    decimalLong = b * decimalLong

    return decimalLong


def eqOfTime(observerQR):
    # start date for next transit of sun
    date = observerQR.date.datetime()

    startStr = '%4d/%02d/%02d' % (date.year,date.month,date.day)
    noon = dt.datetime(date.year,date.month, date.day,12)
    # local longitude
    observerLong = observerQR.long

    decimalLong = convertDegMinSec2DegDec(observerLong)
    # b=0

    # splitLong = str(observerLong).split(":")
    # for i,a in enumerate(splitLong):
    #   a = float(a)
    #   if i == 0 : b = a / abs(a)
    #   decimalLong = decimalLong + abs(a)*(60)**(-1*i)
    
    # decimalLong = b * decimalLong


    #transit time in MST at decimalLong
    transTimeUTC = observerQR.next_transit(ephem.Sun(),start=startStr).datetime()
    transTimeMST = localmeantime(transTimeUTC, decimalLong).astimezone(pytz.utc)

    #equation of time
    delta = noTZDiff(noon,transTimeMST)

    return delta

def theDayOfWeek(date):
    daysOfWeek = {0:"Monday",1:"Tuesday",2:"Wednesday",3:"Thursday", 4:"Friday",5:"Saturday",6:"Sunday"}
    return daysOfWeek[date.weekday()]

def theMonthOfYear(date):
    monthsOfYear ={1:"Jannuary", 2: "February", 3: "March", 4: "April", 5: "May", 6: "June", 7: "July", 8: "August", 9: "September",
                  10: "October", 11: "November", 12: "December"}

    return monthsOfYear[date.month]

def formatedNow(theNow):
    theYear = theNow.year
    theMonth = theNow.month
    theDay = theNow.day
    theHour = theNow.hour
    theMinute = theNow.minute
    dayOfWeek = theDayOfWeek(theNow)
    monthOfYear = theMonthOfYear(theNow)

    s = 'On %s' % dayOfWeek
    s = s + ', in the year %s ' % theYear
    s = s + ', on day %s of %s' % (theDay, monthOfYear)
    s = s + ' at %s hours and %s minutes.'  % (theHour, theMinute)

    return s

def unEqualTime(observerQR,now=detnow(),timezone = pytz.timezone("America/Detroit"), hours=OldHours):

  #observerQR.date = ephem.Date(now) Assume that the QR has the "day" or 24 hour period you want
  
  QRDate = observerQR.date.datetime()

  decimalLong = convertDegMinSec2DegDec(observerQR.long)
  dayOfWeek = theDayOfWeek(observerQR.date.datetime())
  times = planetRisings(observerQR,ephem.Sun(),timezone)
  

  if (now < times[0]):
    QRDate = QRDate + dt.timedelta(days=-1)
    observerQR.date = ephem.date(QRDate)
    times = planetRisings(observerQR,ephem.Sun(),timezone)

  

  #rise, transit, set, antitransit, next rise
  
  # print('@@@@@@@@@@in unEqualTime')
  
  # for time in times:
  #   print(time.strftime("%Y-%m-%d %H:%M:%S"))

  # print('now is: %s' % now)
  if now < times[1] and now >= times[0]:
    i = 1
    hours = eqHour(now,times[i-1],times[i],i)
    theHour = str(int(eqHour(now,times[i-1],times[i],i)) )
    thePlanet = OldHours['days'][dayOfWeek]['hours'][theHour]
  elif now < times[2] and now >= times[1]:
    i = 2
    hours = eqHour(now,times[i-1],times[i],i)
    theHour = str(int(eqHour(now,times[i-1],times[i],i)) )
    thePlanet = OldHours['days'][dayOfWeek]['hours'][theHour]
  elif now < times[3] and now >= times[2]:
    i = 3
    hours = eqHour(now,times[i-1],times[i],i)
    theHour = str(int(eqHour(now,times[i-1],times[i],i)) )
    thePlanet = OldHours['days'][dayOfWeek]['hours'][theHour]
  elif now < times[4] and now >= times[3]:
    i = 4
    hours = eqHour(now,times[i-1],times[i],i)
    theHour = str(int(eqHour(now,times[i-1],times[i],i)) )
    thePlanet = OldHours['days'][dayOfWeek]['hours'][theHour]
  else:
    hours = 13
    theHour = 13
    thePlanet = "Doom!"

  # print('@@@@@@@@@@@@@@@@@@')
  return {'time':hours,'theHour': theHour, 'planet': thePlanet}

def formatPlaentRiseEtc(planetInfo):
    riseTime = planetInfo['rise']
    transTime = planetInfo['transit']
    setTime = planetInfo['set']

    s = 'rise: %s  transit: %s set: %s' % (riseTime.strftime("%Y-%m-%d %H:%M:%S"), transTime.strftime("%Y-%m-%d %H:%M:%S"), setTime.strftime("%Y-%m-%d %H:%M:%S"))
    s = s + '\r\n' + 'time to local noon: %s' % planetInfo['time2noon']
    s = s + '\r\n' + 'time from transit to setting: %s ' % planetInfo['noon2dark']
    return s

def planetRiseEtc(observerQR,planet,timezone):

    theYear,theMonth,theDay = YrMthDay(observerQR.date.datetime())
    observerQR.date =  ephem.Date(dt.datetime(theYear,theMonth,theDay,0))
    # m,t,w,th,f,sa,su = ephem.Moon(), ephem.Mars(), ephem.Mercury(), ephem.Jupiter(), ephem.Venus(), ephem.Saturn(), ephem.Sun()
    # pNames = {m:"Moon",t:"Mars",w:"Mercury",th:"Jupiter",f:"Venus",sa:"Saturn",su:"Sun"}

    startStr = '%4d/%02d/%02d' % (theYear,theMonth,theDay)

    planet.compute(observerQR)
    riseTime = observerQR.next_rising(planet,start=startStr).datetime()
    riseTime = riseTime.astimezone(timezone)

    transTimeUTC = observerQR.next_transit(planet,start=startStr).datetime()
    transTime = transTimeUTC.astimezone(timezone)

    setTime = observerQR.next_setting(planet,start=startStr).datetime()
    setTime = setTime.astimezone(timezone)


    if (setTime < riseTime): #if we get the wrong setting time.
      startStrNxt = '%4d/%02d/%02d' % nxtYrMthDay(observerQR.date.datetime())
      setTime = observerQR.next_setting(planet, start=startStrNxt).datetime()
      setTime = setTime.astimezone(timezone)
      
    antiTime = observerQR.next_antitransit(planet,start=startStr).datetime()
    antiTime = antiTime.astimezone(timezone)

    if (antiTime<riseTime):
      startStrNxt = '%4d/%02d/%02d' % nxtYrMthDay(observerQR.date.datetime())
      antiTime = observerQR.next_antitransit(planet, start=startStrNxt).datetime()
      antiTime = antiTime.astimezone(timezone)

      


    return {'rise':riseTime,'transit':transTime,'set':setTime,'anti':antiTime,'time2noon':(transTime-riseTime),'noon2dark':(setTime - transTime)}

def planetRisingsB(observerQR,planet,timezone):

    listOfTimes = []
    storeDate = observerQR.date

    theYear,theMonth,theDay = YrMthDay(observerQR.date.datetime())
    planetInfo_day = planetRiseEtc(observerQR,planet,timezone)
    




    #do next rise
    theYear,theMonth,theDay = nxtYrMthDay(dt.datetime(theYear,theMonth,theDay))
    observerQR.date =  ephem.Date(dt.datetime(theYear,theMonth,theDay,0))
    planet.compute(observerQR)

    startStr = '%4d/%02d/%02d' % nxtYrMthDay(observerQR.date.datetime())


    planetInfo_nextDay =planetRiseEtc(observerQR,planet,timezone)

    riseTime = planetInfo_day['rise']
    transTime = planetInfo_day['transit']
    setTime = planetInfo_day['set']
    antiTime = planetInfo_day['anti']
    nextRise = planetInfo_nextDay['rise']




    listOfTimes = [riseTime,transTime,setTime,antiTime,nextRise]
    observerQR.date = storeDate
    planet.compute(observerQR)

    return listOfTimes


def planetRisings(observerQR,planet,timezone):

    listOfTimes = []

    theYear,theMonth,theDay = YrMthDay(observerQR.date.datetime())
    planetInfo_day = planetRiseEtc(observerQR,planet,timezone)
    




    #do next rise
    theYear,theMonth,theDay = nxtYrMthDay(dt.datetime(theYear,theMonth,theDay))
    observerQR.date =  ephem.Date(dt.datetime(theYear,theMonth,theDay,0))
    planet.compute(observerQR)

    startStr = '%4d/%02d/%02d' % nxtYrMthDay(observerQR.date.datetime())


    planetInfo_nextDay =planetRiseEtc(observerQR,planet,timezone)

    riseTime = planetInfo_day['rise']
    transTime = planetInfo_day['transit']
    setTime = planetInfo_day['set']
    antiTime = planetInfo_day['anti']
    nextRise = planetInfo_nextDay['rise']




    listOfTimes = [riseTime,transTime,setTime,antiTime,nextRise]
    return listOfTimes

  

def YrMthDay(aDate):
    return aDate.year, aDate.month, aDate.day


def nxtYrMthDay(aDate):
    aDate = aDate + dt.timedelta(days=1)
    return aDate.year, aDate.month, aDate.day

#fixed body code for zodiac

def getAscendDescend(observerQR):

    zodiacNames = ['aries','taurus','gemini','cancer','leo','virgo','libra','scorpio','sagittarius','capricon','aquarius','picies']
    zodiacLong = [0,30,60,90,120,150,180,210,240,270,300,330] #zodiac in degrees
    zodiacLong = [zod * pi / 180 for zod in zodiacLong] #zodiac in radians
    leadZodPoints = [ephem.Ecliptic(long,0) for long in zodiacLong] #zodiac as Ecliptic coordinates
    leadZodPoints = [ephem.Equatorial(zod) for zod in leadZodPoints] #in equatorial coords (ra,dec)

    # for zod in leadZodPoints:
    #   print('ra %s dec %s' % (zod.ra,zod.dec))

    zodiac = []
    for zod in leadZodPoints:
      star = ephem.FixedBody()
      star._ra = zod.ra
      star._dec = zod.dec
      star.compute(observerQR)
      zodiac.append({'alt':star.alt,'az':star.az})

    min_but_not_zero_az =  99.0
    min_but_not_zero_az_index = 13

    max_but_not_zero_az =  0.0
    max_but_not_zero_az_index = 13

    for i,zod in enumerate(zodiac):

      if zod['alt'] >= 0 and zod['az'] < min_but_not_zero_az:
        min_but_not_zero_az = zod['az']
        min_but_not_zero_az_index = i #take the zodiac that is rising
      if zod['alt'] >= 0 and zod['az'] > max_but_not_zero_az:
        max_but_not_zero_az = zod['az']
        max_but_not_zero_az_index =  i-1 #take zodiac that is setting

    return {'ascending':zodiacNames[min_but_not_zero_az_index],'descending':zodiacNames[max_but_not_zero_az_index]}





#for astroNow Data and MoonReport

def planetData(observerQR,planet,timezone=pytz.timezone("America/Detroit")):

      storeDate = observerQR.date
      planet.compute(observerQR)
      times = planetRisingsB(observerQR,planet,timezone)

      observerQR.date = storeDate
      planet.compute(observerQR)


      newTimes = {'rise': times[0], 'transit': times[1], 'set': times[2], 'nextRise': times[3]}
      return {'name': planet.name, 'ra':planet.ra*12/pi,'dec':planet.dec*180/pi,'az':planet.az*180/pi,'alt': planet.alt*180/pi, 'zodiac': getRAZodiac(ephem.Ecliptic(planet).lon*180/pi),
              'constellation': ephem.constellation(planet)[1],'times':newTimes, 'phase': planet.phase, 'obsLat':observerQR.lat,'obsLon':observerQR.lon,'obsDate':observerQR.date}


def getRAZodiac(lon,zods=zodiac):
  for i,zod in enumerate(zods):
      if lon < zods[zod][1] and lon >= zods[zod][0]:
        return zod

def getDegZTrans(observerQR):
  degrees = [i for i in range(360)]
  degrees = [i * pi / 180 for i in degrees]
  degrees = [ephem.Ecliptic(long,0) for long in degrees] #zodiac as Ecliptic coordinates
  degrees = [ephem.Equatorial(deg) for deg in degrees] #in equatorial coords (ra,dec)

  stars = []
  minD = 180
  idx = 3000
  print('#####################')
  for i,deg in enumerate(degrees):
    star = ephem.FixedBody()
    star._ra = deg.ra
    star._dec = deg.dec
    star.compute(observerQR)
    az = star.az*180/pi

    if (az > 90  and az <= 180):
      if (minD > 180-az):
        minD = 180-az
        idx = i


  print('#####################')
  return idx

def fndMoonPeaks(moonData):
  
  ans = {}
  moons = len(moonData)


  for i in range(moons-1):

      prevMoon = moonData[i]
      curMoon = moonData[i+1]

      if prevMoon['name']=='Waning Crescent' and curMoon['name']=='Waxing Crescent':
        ans['newMoon'] =  prevMoon['date']

      if prevMoon['name']=='Waxing Crescent' and curMoon['name']=='Waxing Gibbous':
        ans['firstQuarter'] =  prevMoon['date']

      if prevMoon['name']=='Waxing Gibbous' and curMoon['name']=='Waning Gibbous':
        ans['fullMoon'] =  prevMoon['date']

      if prevMoon['name']=='Waning Gibbous' and curMoon['name']=='Waning Crescent':
        ans['thirdQuarter'] =  prevMoon['date']


  return ans


def moonReport(observerQR,timezone):
    #from https://stackoverflow.com/questions/26702144/human-readable-names-for-phases-of-the-moon-with-pyephem code was psuedo and needed to be corrected


    #definitions
    #
    # new moon: last day of a waning cresent moon
    # first quarter: last day of a waxing cresent moon
    # full moon: last day of a waxing gibbous moon
    # third quarter: last day of a wanning gibbous moon

    tau = 2.0 * ephem.pi

    moonData = []

    begDate = dt.datetime(observerQR.date.datetime().year,observerQR.date.datetime().month,observerQR.date.datetime().day,8,0,0)

    sun = ephem.Sun()
    moon = ephem.Moon()
    names = ['Waxing Crescent', 'Waxing Gibbous',
            'Waning Gibbous', 'Waning Crescent']

    for n in range(1, 31):
        s = '2021/%d/09' % n

        naive = begDate + dt.timedelta(days=n-1)
        local_dt = timezone.localize(naive, is_dst=None)
        theDate = local_dt.astimezone(pytz.utc)

        observerQR.date =  ephem.Date(theDate)

        sun.compute(observerQR)
        moon.compute(observerQR)

        sunlon = ephem.Ecliptic(sun).lon
        moonlon = ephem.Ecliptic(moon).lon

        angle = (moonlon - sunlon) % tau
        quarter = int(angle * 4.0 // tau)

        moonData.append({'n':n,'date': observerQR.date.datetime(),'name': names[quarter],'moonlon': moonlon,'sunlon':sunlon})
        #print("%s, date: %s, name: %s moon lon: %s sun lon: %s" % (n,QR.date, names[quarter], moonlon,sunlon))
    
    return moonData


 
