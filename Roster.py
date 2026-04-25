'''
Created on Jan 16, 2024

@author: Dennis
'''
from Utils import getColumn

def getRoster(fileName : str) -> dict:
    roster = {}
    infile = open(fileName)
    entries = infile.readlines()
    for entry in entries[4:]:
        if len(entry) > 0:
            sailno = getColumn(entry,1,5)
            boatname = getColumn(entry,7,21)
            boattype = getColumn(entry,23,36)
            section = getColumn(entry,38,39)
            rating = int(getColumn(entry,43,45))
            owner = getColumn(entry,48,62)
            harbor = getColumn(entry,64,70)
            roster[sailno] = {"sailno":sailno, "boatname":boatname, "boattype":boattype, 
                              "section":section, "rating":rating, "owner":owner,
                              "harbor":harbor}
    infile.close()
    return roster

def fill(str, start, value):
    col = start - 1
    for index in range(len(value)):
        str[col] = value[index]
        col += 1
    return str

def saveRoster(fileName : str, roster : dict, title):
    outfile = open(fileName, "w")
    outfile.write(title)
    outfile.write("\n")
    outfile.write("Sail# Boat Name       Boat Type      Sx   Rtg  Skipper         Comments\n")
    outfile.write("\n")
    keys = roster.keys()
    for sailno in keys:
        entry = roster[sailno]
        # so, this is a bit odd...
        # Python strings aren't mutable, so turn the straing into an array of characters.
        # insert the value character by character into the arrey
        # and when all done, turn the array back into a string.


        line = list(' ' * 80)
        fill(line, 1, "{:>5}".format(int(entry["sailno"])))
        fill(line, 7, entry['boatname'])
        fill(line, 23,entry['boattype'])
        fill(line, 38, entry['section'])
        fill(line, 43, "{:>3}".format(int(entry['rating'])))
        fill(line, 48, entry['owner'])
        fill(line, 64, entry['harbor'])

        astr = "".join(line).rstrip() + "\n"
        outfile.write(astr)
    outfile.close()   
    