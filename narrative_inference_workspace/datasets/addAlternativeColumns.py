import csv
from ast import literal_eval

def appendInferencesToSentence(sentence, inferences):
  inferences = literal_eval(inferences)
  return ','.join(inferences) + "[SEP]" + sentence

def main():
  fileName = "globalGlobal/gold_global_global.csv"
  originalFile = open(fileName, 'r', encoding='utf-8')
  originalFileReader = csv.reader(originalFile)

  fileName2 = "globalGlobal/gold_global_context.csv"
  originalFile2 = open(fileName2, 'r', encoding='utf-8')
  originalFileReader2 = csv.reader(originalFile2)

  newFileName = "globalGlobal/gold_global_global_final.csv"
  newFile = open(newFileName, 'w', newline='', encoding='utf-8')
  newFileWriter = csv.writer(newFile)

  # create the new file
  next(originalFileReader2)
  headers = next(originalFileReader)
  headers = headers[0:9] + ['alternative_1','alternative_2']
  newFileWriter.writerow(headers)


  for line in originalFileReader:
      line2 = next(originalFileReader2)
      inferences = line2[11]

      alternative_1 = line2[7]
      if (alternative_1 != "empty"):
         alternative_1 = appendInferencesToSentence(alternative_1, inferences)
      alternative_2 = line2[8]
      if (alternative_2 != "empty"):
         alternative_2 = appendInferencesToSentence(alternative_2, inferences)
      
      line = [line[0],line[1],line[2],line[3],line[4],line[5],line[6],line[7],line[8],
              alternative_1,
              alternative_2]

      #write to files
      newFileWriter.writerow(line)

  newFile.close()
main()
