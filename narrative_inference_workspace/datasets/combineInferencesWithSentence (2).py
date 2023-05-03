import csv
from ast import literal_eval

def appendInferencesToSentence(sentence, inferences):
  inferences = literal_eval(inferences)
  return ','.join(inferences) + "[SEP]" + sentence

def main():
  fileName = "datasetsWithInferencesSeparately/silver_ds_10_with_inferences.csv"
  originalFile = open(fileName, 'r', encoding='utf-8')
  originalFileReader = csv.reader(originalFile)

  newFileName = "globalLocal/silver_ds_10_global_local.csv"
  newFile = open(newFileName, 'w', newline='', encoding='utf-8')
  newFileWriter = csv.writer(newFile)

  # create the new file
  headers = next(originalFileReader)
  headers = headers[0:6] + headers[9:11]

  newFileWriter.writerow(headers)

  for line in originalFileReader:
      pre_sentence = str(line[9])
      next_sentence = str(line[10])
      inferences = line[12]
      
      if(pre_sentence == "None"):
        pre_sentence = ""
      if(next_sentence == "None"):
        next_sentence = ""
      line = [line[0],line[1],line[2],line[3], 
              appendInferencesToSentence(line[4], inferences), 
              appendInferencesToSentence(line[5], inferences), 
              pre_sentence, next_sentence]

      #write to files
      newFileWriter.writerow(line)

  newFile.close()

main()
