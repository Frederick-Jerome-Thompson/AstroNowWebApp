import ephem
import datetime as dt
import pandas as pd
from math import pi
from itertools import permutations
from itertools import combinations
from scipy.misc import derivative
import scipy.optimize as optimize


def localTD(aLoc=('-83:09:31', '42:31:26')):
    lat, lon = aLoc[1], aLoc[0]

    QR = ephem.Observer()
    QR.lon, QR.lat = lon, lat  #'-84.39733', '33.775867' #

    d = ephem.Date('1970/12/29 17:22:00')
    e = ephem.Date(ephem.localtime(d))
    tDelta = d - e
    return (tDelta)


def getLocDate(aDate, tDelta=localTD()):  #bad name but works
    d = ephem.Date(aDate)
    d = d + tDelta
    return (ephem.Date(d))


def pullEph(QR):
    m,t,w,th,f,sa,su = ephem.Moon(), ephem.Mars(), ephem.Mercury(), \
        ephem.Jupiter(), ephem.Venus(), ephem.Saturn(), ephem.Sun()

    m.compute(QR)
    t.compute(QR)
    w.compute(QR)
    th.compute(QR)
    f.compute(QR)
    sa.compute(QR)
    su.compute(QR)


    return({'Moon': m.ra,'Mars':t.ra,'Mercury':w.ra,'Jupiter':th.ra,\
            'Venus':f.ra,'Saturn':sa.ra,'Sun':su.ra})


def pullEph_ra_dec(QR):
    m,t,w,th,f,sa,su = ephem.Moon(), ephem.Mars(), ephem.Mercury(), \
        ephem.Jupiter(), ephem.Venus(), ephem.Saturn(), ephem.Sun()

    m.compute(QR)
    t.compute(QR)
    w.compute(QR)
    th.compute(QR)
    f.compute(QR)
    sa.compute(QR)
    su.compute(QR)


    return({'Moon': (m.ra,m.dec),'Mars':(t.ra,t.dec),'Mercury':(w.ra,w.dec),'Jupiter':(th.ra,th.dec),\
            'Venus':(f.ra,f.dec),'Saturn':(sa.ra,sa.dec),'Sun':(su.ra,su.dec)})


def makeDate(aDate):
    month, day, year = aDate.split("/")
    theDate = dt.date(int(year), int(month), int(day))
    return (theDate)


def convDate(aDate):
    month, day, year = aDate.split("/")
    theDate = dt.date(int(year), int(month), int(day))
    return (theDate.strftime('%Y-%m-%d') + " 12:00")


def convDate_Plus1(aDate):
    month, day, year = aDate.split("/")
    theDate = dt.date(int(year), int(month), int(day)) + dt.timedelta(days=1)
    return (theDate.strftime('%Y-%m-%d') + " 12:00")


def convDate_Eph(aDate):
    month, day, year = aDate.split("/")
    theDate = dt.date(int(year), int(month), int(day))
    return (theDate.strftime('%Y/%m/%d') + " 12:00")


def getAllEph(QR, aDate, tDelta):
    QR.date = getLocDate(aDate, tDelta)
    #{'Moon': m.ra,'Mars':t.ra,'Mercury':w.ra,'Jupiter':th.ra,'Venus':f.ra,'Saturn':sa.ra,'Sun':su.ra})

    anEph = pullEph(QR)
    return({'date':aDate, 'Moon':[anEph['Moon']*12/pi], 'Mars':[anEph['Mars']*12/pi], 'Mercury':[anEph['Mercury']*12/pi], \
            'Jupiter':[anEph['Jupiter']*12/pi],'Venus':[anEph['Venus']*12/pi], 'Saturn':[anEph['Saturn']*12/pi], 'Sun':[anEph['Sun']*12/pi]})


def getAll_ra_dec(QR, aDate, tDelta):
    QR.date = getLocDate(aDate, tDelta)
    #{'Moon': m.ra,'Mars':t.ra,'Mercury':w.ra,'Jupiter':th.ra,'Venus':f.ra,'Saturn':sa.ra,'Sun':su.ra})

    anEph = pullEph_ra_dec(QR)
    return({'date':aDate, 'Moon':[anEph['Moon']], 'Mars':[anEph['Mars']], 'Mercury':[anEph['Mercury']], \
            'Jupiter':[anEph['Jupiter']],'Venus':[anEph['Venus']], 'Saturn':[anEph['Saturn']], 'Sun':[anEph['Sun']]})


