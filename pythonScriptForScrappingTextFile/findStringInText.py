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
def parseTextFiles(filesToParse, stringsToFind, finalResults, lock):
    print(datetime.today())
    for textfileName in filesToParse:
        textfile = open(textfileName, "r")
        textfileText = textfile.read()
        textfile.close()
        for i, stringToFind in enumerate(stringsToFind):
            matches = re.findall(r"[^.]*" + stringToFind + "[^.]*\.", textfileText, flags=re.IGNORECASE)
            if matches:
                with lock:
                    finalResults[i] = finalResults[i] + matches

#---------------------------------------
# Change directories to where the command was called from, and write the
# results in a json format to a json file called data.json
if __name__ == '__main__':
    stringsToFind = getJSONOfStringsToLookFor()
    namesFilesToParsePerCore = getNamesOfFilesToParse()
    
    # Shared dictionary for processes to use
    manager = Manager()
    lock = manager.Lock()
    sharedList = manager.list()
    for i in stringsToFind:
        sharedList.append([])

    # List of all processes
    jobs = []
    
    for i in range(NUMBEROFCORES):
        jobs.append(Process(target=parseTextFiles,
        args=[namesFilesToParsePerCore[i], stringsToFind, sharedList, lock]))
        jobs[i].start()

    for i in jobs:
        i.join()

    print(sharedList)
    
    os.chdir(ORIGINALDIRECTORY)
    resultsFile = open("data_" + datetime.today().strftime("%Y-%m-%d_%H-%M-%S") + ".json", "w")
    resultsFile.write(json.dumps(list(sharedList)))
    resultsFile.close()