
from datetime import timedelta
from Utils import get_full_path

FIRST_COLUMN = 1
SECOND_COLUMN = 45
THIRD_COLUMN = 66

def timeDeltaToMinutesSeconds(delta : timedelta) -> str:
    seconds = delta.total_seconds()
    result = "%d:%02d" % (seconds//60, seconds % 60)
    return result

def exportRaceToHtml(outputFileName : str, config : dict, starts : dict, results : []):
    inFile = open(get_full_path('raceTemplate.html'), "r")
    template = inFile.read()
    inFile.close()
    
    html = template.replace("%title", config["title"])
    
    html = html.replace("%Race", config['Race'])
    html = html.replace("%Series", config['Series'])
    html = html.replace("%Date", config['Date'])
    html = html.replace('%Course', config["Course"])
    html = html.replace("%Series", config['Series'])
    html = html.replace("%Distance", config['Distance'])
    html = html.replace("%RCBoat", config['RC Boat'])
    html = html.replace("%Wind", config['Wind'])
    html = html.replace("%Seas", config['Seas'])
    
    startTimes = ""
    for section in starts:
        startTimes += "<td>" + section + ": " + starts[section] + "&nbsp;&nbsp; </td>"
    html = html.replace("%Starts", startTimes)
    
    boats = ""
    for section in results:
        entries = results[section]
        boats += "<tr><td>&nbsp</td></tr>"
        for boat in entries:
            boats += "<tr>"
            boats += "<td>" + section + "</td>"
            boats += "<td>" + str(boat['fleetPosition']) + "</td>"
            boats += "<td>" + str(boat["sectionPosition"]) + "</td>"
            boats += "<td align='right'>" + boat["sailno"] + "</td>"
            boats += "<td>&nbsp;" + boat["boatname"] + "</td>"
            boats += "<td align=right>" + boat['rating'] + "</td>"
            boats += "<td align=right>" + boat['finishTime'] + "&nbsp;</td>"
            boats += "<td align=right>&nbsp;" + timeDeltaToMinutesSeconds(boat['correctedTime']) + "</td>"
            boats += "<td>&nbsp;" + boat['boatType'] + "</td>"
            boats += "<td>" + boat['owner'] + "</td>"
            boats += "</tr>\n"
            
    html = html.replace("%Boats", boats)
    
    outfile = open(outputFileName, "w")
    outfile.write(html)
    outfile.close()
    
def getScoreAsString(score : int, boat, raceNumber, rcBoats) -> str:
    result = ""
    if score:
        result = str(score)
        
    #If it's a rc boat for this race, mark it'
    sailno = boat['sailno']
    if sailno in rcBoats and rcBoats[sailno] == raceNumber:
        result = "*" + result
        
    return result

def doSection(section, boat, nRaces, rcBoats):
    html = "<tr><td>%s</td><td>%d</td><td>%s</td><td>%s</td>" % (section, boat['rank'],  boat['boatName'], 
                                                                 boat['totalPoints'])
    scores = boat['finishPositions']
    for i in range(nRaces):
        html += "<td align=left>%s</td>" % getScoreAsString(scores[i], boat, i, rcBoats) 
    html += "</tr>\n"   
    return html
    
def exportSeriesToHtml(outputFileName : str, nRaces, series : {}, rcBoats):
    inFile = open(get_full_path('seriesTemplate.html'), "r")
    template = inFile.read()
    inFile.close()

    
    html = "<tr><<th align=left>Sc</th><th align=left>Pl</th><th align=left>Boat Name</th><th align=left>Points</th>"
    for i in range(nRaces):
        html += "<th align=left>%02d</th>" % (i + 1)
    html += "</tr>\n"
        
    sectionHtml = ""
    fleetHtml = ""
    for section in series.keys():        
        for boat in series[section]:
            if "Fleet" in section:
                fleetHtml += doSection(section, boat, nRaces, rcBoats)
            else:
                sectionHtml += doSection(section, boat, nRaces, rcBoats)
     
        if "Fleet" in section:
            fleetHtml += "<tr><td>&nbsp</td</tr>\n"
        else:
            sectionHtml += "<tr><td>&nbsp</td</tr>\n"
    
    template = template.replace("%title", "Series Scores " + outputFileName)
    template = template.replace("%heading", html)
    template = template.replace("%sectionScores", sectionHtml)
    template = template.replace("%fleetScores", fleetHtml)
    
    outFile = open(outputFileName + ".html", "w")
    outFile.write(template)
    outFile.close()
    
# Strings are imutable in Python, this will replace columns in a string and return a new string
def replaceCol(line, column, string):
    index = column - 1
    result = ""
    if index != 0:
        result = line[0:index]
    result += string + line[index + len(string):]
    return result

def write_line(outfile, line):
    outfile.write(line.rstrip() + "\n")
    
def write_line_nostrip(outfile, line):
    outfile.write(line + "\n")
    
# the .rac text file consists of 80 column records    
def exportRaceToText(outputFileName : str, config : dict, starts : dict, results : []): 
    blank = " " * 80
    outfile = open(outputFileName , "w")
    
    line = blank
    title = config["title"]
    write_line(outfile, config["title"])
    write_line(outfile, "")
    
    line = blank
    line = replaceCol(line, FIRST_COLUMN, "Race:    " + config["Race"])
    line = replaceCol(line, SECOND_COLUMN, "Series: " + config["Series"])
    line = replaceCol(line, THIRD_COLUMN, "Date: "  + config["Date"]);
    write_line(outfile, line);
    
    line = blank
    line = replaceCol(line, FIRST_COLUMN, "Course:  " + config['Course'])
    line = replaceCol(line, SECOND_COLUMN, "Distance: " + config["Distance"])
    write_line(outfile, line)
    
    line = blank
    line= replaceCol(line, FIRST_COLUMN, "RC Boat: " + config["RC Boat"])
    line = replaceCol(line, SECOND_COLUMN, "Wind: " + config["Wind"])
    line = replaceCol(line, THIRD_COLUMN, "Seas: " + config["Seas"])
    write_line(outfile, line)
    
    write_line(outfile, "")
    line = blank
    line = replaceCol(line, FIRST_COLUMN, "Sections & Start Times: ")
    write_line(outfile, line)
    
    line = blank
    i = 0
    for section in starts.keys():
        line = replaceCol(line, i*17 + 1, section + ": " + starts[section])   
        i += 1 
        if i == 5:
            write_line(outfile, line)
            line = blank
            i = 0 
    if (i != 0):
        write_line(outfile, line)
            
    #write_line(outfile, line)
        
    write_line(outfile, "")
    line = blank
    line = replaceCol(line, FIRST_COLUMN, "Sx  F  S Sail# Boat Name       Rtg   Finish   Corr Boat Type     Owner")
    write_line(outfile, line)
    write_line(outfile, "")
    
    for section in results.keys():
        for boat in results[section]:
            line = blank
            line = replaceCol(line, 1, section)
            line = replaceCol(line, 4, "%2d" % boat["fleetPosition"])
            line = replaceCol(line, 7, "%2d" % boat["sectionPosition"])
            line = replaceCol(line, 10, "%5d" % int(boat['sailno']))
            line = replaceCol(line, 16, boat["boatname"])
            line = replaceCol(line, 32, "%3d" % int(boat["rating"]))

            penalty = boat["penalty"]
            if penalty != None:
                line = replaceCol(line, 41, penalty)
                line = replaceCol(line, 48, penalty)
            else:
                line = replaceCol(line, 36, boat["finishTime"])
                line = replaceCol(line, 45, "{:>6}".format(timeDeltaToMinutesSeconds(boat['correctedTime'])))
            line = replaceCol(line, 52, boat["boatType"])
            line = replaceCol(line, 66, boat["owner"])
            write_line_nostrip(outfile, line)
            
        write_line(outfile, "")
        
    outfile.close()
      

    
        
        
    
    
    
    
    
         

         
    
    
        
    
    
    