def sourceAnEphemerisOld(aDteTm, aLoc=('-83:09:31', '42:31:26')):
    lat, lon = aLoc[1], aLoc[0]

    QR = ephem.Observer()
    QR.lon, QR.lat = lon, lat  #'-84.39733', '33.775867' #

    d = ephem.Date('1970/12/29 17:22:00')
    e = ephem.Date(ephem.localtime(d))
    tDelta = d - e

    #theDate = aDteTm.strftime("%Y/%m/%d %H:%M:%S")
    return (getAllEph(QR, aDteTm, tDelta))


def sourceAnEphemeris(aDteTm=dt.datetime.now(), aLoc=('-83:09:31',
                                                      '42:31:26')):
    lat, lon = aLoc[1], aLoc[0]

    QR = ephem.Observer()
    QR.lon, QR.lat = lon, lat  #'-84.39733', '33.775867' #

    d = ephem.Date('1970/12/29 17:22:00')
    e = ephem.Date(ephem.localtime(d))
    tDelta = d - e

    theDate = aDteTm.strftime("%Y/%m/%d %H:%M:%S")
    return (getAllEph(QR, theDate, tDelta))


def sourcePlanets_ra_dec(aDteTm=dt.datetime.now(),
                         aLoc=('-83:09:31', '42:31:26')):
    lat, lon = aLoc[1], aLoc[0]

    QR = ephem.Observer()
    QR.lon, QR.lat = lon, lat  #'-84.39733', '33.775867' #

    d = ephem.Date('1970/12/29 17:22:00')
    e = ephem.Date(ephem.localtime(d))
    tDelta = d - e

    theDate = aDteTm.strftime("%Y/%m/%d %H:%M:%S")
    return (getAll_ra_dec(QR, theDate, tDelta))


def closeCir(ra, rb, f):  #determines closeness on circle
    d1 = (ra - rb) % f
    d2 = (rb - ra) % f
    return (min(d1, d2))


def fndGradeDelta(begSecs, func, arg, step):

    day_seconds = 24 * 60 * 60
    baseDate = dt.datetime(1900, 1, 1, 0, 0, 0)
    theRate = func(begSecs, arg)

    delta = 1.0
    sng = -1.0
    if (theRate > 0):
        delta = -1.0
        sng = 1.0

    while sng * delta < 0:
        begSecs = begSecs + step * delta * day_seconds
        theRate = func(begSecs, arg)
        sng = -1.0
        if (theRate > 0): sng = 1.0

    return (begSecs)


def findStations(aPlanet, nowSecs):

    baseDate = dt.datetime(1900, 1, 1, 0, 0, 0)
    ####find forward station
    eSecs = fndGradeDelta(nowSecs, raRate, aPlanet, 7.0)
    stationSeconds = optimize.bisect(raRate, nowSecs, eSecs, args=(aPlanet, ))
    aStationDate = baseDate + pd.to_timedelta(stationSeconds, unit='s')

    ####find backward station
    eSecs = fndGradeDelta(nowSecs, raRate, aPlanet, -7.0)
    stationSeconds = optimize.bisect(raRate, nowSecs, eSecs, args=(aPlanet, ))
    bStationDate = baseDate + pd.to_timedelta(stationSeconds, unit='s')

    return ((bStationDate, aStationDate))


def fndBDelta(begSecs, func, args, step, sep):

    day_seconds = 24 * 60 * 60
    baseDate = dt.datetime(1900, 1, 1, 0, 0, 0)
    rate = func(begSecs, args[0], args[1])

    sng = -1.0
    if (rate > 0): sng = 1.0
    
    if sep == "diverging": step = -1*step

    while sng * rate > 0:
        begSecs = begSecs + step *  day_seconds
        rate = func(begSecs, args[0], args[1])

    return (begSecs)

