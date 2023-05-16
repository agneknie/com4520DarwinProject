import os
import csv
import nltk.data
from nltk.tokenize import sent_tokenize
import language_tool_python

#nltk.download()

#grammar_tool = language_tool_python.LanguageTool('en-US')
tokenizer = nltk.data.load('tokenizers/punkt/english.pickle')

counter = 0

print("-----------------------------------")
print("--- Sentence tokenizing started ---")
print("-----------------------------------")

with open('sentences/all_sentences.csv', 'w', newline='', encoding='utf-8') as f:
  
  writer = csv.writer(f) #this is the writer object

  for filename in os.listdir("books/"):
    
    if filename.endswith(".txt"):
      
      file_name = "books/" + filename
      file_path = open(file_name, encoding='utf-8')
      data = file_path.read()
      counter += 1
      
      sentence_list = tokenizer.tokenize(data)
 # type: ignore      
      for sentence in sentence_list:
        sentence = " ".join(sentence.split())
        #errors = grammar_tool.check(sentence)
        
        if "Updated editions will replace" in sentence:
          break
        
        #con1 = len(errors) == 0
        con2 = sentence.isupper() == False
        con3 = len(sentence) > 10
        con4 = "CHAPTER" not in sentence
        con5 = "Gutenberg" not in sentence and "GUTENBERG" not in sentence and "eBook" not in sentence
        
        word_list = sentence.split()
        
        con6 = len(word_list) > 4
        
        if con2 and con3 and con4 and con5 and con6:
          
          writer.writerow([sentence])        
      
 
      print("Books tokenized: " + str(counter), end="\r")
      
    else:
      pass

print("------------------------------------")
print("--- Sentence tokenizing finished ---")
print("------------------------------------")