import csv
from ast import literal_eval

def appendInferencesToSentence(sentence, inferences):
  inferences = literal_eval(inferences)
  return ','.join(inferences) + "[SEP]" + sentence

def main():
  fileName = "globalGlobal/gold_global_global.csv"
  originalFile = open(fileName, 'r', encoding='utf-8')
  originalFileReader = csv.reader(originalFile)

  fileName2 = "originalDataSets/gold_dataset.csv"
  originalFile2 = open(fileName2, 'r', encoding='utf-8')
  originalFileReader2 = csv.reader(originalFile2)

  newFileName = "globalGlobal/gold_global_global_final.csv"
  newFile = open(newFileName, 'w', newline='', encoding='utf-8')
  newFileWriter = csv.writer(newFile)

  # create the new file
  next(originalFileReader2)
  headers = next(originalFileReader)
  headers = headers[0:9] + ['sim']
  newFileWriter.writerow(headers)


  for line in originalFileReader:
      line2 = next(originalFileReader2)
      
      line = [line[0],line[1],line[2],line[3],line[4],line[5],line[6],line[7],line2[6]]

      #write to files
      newFileWriter.writerow(line)

  newFile.close()
main()