def fndRateDelta(begSecs, func, args, step):

    day_seconds = 24 * 60 * 60
    baseDate = dt.datetime(1900, 1, 1, 0, 0, 0)
    theRate = func(begSecs, args[0], args[1])

    delta = 1.0
    sng = -1.0
    if (theRate > 0):
        delta = -1.0
        sng = 1.0

    while sng * delta < 0:
        begSecs = begSecs + step * delta * day_seconds
        theRate = func(begSecs, args[0], args[1])
        sng = -1.0
        if (theRate > 0): sng = 1.0

    return (begSecs)

def fndRateDelta_P(begSecs, func, args, step):

    day_seconds = 24 * 60 * 60
    baseDate = dt.datetime(1900, 1, 1, 0, 0, 0)
    theRate = func(begSecs, args[0], args[1],args[2])

    delta = 1.0
    sng = -1.0
    if (theRate > 0):
        delta = -1.0
        sng = 1.0

    while sng * delta < 0:
        begSecs = begSecs + step * delta * day_seconds
        theRate = func(begSecs, args[0], args[1],args[2])
        sng = -1.0
        if (theRate > 0): sng = 1.0

    return (begSecs)

def checkConjuncs(anEph):  #within ephemeris, what is close and near conjunction(10degrees)
    planets = ['Moon', 'Mars', 'Mercury', 'Jupiter', 'Venus', 'Saturn', 'Sun']
################
###get all combos to check if two planets are near by or near opposites
    perm = combinations(planets, 2)
    aDte = dt.datetime.strptime(anEph['date'], '%Y/%m/%d %H:%M:%S')
    nowTd = aDte - dt.datetime(1900, 1, 1, 0, 0, 0)
    for i in list(perm): #sort throught combos
        aPlanet = i[0]
        ra = anEph[aPlanet][0]
        bPlanet = i[1]
        rb = anEph[bPlanet][0]

        #print('for %s (%3.2f) and %s (%3.2f), the delta is: %3.2f' % (aPlanet,ra*360/24, bPlanet,rb*360/24, closeCir(ra,rb,24)*360/24))
        if closeCir(ra, rb, 24) * 360 / 24 < 10:
            sep = convPlans(anEph['date'], aPlanet, bPlanet)
            outTd = dt.timedelta(
                seconds=fndRateDelta(nowTd.total_seconds(), sepRate, (
                    aPlanet,
                    bPlanet,
                ), .25))
            outDate = dt.datetime(1900, 1, 1, 0, 0, 0) + outTd
            if outDate < aDte:
                conjuncSeconds = optimize.bisect(
                    sepRate,
                    outTd.total_seconds(),
                    nowTd.total_seconds(),
                    args=(
                        aPlanet,
                        bPlanet,
                    ))
            else:
                conjuncSeconds = optimize.bisect(
                    sepRate,
                    nowTd.total_seconds(),
                    outTd.total_seconds(),
                    args=(
                        aPlanet,
                        bPlanet,
                    ))

            conjDate = dt.datetime(1900, 1, 1, 0, 0,
                                   0) + dt.timedelta(seconds=conjuncSeconds)
            ra_conj = retroRA(conjuncSeconds, aPlanet)
            rb_conj = retroRA(conjuncSeconds, bPlanet)
            if closeCir(ra_conj, rb_conj, 24) * 360 / 24 < 0.5:
                print(
                    'On %s, %s (%2.2f) and %s (%2.2f) are close (separation: %3.2f degrees) and %s (conjunction: %s)'
                    % (anEph['date'], aPlanet, ra, bPlanet, rb,
                       closeCir(ra, rb, 24) * 360 / 24, sep,
                       conjDate.strftime('%Y-%m-%d %H:%M:%S')))
            else:
                print(
                    'On %s, %s (%2.2f) and %s (%2.2f) are close (separation: %3.2f degrees) and %s (nearest on : %s)'
                    % (anEph['date'], aPlanet, ra, bPlanet, rb,
                       closeCir(ra, rb, 24) * 360 / 24, sep,
                       conjDate.strftime('%Y-%m-%d %H:%M:%S')))
