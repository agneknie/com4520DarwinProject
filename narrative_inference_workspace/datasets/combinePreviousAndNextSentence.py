import csv
from ast import literal_eval

def appendInferencesToSentence(sentence, inferences):
  inferences = literal_eval(inferences)
  return ','.join(inferences) + "[SEP]" + sentence

def main():
  fileName = "silver_ds_1.csv"
  originalFile = open(fileName, 'r', encoding='utf-8')
  originalFileReader = csv.reader(originalFile)

  newFileName = "silver_ds_1_combined_sentences.csv"
  newFile = open(newFileName, 'w', newline='', encoding='utf-8')
  newFileWriter = csv.writer(newFile)

  # create the new file

  headers = next(originalFileReader)
  headers = headers[0:6]
  newFileWriter.writerow(headers)

  for line in originalFileReader:
      pre_sentence = str(line[9])
      next_sentence = str(line[10])
      
      if(pre_sentence == "None"):
        pre_sentence = ""
      if(next_sentence == "None"):
        next_sentence = ""
      line = [line[0],line[1],line[2],line[3], pre_sentence +line[4]+ next_sentence, pre_sentence +line[5]+ next_sentence]

      #write to files
      newFileWriter.writerow(line)

  newFile.close()

main()
