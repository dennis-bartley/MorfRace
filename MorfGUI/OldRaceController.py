from Controller import Controller
import OldRaceView.RaceView
from ReadRaceFiles import readRacFile
from MorfRace import getCorrectedTime, rank
from Utils import toTime, timeDeltaToMinutesSeconds
from Export import exportRaceToText, exportRaceToHtml
from Roster import getRoster
from RaceInfoView import showInfoDialog

'''
    This is the controller for the race entry spreadsheet
    It contains useful methods to interact with the scoring program
    and file operations
'''
class RaceController(Controller):
    def __init__(self, master, roster, title, topview = False):
        self.root = master
        self.roster = roster
        self.info = showInfoDialog(master)
        if self.info is not None:
            self.startTimes = self.info["startTimes"]
        
            # Now show the Race entry grid
            self.view = OldRaceView(self, master, self.roster, self.info["title"], "1300x600", toplevel = True)
        
    def getRoster(self):
        self.roster = getRoster("Morfrace.rst")
        return self.roster
    
    def open_file(self, file_path):
        race_file = readRacFile(file_path)
        (self.info, self.startTimes, self.results) = race_file
        return race_file
    
    def save_file(self, file_path, results):
        file = file_path.split(".")
        if file[len(file)-1] == "html":
            exportRaceToHtml(file_path, self.info, self.startTimes, results)
        else:
            exportRaceToText(file_path, self.info, self.startTimes, results)
            
    def getStartTimes(self):
        return self.startTimes            

    def calculateCorrectedTime(self, sailno, finish, rate, section):
        distance = float(self.info['Distance'])
        rating = float(rate)
        date = self.info["Date"]
        print(self.startTimes)
        startTime = toTime(date, self.startTimes[section])
        elapsedTime = toTime(date, finish) - startTime
        correctedTime = getCorrectedTime(elapsedTime, distance, rating)
        result = timeDeltaToMinutesSeconds(correctedTime)
        return result
    
    # rank the boats by corrected time within section and fleet
    def Score(self, boats : list):
        # Make sure each boat has a finish time
        for boat in boats:
            if boat["finishTime"].strip() == "":
                raise BaseException("Sailno %s does not have a finish time" %
                                     boat["sailno"])
        results = rank(boats)
        return results