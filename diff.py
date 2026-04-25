import sys

file1 = sys.argv[1]
file2 = sys.argv[2]

ifile1 = open(file1, "r")
ifile2 = open(file2, "r")

file1 = ifile1.readlines()
file2 = ifile2.readlines()

i = 0
for line1 in file1:
    line2 = file2[i]
    
    if line1.rstrip() != line2.rstrip():
        print(i, len(line1), line1)
        print(i, len(line1), line2)
        print()
    
    i += 1
        
        