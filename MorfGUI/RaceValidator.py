from tkinter import messagebox
from Validator import Validator
from MorfRace import alphabetSoup

class RaceValidator(Validator):
    def __init__(self, roster, controller):
        self.roster = roster
        self.controller = controller
        self.validators = {"Sailno": self.sailno, "Rating": self.rating, "Finish": self.finishValidator,
                           "Corrected": self.correctedValidator, "Section": self.section}
        
    # Return True if the value is valid, otherwise an error message
    #
    def validate(self, colName, value):
        # find the validator for this column. If there is none, assume it's ok
        rc = True 
        if colName in self.validators:
            rc = self.validators[colName](value)
            
        return rc
    
    def sailno(self, value):
        # Make sure the sail number is in the roster
        rc = False 
        if value in self.roster:
            rc = True 
            
        return rc
    
    # for now, we'll accept any integer
    def rating(self, value):
        try:
            ratingInt = int(value)
            rc = True 
        except:
            rc = "%s is invalid for Rating. It must be an integer" % value
            
        return rc
    
    
    def finishValidator(self, value):
        rc = False
        
        # if the value is DNS, DNF, DSQ...allow
        if value in alphabetSoup:
            return True
        try: 
            (hh,mm,ss) = value.split(":")
            hhInt = int(hh)
            mmInt = int(mm)
            ssInt = int(ss)
            if hhInt >= 0 and hhInt <= 24 and mmInt >=0 and mmInt <= 60 and \
               ssInt >= 0 and ssInt <= 60:
                rc = True
        except:
            pass
        
        if not rc:
            rc = "%s is invalid for finish Time. It should be HH:MM:SS" % value
            
        return rc
    
    def correctedValidator(self, value):
        rc = False
        
        # if the value is DNS, DNF, DSQ...allow
        if value in alphabetSoup:
            return True
        try: 
            (mm,ss) = value.split(":")
            mmInt = int(mm)
            ssInt = int(ss)

            if mmInt >=0 and mmInt <= 1440 and \
               ssInt >= 0 and ssInt <= 60:
                rc = True
        except:
            pass

        if not rc:
            rc = "%s is invalid for corrected Time. It should be MMM:SS" % value
            
        return rc
    
    
    # Make sure the section is in the list of Sections from the info file
    def section(self, value):
        sections = self.controller.get_sections()
        if  value in sections:
            rc = True 
        else:
            rc = "%s is not a valid Section. It should be in %s" % (value, sorted(sections))
            
        return rc

    