#from ClaudeView  import create_grid_app
from RosterView import RosterView
from RaceView import RaceView
from Roster import getRoster
from Utils import get_full_path
from Info import getInfo
from Utils import toTime, timeDeltaToMinutesSeconds
from MorfRace import getCorrectedTime, rank
from Export import exportRaceToText, exportRaceToHtml
from ReadRaceFiles import readRacFile



class RaceController():
    def __init__(self, rosterFile, race_file_name):
        self.rosterFile = rosterFile
        roster = getRoster(rosterFile)
        view = RaceView(self, roster, race_file_name, "New Race")

    def new_race(self):
        roster = getRoster(get_full_path(self.rosterFile))
        view = RaceView(self, roster, None, "Race")
        
    def get_sections(self):
        return self.sections.keys()
    
    # Remeber the information for the race... start times, distance, etc
    def set_info(self, info):
        self.info = info
        self.startTimes = info["startTimes"]
    
    def calculateCorrectedTime(self, sailno, finish, rate, section):
        distance = float(self.info['Distance'])
        rating = float(rate)
        date = self.info["Date"]
        start_times = self.startTimes
        startTime = toTime(date, start_times[section])
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
        