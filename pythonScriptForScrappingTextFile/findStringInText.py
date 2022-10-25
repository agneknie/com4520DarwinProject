import sys
import os
import re
import json
from datetime import datetime

originalDirectory = os.getcwd()

#---------------------------------------
# List of strings to look for in the files

stringsFile = open("strings.txt", "r")
stringsData = stringsFile.read()
stringsFile.close()
stringsToFind = stringsData.splitlines()

# Empty json object with array for each string to find
results = {}
for stringToFind in stringsToFind:
    results[stringToFind] = []

#---------------------------------------
# find names of all files to parse

filesToParse = []

# First argument is directory where text files to parse are
if len(sys.argv) > 1:
    os.chdir(sys.argv[1])

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
    for stringToFind in stringsToFind:
        matches = re.findall(r"[^.]*" + stringToFind + "[^.]*\.", textfileText, flags=re.IGNORECASE)
        results[stringToFind] = results[stringToFind] + matches

#---------------------------------------
# Change directories to where the command was called from, and write the
# results in a json format to a json file called data.json

os.chdir(originalDirectory)
resultsFile = open("data_" + datetime.today().strftime("%Y-%m-%d_%H-%M-%S") + ".json", "w")
resultsFile.write(json.dumps(results))
resultsFile.close()