#oppositin
        if closeCir(ra, rb + 12, 24) * 360 / 24 < 10:
            sep = convPlans(anEph['date'], aPlanet, bPlanet)
            outTd = dt.timedelta(
                seconds=fndRateDelta_P(nowTd.total_seconds(), sepRate_phase, (
                    aPlanet,
                    bPlanet,12,
                ), .25))
            outDate = dt.datetime(1900, 1, 1, 0, 0, 0) + outTd
            if outDate < aDte:
                oppositionSeconds = optimize.bisect(
                    sepRate_phase,
                    outTd.total_seconds(),
                    nowTd.total_seconds(),
                    args=(
                        aPlanet,
                        bPlanet,
                        12,
                    ),
                    maxiter=1000)
            else:
                oppositionSeconds = optimize.bisect(
                    sepRate_phase,
                    nowTd.total_seconds(),
                    outTd.total_seconds(),
                    args=(
                        aPlanet,
                        bPlanet,
                        12,
                    ),
                    maxiter=1000)
            oppoDate = dt.datetime(1900, 1, 1, 0, 0,
                                   0) + dt.timedelta(seconds=oppositionSeconds)

            ra_conj = retroRA(oppositionSeconds, aPlanet)
            rb_conj = retroRA(oppositionSeconds, bPlanet)
            if closeCir(ra_conj, rb_conj, 24) * 360 / 24 < 0.5:
                print(
                    'On %s, %s (%2.2f) and %s (%2.2f) are close to opposition (separation: %3.2f degrees) and %s (opposition: %s)'
                    % (anEph['date'], aPlanet, ra, bPlanet, rb,
                       closeCir(ra, rb, 24) * 360 / 24, sep,
                       oppoDate.strftime('%Y-%m-%d %H:%M:%S')))
            else:
                print(
                    'On %s, %s (%2.2f) and %s (%2.2f) are close to opposition (separation: %3.2f degrees) and %s (nearest opposition: %s)'
                    % (anEph['date'], aPlanet, ra, bPlanet, rb,
                       closeCir(ra, rb, 24) * 360 / 24, sep,
                       oppoDate.strftime('%Y-%m-%d %H:%M:%S')))

            #print('search date: %s' % outDate.strftime('%Y-%m-%d %H:%M:%S'))
            print(
                'On %s, %s (%2.2f) and %s (%2.2f) are close to opposition (separation: %3.2f degrees) and %s (opposition: %s)'
                % (anEph['date'], aPlanet, ra, bPlanet, rb,
                   closeCir(ra, rb, 24) * 360 / 24, sep,
                   oppoDate.strftime('%Y-%m-%d %H:%M:%S')))


