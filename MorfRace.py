'''
Created on Jan 11, 2024

@author: Dennis
'''
import sys
from datetime import datetime, timedelta
from ReadRaceFiles import readRacFile
from Info import getInfo
from Roster import getRoster
from Export import exportRaceToHtml, exportRaceToText
from Utils import toTime, timeDeltaToMinutesSeconds, get_full_path

timeCorrection = "TOD"

def startersPlusOne(starters : int, position : int) -> int:
    return starters

def startersPlusTwo(starters : int, position : int) -> int:
    return starters + 2

def twentyPercent(starters : int, position : int) -> int:
    # add 20% of finish position but no worse than DNF (starters + 1)
    result = min(round(starters * .2) + position, starters + 1)
    return result

alphabetSoup = {'DNF':startersPlusOne,
                'DNS':startersPlusOne,
                'DSQ':startersPlusTwo,
                'OCS':startersPlusOne,
                'RAF':startersPlusOne,
                'RET':startersPlusOne,
                'WDW':startersPlusOne,
                'ZFP':twentyPercent,
                'UFD':startersPlusOne,
                'DNE':startersPlusOne}



'''
For time on distance calculate the corrected time
'''            
def timeOnDistance(elapsedTime : datetime, distance : float, rating : float):
    # round rounds .5 dowwn .. .51 up
    correction = round(distance * rating, 0)
    correctedTime = elapsedTime - timedelta(seconds = correction)
    return correctedTime

'''
For Time on Time, calculate the corrected time
'''
def timeOnTime(elapsedTime : datetime, distance : float, rating : float) -> datetime:
    tcf = 650.0 / (550.0 + rating)
    correctedTime = elapsedTime * tcf
    return correctedTime

'''
get the corrected time using the correction method (time on distance or time on time)
'''
def getCorrectedTime(elapsedTime : datetime, distance : float, rating : float) -> datetime:
    correctionMethod = {'TOD':timeOnDistance, 'TOT': timeOnTime}
    correctedTime = correctionMethod[timeCorrection](elapsedTime, distance, rating)
    return correctedTime
    
'''
read the race data and 
calculate the corrected time for each boat
'''
def calculateCorrectedTime(entries : [], sections : {}, distance: float, raceDate : str) -> list:
    for entry in entries:
        penalty = entry['penalty']
        fleetSection = entry['fleetSection'].strip()
        rating = float(entry['rating'])
        finishStr = entry['finishTime'].strip()
        if finishStr in alphabetSoup:
            penalty = finishStr
            finishTime = toTime(raceDate, "23:23:59")
        else:
            finishTime = toTime(raceDate, finishStr)

        startTime  = toTime(raceDate, sections[fleetSection])
        elapsedTime = finishTime - startTime
        correctedTime = getCorrectedTime(elapsedTime, distance, rating)
        entry['fleet'] = fleetSection[0]
        entry['section'] = fleetSection[1:]
        entry['startTime'] = startTime
        entry['elapsedTime'] = elapsedTime
        entry['correctedTime'] = correctedTime
        entry['penalty'] = penalty

    return entries

'''
return the value to sort by
used to sort boats by corrected time
'''
def sortCorrectedTime(entry : dict) -> datetime:
    return entry['correctedTime']

def sortSectionPosition(entry : dict):
    return (entry['sectionPosition'], entry['boatname'].upper())


'''
calculate the position for a group of boats
ignore ties for now    
'''
def calculatePosition(entries : list, valueName : str) -> list:
    starters = len(entries)
    entries.sort(key=sortCorrectedTime)
    position = 1
    for entry in entries:
        entry[valueName] = position
        
        penalty = entry["penalty"]
        if penalty:
            penaltyPosition = alphabetSoup[penalty](starters, position)
            entry[valueName] = penaltyPosition
            
        position += 1
        
        # score penalties

    return entries
        
        
'''
Returns the entries by section sorted by finish position
'''
def rank(entries : list ) -> dict:
    fleet = {}
    fleetSection = {}
    #print("Entries", entries)

    
    # split the entries by fleet, and section
    for entry in entries:
        boatsFleet = entry["fleet"]
        boatsFleetSection = entry["fleet"] + entry["section"]
        
        if boatsFleet in fleet:
            aray = fleet[boatsFleet]
            aray.append(entry)
            fleet[boatsFleet] = aray
        else:
            fleet[boatsFleet] = [entry]
        
        if boatsFleetSection in fleetSection:
            aray = fleetSection[boatsFleetSection]
            aray.append(entry)
            fleetSection[boatsFleetSection] = aray
        else:
            fleetSection[boatsFleetSection] = [entry]

    for key in fleet.keys():
        calculatePosition(fleet[key], "fleetPosition")
        
    for key in fleetSection.keys():
        calculatePosition(fleetSection[key], "sectionPosition")
        
    return fleetSection

        
    
if __name__ == "__main__":
    raceFile = sys.argv[1]
    (config, series, sections, courses) = getInfo(get_full_path("morfrace.inf"))
    #print(config)
    roster = getRoster(get_full_path("morfrace.rst"))
    
    (raceConfig, starts, raceResults) = readRacFile(get_full_path(raceFile + ".rac"))
    #print("Race Config", raceConfig)
    date = raceConfig['Date']
    distance = float(raceConfig['Distance'])
    
    entries = calculateCorrectedTime(raceResults, starts, distance, date)
    raceResults = rank(entries)
    
    for section in raceResults.keys():
        sectionBoats = raceResults[section]    
        sectionBoats.sort(key=sortSectionPosition)
        for boat in sectionBoats:
            penalty = boat['penalty']
            if penalty:
                print(section, boat['fleetPosition'], boat['sectionPosition'], boat['sailno'], boat['boatname'], 
                  boat['rating'], penalty, penalty,
                  boat['boatType'], boat['owner'])
                
            else:
                print(section, boat['fleetPosition'], boat['sectionPosition'], boat['sailno'], boat['boatname'], 
                  boat['rating'], boat['finishTime'], timeDeltaToMinutesSeconds(boat['correctedTime']),
                  boat['boatType'], boat['owner'])
        print(' ')
        
    exportRaceToHtml(raceFile + ".html", raceConfig, starts, raceResults)
    exportRaceToText(raceFile + ".txt", raceConfig, starts, raceResults)




