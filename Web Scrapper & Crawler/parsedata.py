from bs4 import BeautifulSoup
import requests
import json
import csv
import re
import pandas as pd
import sys
import time

#Provide .csv file (for now) with text and the scipt will separate it into
#sentences. Those sentences will be checked for idioms present in the idiom list.
#Produce output for all idioms and sentences that have them.

#Idiom list used when detection idioms in sentences
idiom_list = ['beat around the bush', 'get your act together', 'hit the sack', 'your guess is as good as mine', 'good things come to those who wait', 'back against the wall', 'up in arms', 'scrape the barrel', 'sell like hot cakes', 'run around in circles', 'on cloud nine', 'left out in the cold', 'blow hot and cold', 'cut corners', 'boil the ocean', 'keep an ear to the ground', 'eat like a horse', 'a snowball effect', 'in for a penny, in for a pound', 'chip off the old block', 'don’t cry over spilt milk', 'every cloud has a silver lining', 'fair and square', 'a black sheep', 'bear a grudge', 'draw the line',  'easier said than done', 'break a leg', 'fish out of water', 'give it a whirl', 'in the fast lane', ' go the extra mile', 'step up your game', 'lose your marbles', 'crying wolf', 'palm off', 'has bigger fish to fry', 'look before you leap', 'on thin ice', 'like a cakewalk', 'the whole nine yards', 'kick the bucket', 'a piece of cake', 'bite off more than you can chew', 'ignorance is bliss', 'you can say that again', 'bite the bullet', 'go back to the drawing board', 'call it a day', 'be in a tight corner', 'at the 11th hour', 'swan song', 'wild goose chase', 'bury the hatchet', 'hit the books', 'stab someone in the back', 'ring a bell', 'blow off steam', 'cut no ice', 'light at the end of tunnel', 'cry for the moon', 'read between the lines', 'flesh and blood', 'a slap on the wrist', 'old as the hills', 'black and blue', 'black out', 'shoot from the hip', 'an arm and a leg', 'not your cup of tea', 'in the same boat']

###################################
### WORKS WITH CSV ONLY FOR NOW ###
###################################

#Files read/created during runtime
txt_scrap_file_name = 'data/dataScrap_1.txt'            #File being read
csv_scrap_file_name = 'data/dataScrap_1.csv'            #File being read
csv_sentence_file_name = 'senteces/sentenceData_1.csv'  #File being written/created
csv_output_file_name = 'output/output_1.csv'            #File being written/created

#Regex for sentence detection  
alphabets= "([A-Za-z])"
prefixes = "(Mr|St|Mrs|Ms|Dr)[.]"
suffixes = "(Inc|Ltd|Jr|Sr|Co)"
starters = "(Mr|Mrs|Ms|Dr|He\s|She\s|It\s|They\s|Their\s|Our\s|We\s|But\s|However\s|That\s|This\s|Wherever)"
acronyms = "([A-Z][.][A-Z][.](?:[A-Z][.])?)"
websites = "[.](com|net|org|io|gov)"
digits = "([0-9])"

#Seperate text into sentencs. Covers most edge cases
def split_into_sentences(text):
    text = " " + text + "  "
    text = text.replace("\n"," ")
    text = re.sub(prefixes,"\\1<prd>",text)
    text = re.sub(websites,"<prd>\\1",text)
    text = re.sub(digits + "[.]" + digits,"\\1<prd>\\2",text)
    if "..." in text: text = text.replace("...","<prd><prd><prd>")
    if "Ph.D" in text: text = text.replace("Ph.D.","Ph<prd>D<prd>")
    text = re.sub("\s" + alphabets + "[.] "," \\1<prd> ",text)
    text = re.sub(acronyms+" "+starters,"\\1<stop> \\2",text)
    text = re.sub(alphabets + "[.]" + alphabets + "[.]" + alphabets + "[.]","\\1<prd>\\2<prd>\\3<prd>",text)
    text = re.sub(alphabets + "[.]" + alphabets + "[.]","\\1<prd>\\2<prd>",text)
    text = re.sub(" "+suffixes+"[.] "+starters," \\1<stop> \\2",text)
    text = re.sub(" "+suffixes+"[.]"," \\1<prd>",text)
    text = re.sub(" " + alphabets + "[.]"," \\1<prd>",text)
    if "”" in text: text = text.replace(".”","”.")
    if "\"" in text: text = text.replace(".\"","\".")
    if "!" in text: text = text.replace("!\"","\"!")
    if "?" in text: text = text.replace("?\"","\"?")
    text = text.replace(".",".<stop>")
    text = text.replace("?","?<stop>")
    text = text.replace("!","!<stop>")
    text = text.replace("<prd>",".")
    sentences = text.split("<stop>")
    sentences = sentences[:-1]
    sentences = [s.strip() for s in sentences]
    return sentences

#Deletes last line written in terminal
def delete_last_line():
    "Use this function to delete the last line in the STDOUT"

    #cursor up one line
    sys.stdout.write('\x1b[1A')

    #delete last line
    sys.stdout.write('\x1b[2K')
    
#Detect senteces in scrapped text
with open(csv_scrap_file_name, 'r', encoding='UTF8', newline='') as f:
  csv_reader = csv.reader(f, delimiter=',')
  sentenceList = []
  counter = 0
  
  print("---- Detecting Sentences ----")
  print("---- Detecting ----")
  
  with open(csv_sentence_file_name, 'w', encoding='UTF8', newline='') as f:
    header = ['Sentence']
    writer = csv.writer(f)
    writer.writerow(header)
    
    #Collect detected sentences
    for row in csv_reader:
      if row[0] != "Text":
        sentenceList = sentenceList + split_into_sentences(str(row[0]))
        counter +=1
      
      if counter % 1000 == 0:
        for csv_sentence in sentenceList: 
          writer.writerow([csv_sentence])
          
        delete_last_line()
        print("---- Senteced detected: " + str(counter) + " ----")
        sentenceList = []
  
  # #Remove duplicates        
  df = pd.read_csv(csv_sentence_file_name)
  df.drop_duplicates(inplace=True)    
  df.to_csv(csv_sentence_file_name, index=False)    
      

with open(csv_output_file_name, 'w', encoding='UTF8', newline='') as f:
  writer = csv.writer(f, quoting=csv.QUOTE_ALL)
  print("---- Scanning Sentences ----")
  idiom_count = 0
  
  #Start checking senteces for idioms present in the idiom list
  for idiom in idiom_list:
    if idiom_count > 0:
      delete_last_line()
      
    print("---- Checking idiom: " + str(idiom_count + 1) + "/" + str(len(idiom_list)) + " ----")
    idiom_count += 1
    idiom_sentence_list = ['------------------------------------',
                           idiom,
                           '------------------------------------']
    
    with open(csv_sentence_file_name, 'r', encoding='UTF8', newline='') as f:
      csv_reader = csv.reader(f, delimiter=',')
      
      #Collect detected senteces
      for sentence in csv_reader:
        if idiom in sentence[0]:
          idiom_sentence_list += [sentence[0]]
          
    for line in idiom_sentence_list:
      writer.writerow([line])
               
print("---- Task Completed ----")
          
          
          
          
  
  