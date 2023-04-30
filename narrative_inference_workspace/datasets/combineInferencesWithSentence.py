import csv
from ast import literal_eval

def appendInferencesToSentence(sentence, inferences):
  inferences = literal_eval(inferences)
  return ','.join(inferences) + "[SEP]" + sentence

def main():
  fileName = "original_eval_with_inferences.csv"
  originalFile = open(fileName, 'r', encoding='utf-8')
  originalFileReader = csv.reader(originalFile)

  newFileLocalName = "original_eval_context.csv"
  newFileLocal = open(newFileLocalName, 'w', newline='', encoding='utf-8')
  newFileLocalWriter = csv.writer(newFileLocal)

  # newFileGlobalName = "original_dev_context.csv"
  # newFileGlobal = open(newFileGlobalName, 'w', newline='', encoding='utf-8')
  # newFileGlobalWriter = csv.writer(newFileGlobal)

  # create the new file

  headers = next(originalFileReader)
  headers = headers[0:6]
  newFileLocalWriter.writerow(headers)
  # newFileGlobalWriter.writerow(headers)

  for line in originalFileReader:
      inferences = line[6]
      
      # local
      lineLocal = [line[0],line[1],line[2],line[3],appendInferencesToSentence(line[4], inferences),
              appendInferencesToSentence(line[5], inferences)]
      
      # #global
      # sentence_previous = line[9]
      # if sentence_previous == "None":
      #    sentence_previous = ""
      # sentence_next = line[10]
      # if sentence_next == "None":
      #    sentence_next = ""
      # lineGlobal = [line[0],line[1],line[2],line[3],appendInferencesToSentence(sentence_previous+line[4]+sentence_next, inferences),
      #         appendInferencesToSentence(sentence_previous+line[5]+sentence_next, inferences), line[6],
      #         appendInferencesToSentence(sentence_previous+line[7]+sentence_next, inferences),
      #         appendInferencesToSentence(sentence_previous+line[8]+sentence_next, inferences)]

      #write to files
      newFileLocalWriter.writerow(lineLocal)
      # newFileGlobalWriter.writerow(lineGlobal)

  newFileLocal.close()
  # newFileGlobal.close()

main()
