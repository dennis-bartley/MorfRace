courses = {}
series = {}
sections = {}
config = {}

def courseHandler(record : str, cols : list):
    courses[cols[1]] = {"name":cols[1], "length":cols[2]}
    
def clubHandler(record, cols):
    config['club'] = cols[1]
    
def scoringHandler(record, cols):
    config['scoring'] = cols[1]
    
def seriesHandler(record, cols):
    series[cols[1]] = {"name":cols[1]}
    
def sectionHandler(record, cols):
    sections[cols[1]] = {"name":cols[1], "startTime":cols[2]}
    
def correctionHandler(record, cols):
    if cols[1] in ['TOD', 'TOT']:
        timeCorrection = cols[1]
    else:
        print("Invalid correction method, must be TOT or TOD. Using: ", timeCorrection)

'''
Get the info file
'''
def getInfo(fileName : str):
    handlers = {"course:":courseHandler, "club:": clubHandler, "series:" : seriesHandler, 
                "section:" : sectionHandler, "scoring:":scoringHandler, "correctionmethod": correctionHandler}
               
    inFile = open(fileName)
    info = inFile.readlines()
    for record in info:
        record = record.strip()
        if len(record) > 0:
            cols = record.split()
            configType = cols[0].lower()
            
            try:
                handler = handlers[configType]
                handler(record, cols)
            except Exception as e:
                # ignore anything else
                pass
    return (config, series, sections, courses)