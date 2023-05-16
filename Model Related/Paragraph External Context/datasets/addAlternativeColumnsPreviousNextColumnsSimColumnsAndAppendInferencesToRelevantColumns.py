import csv
from ast import literal_eval

def appendInferencesToSentence(sentence, inferences):
  inferences = literal_eval(inferences)
  return ','.join(inferences) + "[SEP]" + sentence

def main():
  fileName = "localLocal/silver_ds_5_local_local.csv"
  originalFile = open(fileName, 'r', encoding='utf-8')
  originalFileReader = csv.reader(originalFile)

  fileName2 = "datasetsWithInferencesSeparately/silver_ds_10_with_inferences.csv"
  originalFile2 = open(fileName2, 'r', encoding='utf-8')
  originalFileReader2 = csv.reader(originalFile2)

  newFileName = "localLocal/silver_ds_5_local_local_final.csv"
  newFile = open(newFileName, 'w', newline='', encoding='utf-8')
  newFileWriter = csv.writer(newFile)

  # create the new file
  next(originalFileReader2)
  headers = next(originalFileReader)
  headers = headers[0:6] + ['sim','alternative_1','alternative_2']
  newFileWriter.writerow(headers)


  for line in originalFileReader:
      line2 = next(originalFileReader2)
      inferences = line2[12]

      sentence_previous = line2[9]
      if (sentence_previous == "None"):
         sentence_previous = ""
      sentence_next = line2[10]
      if (sentence_next == "None"):
         sentence_next = ""

      alternative_1 = line2[7]
      if (alternative_1 != "empty"):
         alternative_1 = appendInferencesToSentence(alternative_1, inferences)
      alternative_2 = line2[8]
      if (alternative_2 != "empty"):
         alternative_2 = appendInferencesToSentence(alternative_2, inferences)
      
      line = [line[0],line[1],line[2],line[3],
              # appendInferencesToSentence(line2[4], inferences),
              # appendInferencesToSentence(line2[5], inferences),
              line[4], line[5],
              line2[6],
              # line2[6],line2[9],line2[10],
              alternative_1,
              alternative_2]

      #write to files
      newFileWriter.writerow(line)

  newFile.close()
main()
