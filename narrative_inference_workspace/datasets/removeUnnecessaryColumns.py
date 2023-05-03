import csv
from ast import literal_eval

def appendInferencesToSentence(sentence, inferences):
  inferences = literal_eval(inferences)
  return ','.join(inferences) + "[SEP]" + sentence

def main():
  fileName = "globalGlobal/gold_global_context.csv"
  originalFile = open(fileName, 'r', encoding='utf-8')
  originalFileReader = csv.reader(originalFile)

  newFileName = "globalGlobal/gold_global_global.csv"
  newFile = open(newFileName, 'w', newline='', encoding='utf-8')
  newFileWriter = csv.writer(newFile)

  # create the new file
  headers = next(originalFileReader)
  headers = headers[0:6] + headers[9:11]
  newFileWriter.writerow(headers)

  for line in originalFileReader:
      sentence_previous = line[9]
      if (sentence_previous == "None"):
         sentence_previous = ""
      sentence_next = line[10]
      if (sentence_next == "None"):
         sentence_next = ""
      
      inferences = line[11]
      
      line = [line[0],line[1],line[2],line[3],
              appendInferencesToSentence(line[4], inferences),
              appendInferencesToSentence(line[5],inferences),
              sentence_next, sentence_previous]

      #write to files
      newFileWriter.writerow(line)

  newFile.close()
main()
