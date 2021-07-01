import ephem
import datetime as dt
import pandas as pd

from itertools import permutations
from itertools import combinations
from scipy.misc import derivative
import scipy.optimize as optimize




def getLocDate(aDate, tDelta): #bad name but works
    d = ephem.Date(aDate)
    d = d + tDelta
    return(ephem.Date(d))


def pullEph_ra_dec(QR):
    m,t,w,th,f,sa,su = ephem.Moon(), ephem.Mars(), ephem.Mercury(), \
        ephem.Jupiter(), ephem.Venus(), ephem.Saturn(), ephem.Sun()
        
    m.compute(QR);t.compute(QR);w.compute(QR);th.compute(QR)
    f.compute(QR);sa.compute(QR);su.compute(QR)
    
    
    return({'Moon': (m.ra,m.dec),'Mars':(t.ra,t.dec),'Mercury':(w.ra,w.dec),'Jupiter':(th.ra,th.dec),\
            'Venus':(f.ra,f.dec),'Saturn':(sa.ra,sa.dec),'Sun':(su.ra,su.dec)})




def getAll_ra_dec(QR,aDate,tDelta):
    QR.date = getLocDate(aDate,tDelta)
    #{'Moon': m.ra,'Mars':t.ra,'Mercury':w.ra,'Jupiter':th.ra,'Venus':f.ra,'Saturn':sa.ra,'Sun':su.ra})

    anEph = pullEph_ra_dec(QR)
    return({'date':aDate, 'Moon':[anEph['Moon']], 'Mars':[anEph['Mars']], 'Mercury':[anEph['Mercury']], \
            'Jupiter':[anEph['Jupiter']],'Venus':[anEph['Venus']], 'Saturn':[anEph['Saturn']], 'Sun':[anEph['Sun']]})






def sourcePlanets_ra_dec(aDteTm = dt.datetime.now(), aLoc=('-83:09:31', '42:31:26' )):
    lat, lon = aLoc[1], aLoc[0]
    
    QR = ephem.Observer()
    QR.lon, QR.lat = lon, lat #'-84.39733', '33.775867' #
    
    
    d = ephem.Date('1970/12/29 17:22:00')
    e = ephem.Date(ephem.localtime(d))
    tDelta = d - e

    
    theDate = aDteTm.strftime("%Y/%m/%d %H:%M:%S")
    return(getAll_ra_dec(QR,theDate,tDelta))



