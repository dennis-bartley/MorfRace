

from RosterView import RosterView
from Roster import getRoster, saveRoster
from RaceController import RaceController
from Utils import get_full_path
from Info import getInfo
from Observer import Observer


class RosterController():
    def __init__(self, rosterFile):
        self.rosterFile = rosterFile
        (self.config, self.series, self.sections, self.courses) = getInfo(get_full_path("MorfRace.inf"))  
        self.roster = None   
        if (rosterFile):
            self.roster = getRoster(rosterFile)
            
        self.view = RosterView(self, self.roster, rosterFile)   


    def new_race(self):
        raceController = RaceController(self.rosterFile, None)
        
    def open_race(self, race_file_name):
        race_controller = RaceController(self.rosterFile, race_file_name)
        
        
    def new_file(self):
        controller = RosterController(None)
        pass
    
    def save_file(self, file_path, roster):
        title = "Midwest Open Racing Fleet 2023                                         15-Sep-23\n"
        saveRoster(file_path, roster, title)
        Observer().notify("Roster saved")
        
    def get_sections(self):
        return self.sections.keys()