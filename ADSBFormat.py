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
# Version: 0.1    Added option to include Stats
# Version: 0.2    jOption to Exclude some flights
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
MCH  = 3
SPD  = 4
SWK  = 5
HEAD = 6
LAT  = 7
LON  = 8
DIST = 9
LINK = 10

# Home Location - used to calculate distance to fligts
QTH_LAT = 'SET'
QTH_LON = 'SET'
QTH = (QTH_LAT, QTH_LON)

# Statistics we can display
DEFAULT        = "XXXX"
UNKNOWN        = "XX"

HIGH_ID        = DEFAULT
HIGH_CALL      = DEFAULT
HIGHEST        = DEFAULT
FAST_ID        = DEFAULT
FAST_CALL      = DEFAULT
FASTEST        = DEFAULT
FURT_ID        = DEFAULT
FURT_CALL      = DEFAULT
FURTHEST       = DEFAULT


NUM_AIRCRAFT      = 0
NUM_NO_POSITIONS  = 0
NUM_EXLUDED       = 0


URL = "http://localhost/tar1090/data/aircraft.json"         #Flight Data served up from URL

# Header Information
HEADER_INFO = "Current flight's tracked from SET QTH using 1090 MHz Radio ADSB transmissions\n\n"

#OARC Flight Link
FLIGHT_LINK = "https://adsb.oarc.uk/?icao="

# OARC Trailer
OARC_DETAILS = "The Online Amateur Radio Community ADSB website: https://adsb.oarc.uk/"
OARC_WIKI = "For further information about OARC Flight Tracking check here: https://wiki.oarc.uk/flight:adsb"

MACH_SPD = 1235

# Limit the number of flights to display - remember this is Packet Radio!
MAX_DISPLAY = 15

INC_STATS = True             # Include Stats. Set to False if NOT wanted.

STATS_LINK = True            # Include URL Link with Stats? Set to False if NOT wanted
FLTS_LINK  = True            # Include URL Link with Flights? Set to False if NOT wanted

#======================================================================================
# Exclude - list Id / Hex codes to exclude from Flights
EXCLUDE = ['43bf94', '43bf95', '43bf96']

#======================================================================================

def getDistance(flight_lat, flight_lon):
    dist_f = 0.0
    
    if (flight_lat):
        flight_coords = (flight_lat, flight_lon)
        distance = str(geopy.distance.geodesic(QTH, flight_coords))
        dist_f = float(f'{distance.strip(" km")}')
        dist_f = f'{dist_f: 7.2f}'
    
    return dist_f

def getSpeed(flt_mach):
    fltSpeed = 0.00
    
    if (flt_mach):
        fltSpeed = float(f'{flt_mach * MACH_SPD: 7.2f}')
    
    return fltSpeed


def printStats(fltStats, links = True):
    print("Real Time Flight information:\n")
    output1 = f'\tTotal Aircraft: {fltStats[9]}\t\tHighest:  Id: {fltStats[0]}\tCall:  {fltStats[1]}\tAltitude: {fltStats[2]}m'
    output2 = f'\tWith Positions: {fltStats[10]}\t\tFastest:  Id: {fltStats[3]}\tCall:  {fltStats[4]}\tSpeed:    {fltStats[5]}km/h'
    output3 = f'\tTotal Exluded: {fltStats[11]}\t\tFurthest: Id: {fltStats[6]}\tCall:  {fltStats[7]}\tDistance: {fltStats[8]}km'
    
    if links:
        output1 = output1 + f'\t{FLIGHT_LINK}{fltStats[0]}'
        output2 = output2 + f'\t{FLIGHT_LINK}{fltStats[3]}'
        output3 = output3 + f'\t{FLIGHT_LINK}{fltStats[6]}'
    
    print(output1)
    print(output2)
    print(output3 + '\n\n')

response = requests.get(URL)                  # Get Flight Information from URL

if response.status_code == 200:               # Success
    flights = response.json()


    schedule = []
    flight = []
    
    # Flight Stats
    highId         = 0
    highCl         = 0
    highest        = 0
    fastId         = 0
    fastCl         = 0
    fastest        = 0
    furtId         = 0
    furtCl         = 0
    furthest       = 0
    
    Stats         = [HIGH_ID, HIGH_CALL, HIGHEST, FAST_ID, FAST_CALL, FASTEST, FURT_ID, FURT_CALL, FURTHEST, NUM_AIRCRAFT, NUM_NO_POSITIONS, NUM_EXLUDED]

    for i in flights['aircraft']:
        hx       = str(i.get('hex'))
        call     = i.get('flight', 'XX')
        alt      = i.get('alt_baro', 0)
        mach     = i.get('mach', 0)
        
        speed    = getSpeed(mach)
        
        swk      = i.get('squawk', 'XX')
        hd       = str(i.get('track'))
    
        lat      = i.get('lat')
        if lat:
            lat = f'{lat:5.2f}'
        else:
            NUM_NO_POSITIONS = NUM_NO_POSITIONS + 1
    
        lon      = i.get('lon')
        if lon:
            lon = f'{lon:5.2f}'
        
        dist     = getDistance(lat, lon)
    
        link = f'{FLIGHT_LINK}{hx}'
    
        flight.append(hx)
        flight.append(call)
        flight.append(alt)
        flight.append(mach)
        flight.append(speed)
        flight.append(swk)
        flight.append(hd)
        flight.append(lat)
        flight.append(lon)
        flight.append(dist)
        flight.append(link)

    
        if hx not in EXCLUDE:                                # Do we exclude this?
            schedule.append(flight.copy())               # Add Flight data to the Schedule
            NUM_AIRCRAFT = NUM_AIRCRAFT + 1
        else:
            NUM_EXLUDED = NUM_EXLUDED + 1
        
        if alt != "ground":
            if alt > highest:
                highId = hx
                highCl = call
                highest = alt
        
        if speed > fastest:
            fastId = hx
            fastCl = call
            fastest = speed
        
        if float(dist) > float(furthest):
            furtId = hx
            furtCl = call
            furthest = dist
    
        flight.clear()                                   # Clear down the current Flight data
        
    
    # Update the Stats:
    Stats[0]  = highId
    Stats[1]  = highCl
    Stats[2]  = highest
    Stats[3]  = fastId
    Stats[4]  = fastCl
    Stats[5]  = fastest
    Stats[6]  = furtId
    Stats[7]  = furtCl
    Stats[8]  = furthest
    Stats[9]  = len(schedule)
    Stats[10] = NUM_NO_POSITIONS
    Stats[11] = NUM_EXLUDED    
    
    sortedSchedule = sorted(schedule, key=itemgetter(DIST))                        # Sort the Flight Schedule by Distance (Field 7)

    print(HEADER_INFO)

    if INC_STATS:
        printStats(Stats, STATS_LINK)

    l = 0

    for k in sortedSchedule:
        output = f'Id: {k[HEX]}\tCall: {k[CALL]}\tAlt: {k[ALT]}\tSquawk: {k[SWK]}\tSpeed: {k[SPD]}\tHeading: {k[HEAD]}\tLat {k[LAT]} Lon: {k[LON]}\tDistance: {k[DIST]}km'
        
        if FLTS_LINK:
            output = output + f'\t{k[LINK]}'
        
        print(output)
    
        l = l + 1
        if l >= MAX_DISPLAY:
            break
    print("\n\n" + OARC_WIKI + "\n\n" + OARC_DETAILS)
else:
    print("I'm sorry but I've been unable to retrieve Flight details right now.\n Please try again later.")