#new Check Conjuncs
def recordConjuncs(anEph, conjuncs={}):  
    #within ephemeris, what is close and near conjunction(10degrees)
    planets = ['Moon', 'Mars', 'Mercury', 'Jupiter', 'Venus', 'Saturn', 'Sun']
    perm = combinations(planets, 2)
    aDte = dt.datetime.strptime(anEph['date'], '%Y/%m/%d %H:%M:%S')
    nowTd = aDte - dt.datetime(1900, 1, 1, 0, 0, 0)
    for i in list(perm):
        aPlanet = i[0]
        ra = anEph[aPlanet][0]
        bPlanet = i[1]
        rb = anEph[bPlanet][0]

        #print('for %s (%3.2f) and %s (%3.2f), the delta is: %3.2f' % (aPlanet,ra*360/24, bPlanet,rb*360/24, closeCir(ra,rb,24)*360/24))
        if closeCir(ra, rb, 24) * 360 / 24 < 10:
            sep = convPlans(anEph['date'], aPlanet, bPlanet)
            #fndBDelta(begSecs, func, args, step, sep)
            outTd = dt.timedelta(
                seconds=fndBDelta(nowTd.total_seconds(), bSep, (
                    aPlanet,
                    bPlanet,
                ), 1,sep))
            outDate = dt.datetime(1900, 1, 1, 0, 0, 0) + outTd
            #print('out date is: %s for planets %s and %s' % (outDate,aPlanet,bPlanet))
            if outDate < aDte:
                #optimize.minimize_scalar(retroDeg,args=(aPlanet,deg), bounds=(nowSecs,eSecs),method="bounded")
                #optimize.bisect(sepRate,  outTd.total_seconds(),nowTd.total_seconds(),args= (aPlanet,bPlanet,))
                conjuncSeconds = optimize.minimize_scalar(
                    bSep,
                    bounds=(outTd.total_seconds(), nowTd.total_seconds()),
                    args=(
                        aPlanet,
                        bPlanet,
                    ),
                    method="bounded").x
            else:
                #conjuncSeconds = optimize.bisect(sepRate, nowTd.total_seconds(), outTd.total_seconds(),args= (aPlanet,bPlanet,))
                conjuncSeconds = optimize.minimize_scalar(
                    bSep,
                    bounds=(nowTd.total_seconds(), outTd.total_seconds()),
                    args=(
                        aPlanet,
                        bPlanet,
                    ),
                    method="bounded").x
            conjDate = dt.datetime(1900, 1, 1, 0, 0,
                                   0) + dt.timedelta(seconds=conjuncSeconds)
            conjunc = {
                'date': conjDate,
                'aPlanet': aPlanet,
                'bPlanet': bPlanet,
                'align': 'conjunct'
            }
            pKey = aPlanet + bPlanet
            conjuncs[pKey] = conjunc

        if closeCir(ra, rb + 12, 24) * 360 / 24 < 10:
            sep = convPlans(anEph['date'], aPlanet, bPlanet)
            outTd = dt.timedelta(
                seconds=fndRateDelta(nowTd.total_seconds(), sepRate, (
                    aPlanet,
                    bPlanet,
                ), 7))
            outDate = dt.datetime(1900, 1, 1, 0, 0, 0) + outTd
            if outDate < aDte:
                #                oppositionSeconds = optimize.bisect(sepRate_phase,  outTd.total_seconds(),nowTd.total_seconds(),args= (aPlanet,bPlanet,12,))
                oppositionSeconds = optimize.minimize_scalar(
                    sepRate_phase,
                    bounds=(outTd.total_seconds(), nowTd.total_seconds()),
                    args=(
                        aPlanet,
                        bPlanet,
                        12,
                    ),
                    method="bounded").x

            else:
                #oppositionSeconds = optimize.bisect(sepRate_phase, nowTd.total_seconds(), outTd.total_seconds(),args= (aPlanet,bPlanet,12, ))
                oppositionSeconds = optimize.minimize_scalar(
                    sepRate_phase,
                    bounds=(nowTd.total_seconds(), outTd.total_seconds()),
                    args=(
                        aPlanet,
                        bPlanet,
                        12,
                    ),
                    method="bounded").x
            oppoDate = dt.datetime(1900, 1, 1, 0, 0,
                                   0) + dt.timedelta(seconds=oppositionSeconds)
            conjunc = {
                'date': oppoDate,
                'aPlanet': aPlanet,
                'bPlanet': bPlanet,
                'align': 'opposed'
            }
            pKey = aPlanet + bPlanet
            conjuncs[pKey] = conjunc

    return (conjuncs)


#this function has the datetime and planet as argument for finding RA
def retroFun(aDte, aPlanet):
    anEph = sourceAnEphemeris(aDte)
    return (anEph[aPlanet])


#this function converts RA funciton of datetime and planet to
#specific planet and seconds since 1900/1/1 0:00 UTC


def retroRA(aSecs, aPlanet):
    aTd = pd.to_timedelta(int(aSecs), unit='s')
    aDte = aTd + dt.datetime(1900, 1, 1, 0, 0, 0)
    return (retroFun(aDte, aPlanet)[0])


#derivative of the RA  function
def raRate(aSecs, aPlanet):
    return (derivative(retroRA, aSecs, args=(aPlanet, )))


#functional separation that can be differentiated
def sepRate_phase(aSecs, aPlanet, bPlanet, phase):
    return (derivative(aSep_phase, aSecs, args=(
        aPlanet,
        bPlanet,
        phase,
    )))


#functional separation that can be differentiated
def sepRate(aSecs, aPlanet, bPlanet):
    return (derivative(aSep, aSecs, args=(
        aPlanet,
        bPlanet,
    )))


