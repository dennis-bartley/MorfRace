import re
from Utils import getColumn


pattern =  pattern = r'([A-Za-z0-9\s]*):\s*(.*)'
p = re.compile(pattern)



'''
Get a key/value pair from a column and add it to the dictionary
'''
def getValue(record, fromCol, toCol, aDict):
    field = getColumn(record, fromCol, toCol)
    if field != '':
        m = p.match(field)
        if m:
            aDict[m.group(1)] = m.group(2)
        else:
            #print("No Match", field)
            pass
            


def getConfigValues(record : str, config : dict): 
    getValue(record,  1, 43, config)
    getValue(record, 45, 64, config)
    getValue(record, 66, 80, config)

    
def getStartingTimes(record : str, starts : dict):
    getValue(record,  1, 16, starts)
    getValue(record, 18, 33, starts)
    getValue(record, 35, 50, starts)
    getValue(record, 52, 67, starts)
    getValue(record, 69, 80, starts)

    
def getRaceResults(record : str, results : []):
    raceResult = {}
    penalty = None
    raceResult['fleetSection'] = getColumn(record, 1, 3)
    raceResult['fleetPosition'] = getColumn(record, 4, 5)
    raceResult['sectionPosition'] = getColumn(record, 7, 8)
    raceResult['sailno'] = getColumn(record, 10, 14)
    raceResult['boatname'] = getColumn(record, 16, 30)
    raceResult['rating'] = getColumn(record, 32, 34)
    raceResult['finishTime'] = getColumn(record, 36, 43)
    raceResult['correctedTime'] = getColumn(record, 45, 50)
    raceResult['boatType'] = getColumn(record, 52, 64)
    raceResult['owner'] = getColumn(record, 66, 80)
    raceResult['penalty'] = penalty
    results.append(raceResult)
    
    

def readRacFile(fileName: str) -> (dict, dict):
    config = {}
    starts = {}
    results = []
    
    afile = open(fileName)
    
    config['title'] = afile.readline().strip()
    blank = afile.readline()
    
    while True:
        record = afile.readline().strip()
        if len(record) == 0:
            break
        getConfigValues(record, config)
        
    blank = afile.readline()
    while True:
        record = afile.readline().strip()
        if len(record) == 0:
            break
        getStartingTimes(record, starts)
        
    header = afile.readline()
    
    while True:
        record = afile.readline()
        if not record:
            break
        record = record.strip()
        if len(record) > 0:
            getRaceResults(record, results)
        
    return(config, starts, results)
        
if __name__ == "__main__":
    (config, starts, results) = readRacFile('perf03.rac')
    print(config)
    print(starts)
    for result in results:
        print(result)
    

    