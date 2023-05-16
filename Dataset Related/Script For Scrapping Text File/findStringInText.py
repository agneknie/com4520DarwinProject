import sys
import os
import re

originalDirectory = os.getcwd()

#---------------------------------------
# List of strings to look for in the files

stringsFile = open("strings.txt", "r")
stringsData = stringsFile.read()
stringsToFind = stringsData.splitlines()

# Empty 2D array with array for each string to find
results = [[]] * len(stringsToFind)

#---------------------------------------
# Construct list of files to parse. If arguments were passed to the script,
# each argument is added as a separate name of file to parse

os.chdir("..")
filesToParse = []

if len(sys.argv) > 1:
    for file in sys.argv[1:]:
        filesToParse.append(file)
else:
    listCurrentDirectory = os.listdir()
    for file in listCurrentDirectory:
        if file[-4:] == ".txt":
            filesToParse.append(file)
            
#---------------------------------------
# Open each file and apply a regular expression for every stringToFind to
# the text within

for textfileName in filesToParse:
    textfile = open(textfileName, "r")
    textfileText = textfile.read()
    textfile.close()
    for stringIndex, stringToFind in enumerate(stringsToFind):
        matches = re.findall(r"[^.]*" + stringToFind + "[^.]*\.", textfileText, flags=re.IGNORECASE)
        results[stringIndex] = results[stringIndex] + matches

print(results)

#---------------------------------------

os.chdir(originalDirectory)

