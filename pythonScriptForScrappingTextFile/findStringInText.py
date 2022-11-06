import sys
import os
import re
import json
from datetime import datetime
from multiprocessing import Process, Manager

ORIGINALDIRECTORY = os.getcwd()
NUMBEROFCORES = os.cpu_count()

#---------------------------------------
# List of strings to look for in the files
def getJSONOfStringsToLookFor():
    print(os.getcwd())
    stringsFile = open("strings.txt", "r")
    stringsData = stringsFile.read()
    stringsFile.close()
    stringsToFind = stringsData.splitlines()

    return stringsToFind

#---------------------------------------
# find names of all files to parse
def getNamesOfFilesToParse():
    filesToParse = [[] for i in range(NUMBEROFCORES)]
    counter = 0

    # First argument is directory where text files to parse are
    if len(sys.argv) > 1:
        os.chdir(sys.argv[1])

    listCurrentDirectory = os.listdir()
    for file in listCurrentDirectory:
        if file[-4:] == ".txt":
            filesToParse[counter].append(file)
            if counter < (NUMBEROFCORES - 1):
                counter +=1
            else:
                counter = 0
    return filesToParse
            
#---------------------------------------
# Open each file and apply a regular expression for every stringToFind to
# the text within
def parseTextFiles(procNum, filesToParse, stringsToFind, results, finalResults):
    print(datetime.today())
    for textfileName in filesToParse:
        textfile = open(textfileName, "r")
        textfileText = textfile.read()
        textfile.close()
        for stringToFind in stringsToFind:
            matches = re.findall(r"[^.]*" + stringToFind + "[^.]*\.", textfileText, flags=re.IGNORECASE)
            results[stringToFind] = results[stringToFind] + matches
    finalResults[procNum] = results

#---------------------------------------
# Change directories to where the command was called from, and write the
# results in a json format to a json file called data.json
if __name__ == '__main__':
    stringsToFind = getJSONOfStringsToLookFor()
    namesFilesToParsePerCore = getNamesOfFilesToParse()
    
    # Empty json object with array for each string to find
    results = {}
    for stringToFind in stringsToFind:
        results[stringToFind] = []
    
    manager = Manager()
    returnDict = manager.dict()
    jobs = []
    
    for i in range(NUMBEROFCORES):
        jobs.append(Process(target=parseTextFiles,
        args=[i, namesFilesToParsePerCore[i], stringsToFind, results, returnDict]))
        jobs[i].start()

    for i in jobs:
        i.join()
    print(returnDict)
    raise SystemExit(0)
    
    os.chdir(ORIGINALDIRECTORY)
    resultsFile = open("data_" + datetime.today().strftime("%Y-%m-%d_%H-%M-%S") + ".json", "w")
    resultsFile.write(json.dumps(results))
    resultsFile.close()