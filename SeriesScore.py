import glob
import sys
from statistics import mean
from Utils import get_full_path


from ReadRaceFiles import readRacFile
from Export import exportSeriesToHtml

scoringMethod = 'lowpoint'

# score - 1600 - finish position ^ 2    
def snipe(position):
    return (41 - position) ** 2
    
def appendixA(position):
    return position

def appendixAPlus(position):
    return position if position > 1 else .75

'''
    Add a score to an array of finishes for a boat by race number
'''
def addScore(adict, section, sailno, boatNames, raceNumber, points, nRaces):
    if section not in adict:
        adict[section] = {}
        
    sectionBoats = adict[section]
    if sailno not in sectionBoats:
        sectionBoats[sailno] = [None] * nRaces
        
    boatScores = sectionBoats[sailno]
    boatScores[raceNumber] = points

'''
    Count the number of races completed by a boat
'''
def completedRaces(scores : dict) -> int:
    n = 0
    for score in scores:
        if score != None:
            n += 1
    return n
'''
Get the ge points for each race in the series

return a map of scores by section, finish position, and RC boats
'''
def getSeriesPoints(files):
    methods = {"MORF": snipe, "lowpoint": appendixA, "lowpointbonus":appendixAPlus, "appendixa":appendixA}
    scores = {}
    finishPositions = {}
    rc_boats = {}
    nRaces = len(files)
    boatNames = {}
    raceNumber = 0
    for fileName in files:
        (config, starts, results) = readRacFile(fileName)
        
        rc  = config['RC Boat'].strip()
        rc_sailno = ''
        if len(rc) > 0:
            rc_sailno = rc.split()[0]          
        rc_boats[rc_sailno] = raceNumber
        
        for boat in results:
            sailno = boat['sailno']
            boatNames[sailno] = boat['boatname']
            sectionPosition = int(boat['sectionPosition'])
            fleetPosition = int(boat['fleetPosition'])
            sectionPoints = methods[scoringMethod](sectionPosition)
            fleetPoints = methods[scoringMethod](fleetPosition)
            
            fleetSection = boat['fleetSection']
            fleetName =  "Fleet_" + fleetSection[0]
            
            addScore(finishPositions, fleetSection, sailno, boatNames, raceNumber, sectionPosition, nRaces)
            addScore(finishPositions, fleetName, sailno, boatNames, raceNumber, fleetPosition, nRaces)
            
            addScore(scores, fleetSection, sailno, boatNames, raceNumber, sectionPoints, nRaces)
            addScore(scores, fleetName, sailno, boatNames, raceNumber, fleetPoints, nRaces)
        raceNumber += 1
            
    return (scores, finishPositions, rc_boats, boatNames)    

'''
Sort a list of scores. Treat None as 0 (for MORF scoring) and large for lowpoint scoring
'''
def sortNone(value):
    if scoringMethod == 'MORF':
        return value if value != None else 0
    else:
        return value if value != None else 1000
    
'''
sort a list of boats by total points
'''
def sortTotalPoints(boat):
    return boat['totalPoints']

'''
    Get the compensation for a RC boat
    It is the average of the best required races 
'''
def calculateRCScore(scores, requiredRaces):
    scoreCopy = scores.copy()
    if scoringMethod == 'MORF':
        scoreCopy.sort(reverse=True, key=sortNone)
    else:
        scoreCopy.sort(reverse=False, key=sortNone)
        
    n = min(completedRaces(scoreCopy), requiredRaces-1)
    result = round(mean(scoreCopy[0:n]), 2)
    return result
        

'''
    Calculate the score for each boat in a series.
    Include compensation for RC boats
    return a lust sorted by series score
'''
def getSeriesScores(series : dict, requiredRaces : int, rc_boats : dict, boatNames) -> dict:
    results = {}
    for sectionID in series.keys():
        section = series[sectionID]
        for sailno in section.keys():
            boatName = boatNames[sailno]
            scores = section[sailno]
            
            if sailno in rc_boats:
                rc_score = calculateRCScore(scores, requiredRaces)
                scores[rc_boats[sailno]] = rc_score
                
            if scoringMethod == 'MORF':
                scores.sort(reverse=True, key=sortNone)
            else:
                scores.sort(reverse=False, key=sortNone)
                
            
            totalPoints = 0
            nRaces = 1
            for points in scores:
                if nRaces > requiredRaces:
                    break
                if points == None:
                    break
                totalPoints += points
                nRaces += 1
                
            if sectionID not in results:
                results[sectionID] = []
            
            listOfBoats = results[sectionID]
            listOfBoats.append({"sailno": sailno, "totalPoints": totalPoints, "racePoints": scores, 'boatName':boatName})
            
        # sort the results by total points
        listOfBoats = results[sectionID]
        if (scoringMethod == "MORF"):
            listOfBoats.sort(reverse=True, key=sortTotalPoints)
        else:
            listOfBoats.sort(reverse=False, key=sortTotalPoints)
            
    return results

'''
    Compute the series position accounting for tied scores
'''
def rankSeries(seriesScores):
    rankedScores = {}
    for section in seriesScores.keys():
        boats = seriesScores[section]
        rank = 1
        for boat in boats:
            boat['rank'] = rank
            rank += 1
            
    return seriesScores

# Undortunately, the finish positions aren't in the results map right now, so merge them
def mergeResults(results, finishPositions):
    for section in results.keys():
        resultsSection = results[section]
        positionsSection = finishPositions[section]
        for boat in resultsSection:
            sailno = boat['sailno']
            positions = positionsSection[sailno]
            boat['finishPositions'] = positions
            
    return results
            
        
    
if __name__ == "__main__":
    seriesName = sys.argv[1]
    races = glob.glob(get_full_path(seriesName + "*.rac"))
    print("Races", races)
    
    scoringMethod = 'MORF'
    if len(sys.argv) > 2:
        scoringMethod = sys.argv[2]
         
    (scores, finishPositions, rc_boats, boatNames)  = getSeriesPoints(races)
    #print(finishPositions)
    seriesScores = getSeriesScores(scores, 4, rc_boats, boatNames)
    results = rankSeries(seriesScores)
    
    # the following is a bit odd... but it seems to be the only way to get
    # the results sorted by section
    for section in dict(sorted(results.items())).keys():
        boats = results[section]
        for boat in boats:
            sailno = boat['sailno']
            #print(sailno, boat['rank'], boatNames[sailno], boat['totalPoints'], finishPositions[section][sailno])
            
    requiredRaces = len(races) // 2 + 1

    xresults = mergedResults = mergeResults(results, finishPositions)

    print("Exporting series score to html")
    exportSeriesToHtml(get_full_path(seriesName), len(races), results, rc_boats)
            
            
        

            
            
            
            
        
    
    