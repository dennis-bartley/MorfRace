'''
 Observer is a singleton class. Use getObserver() to access it

 As a aingleton, it doesnt have to be passed around to everybody
 just the ones that need it can use it
 
 
'''
from pickle import NONE



class Observer():
    
    instance = None 
    observers = [] 
    
    def __new__(cls):
        if cls.instance is None:
            cls.instance = super().__new__(cls)
        return cls.instance
    
    def __init__(self):
        pass   
        
    def register(self, fn):
        self.observers.append(fn)
        
    def remove(self, fn):
        try:
            self.observers.remove(fn)
        except:
            pass
        
        
    def notify(self, message):
        for fn in self.observers:
            fn(message)


        
    