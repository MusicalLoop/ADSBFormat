#==================================================================
#
# ADSBFormat: Retrieves ADSB Flight data from tar1090 feed
#             parsing the JSON, sorting and then displaying
#             the results.
#
###################################################################
#
# Author: Andy Holmes (2E0IJC)
# Date:   17th November 2023
#
###################################################################

import json
import geopy.distance

from operator import itemgetter

import requests

# Field names to output with positions
# If you want to add more fields then it's easier to user a readble name than just a number
HEX  = 0
CALL = 1
ALT  = 2
SWK  = 3
HEAD = 4
LAT  = 5
LON  = 6
DIST = 7
LINK = 8

# Home Location - used to calculate distance to fligts
QTH_LAT = '55.02974'
QTH_LON = '-1.54938'
QTH = (QTH_LAT, QTH_LON)


URL = "http://radiopi/tar1090/data/aircraft.json"         #Flight Data served up from URL

# Header Information
HEADER_INFO = "Current flight's tracked from Killingworth QTH using 1090 MHz Radio ADSB transmissions\n\n"

#OARC Flight Link
FLIGHT_LINK = "https://adsb.oarc.uk/?icao="

# OARC Trailer
OARC_DETAILS = "The Online Amateur Radio Community ADSB website: https://adsb.oarc.uk/"
OARC_WIKI = "For further information about OARC Flight Tracking check here: https://wiki.oarc.uk/flight:adsb"


# Limit the number of flights to display - remember this is Packet Radio!
MAX_DISPLAY = 25

#======================================================================================


def getDistance(flight_lat, flight_lon):
    dist_f = 0.0
    
    if (flight_lat):
        flight_coords = (flight_lat, flight_lon)
        distance = str(geopy.distance.geodesic(QTH, flight_coords))
        dist_f = float(f'{distance.strip(" km")}')
        dist_f = f'{dist_f: 7.2f}'
    
    return dist_f


response = requests.get(URL)                  # Get Flight Information from URL

if response.status_code == 200:               # Success
    flights = response.json()


    schedule = []
    flight = []

    for i in flights['aircraft']:
        hx = str(i.get('hex'))
        call = i.get('flight')
        alt = i.get('alt_baro')
        swk = i.get('squawk')
        hd = str(i.get('track'))
    
        lat = i.get('lat')
        if lat:
            lat = f'{lat:5.2f}'
    
        lon = i.get('lon')
        if lon:
            lon = f'{lon:5.2f}'
        
        dist = getDistance(lat, lon)
    
        link = f'{FLIGHT_LINK}{hx}'
    
        flight.append(hx)
        flight.append(call)
        flight.append(alt)
        flight.append(swk)
        flight.append(hd)
        flight.append(lat)
        flight.append(lon)
        flight.append(dist)
        flight.append(link)

    
        if call is not None:                                          # Only record flight if it contains a Call Sign
            if float(dist) > 0.00:
                schedule.append(flight.copy())               # Add Flight data to the Schedule
    
        flight.clear()                                   # Clear down the current Flight data
    
    
    sortedSchedule = sorted(schedule, key=itemgetter(DIST))                        # Sort the Flight Schedule by Distance (Field 7)

    print(HEADER_INFO)

    l = 0

    for k in sortedSchedule:
        output = f'Id: {k[HEX]}\tCall: {k[CALL]}\tAlt: {k[ALT]}\tSquawk: {k[SWK]}\tHeading: {k[HEAD]}\tLat {k[LAT]} Lon: {k[LON]}\tDistance: {k[DIST]}km\t{k[LINK]}'
        
        print(output)
    
        l = l + 1
        if l >= MAX_DISPLAY:
            break
    
    print("\n\n" + OARC_WIKI + "\n\n" + OARC_DETAILS)
else:
    print("I'm sorry but I've been unable to retrieve Flight details right now.\n Please try again later.")
