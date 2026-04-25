# Validate an entry field

class RosterValidator():
    def __init__(self, roster, controller, cols):
        self.controller = controller
        self.column_names = cols
        self.validators = {"Rating": self.rating, "Section": self.section, "Sailno": self.sailno}
        
    def validate(self, column, value):
        if column in self.validators:
            validator = self.validators[column]
            return validator(value)
        
        return True
    
    # ratings must be integer. We'll not allow decimal... for now
    def rating(self, value):
        try:
            int(value)
            return True
        except:
            return "%s is an invalid rating" % value
    
        
    def section(self, value):
        sections = self.controller.get_sections()
        if  value in sections:
            rc = True 
        else:
            rc = "%s is not a valid Section. It should be in %s" % (value, sorted(sections))
            
        return rc
    
    def sailno(self, value):
        rc = True 
        try:
            num = int(value)
        except Exception as e:
            rc = "%s is not a valid sail number. It should be a number" % (value)
            
        return rc
    