def convPlans(aDte, aPlanet, bPlanet):
    aDte = dt.datetime.strptime(aDte, '%Y/%m/%d %H:%M:%S')
    aTd = aDte - dt.datetime(1900, 1, 1, 0, 0, 0)
    delta = sepRate(float(aTd.total_seconds()), aPlanet, bPlanet)
    sep = "converging"
    if delta > 0.0:
        sep = "diverging"
    return (sep)


#functional separation that can be differentiated
def aSep(aSecs, aPlanet, bPlanet):
    ra = retroRA(aSecs, aPlanet)
    rb = retroRA(aSecs, bPlanet)
    return (closeCir(ra, rb, 24))


def bSep(aSecs, aPlanet, bPlanet):
    ra = retroRA(aSecs, aPlanet)
    rb = retroRA(aSecs, bPlanet)
    d = ra - rb
    if d > 12: d=d-24
    if d < -12: d=d+24
    return (ra-rb)

#functional separation that can be differentiated
def aSep_phase(aSecs, aPlanet, bPlanet, phase):
    ra = retroRA(aSecs, aPlanet)
    rb = retroRA(aSecs, bPlanet) + phase
    return (closeCir(ra, rb, 24))


def astroGrade(aSecs, aPlanet):
    grade = 'P'
    if ((derivative(retroRA, aSecs, args=(aPlanet, ))) < 0): grade = 'R'
    return (grade)






###general functions that take ephem objecst and give results
###used to find conjuction and opposition, as well as phase

###################################
#general separation functions

#return planet separation from date-time input
def planetSep(theDate, QR, a, b):
    QR.date = theDate.strftime("%Y/%m/%d %H:%M:%S")
    a.compute(QR)
    b.compute(QR)
    return(ephem.separation(a,b))

#return planet separation from elapsed seconds from 1900/1/1
def planetSepSecs(theSecs, QR, a, b):
    aTd = pd.to_timedelta(int(theSecs), unit='s')
    theDate = aTd + dt.datetime(1900, 1, 1, 0, 0, 0) #base date
    QR.date = theDate.strftime("%Y/%m/%d %H:%M:%S")
    a.compute(QR)
    b.compute(QR)
    return(ephem.separation(a,b))

#return planet separation minus phase from elapsed seconds from 1900/1/1
#output is squared in defualt to be minimized in optimization routine
#can set eponent to anything, and will be 1 to find root
def planetSepPhaseSecs(theSecs, QR, a, b, aPhase, aInt = 2):
    aTd = pd.to_timedelta(int(theSecs), unit='s')
    theDate = aTd + dt.datetime(1900, 1, 1, 0, 0, 0) #base date
    QR.date = theDate.strftime("%Y/%m/%d %H:%M:%S")
    a.compute(QR)
    b.compute(QR)
    return((ephem.separation(a,b)-aPhase)**aInt)

#find the switch in sign for fabove function.  to find phase root
def fndSignSwitch(begSecs,func,QR,a,b,aPhase, step=60*60):
    startSign = 1
    if func(begSecs,QR,a,b,aPhase,1) < 0:
        startSign = -1
    
    delta = -1* startSign
    
    while startSign * delta < 0:
        begSecs = begSecs + step 
        theRate = func(begSecs,QR,a,b,aPhase,1)
        startSign = -1.0
        if (theRate > 0): startSign = 1.0

    return (begSecs+step*2)
    
#find derivative of sparation
def planetSepRate(aSecs,QR,a,b):
    return (derivative(planetSepSecs, aSecs, args=[QR,a,b,]))

#find change in derivative
def fndRateSwitch(begSecs,func,QR,a,b, step=24*60*60):
    startSign = 1
    if func(begSecs,QR,a,b) < 0:
        startSign = -1
    
    delta = -1* startSign
    
    while startSign * delta < 0:
        begSecs = begSecs + step 
        theRate = func(begSecs,QR,a,b)
        startSign = -1.0
        if (theRate > 0): startSign = 1.0

    return (begSecs)
    
#utilitiy to take seconds to date
def secs2date(secs, basedate = dt.datetime(1900,1,1,0,0,0)):
    return(basedate + dt.timedelta(seconds=secs))



