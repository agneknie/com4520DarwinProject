import os
import sys
import csv
import random
import string
import pandas as pd
import utils
import nltk
from nltk import word_tokenize
from nltk.stem import WordNetLemmatizer 
from numpy import dot
from numpy.linalg import norm
import multiprocessing
import math
import time
from datetime import timedelta
import spacy

if __name__ == '__main__':
  
  nltk.download("stopwords")
  nltk.download('wordnet')

  stopwords = nltk.corpus.stopwords.words('english')
  lemmatizer = WordNetLemmatizer()

  maxInt = sys.maxsize

  while True:
    # decrease the maxInt value by factor 10 
    # as long as the OverflowError occurs.

    try:
      csv.field_size_limit(maxInt)
      break
    except OverflowError:
      maxInt = int(maxInt/10)

#Generate bronze dataset for desired type
#Ignores non-csv files in input folder
#Output is stored in folder 'idiomaticSentences'
#If you run the generator multiple types for the same type, the output file will be overwritten
#---------------------------------------
#ds_type:
#bronze_1 - genarete bronze dataset of approach 1
#bronze_2 - genarete bronze dataset of approach 2
#test     - used for  testing code
#---------------------------------------
#folder_path:
#sentences/  - relative path to folder containing senteces in csv format
#chunks/


def generateDSlemma(ds_folder_path, ds_name):
  
  # your output file
  out_csvfile = open('lemmaSentences/all_idiomatic_sentences_lemma_' + ds_name + '.csv', "w", newline='',encoding='utf-8-sig')
  writer = csv.writer(out_csvfile)

  header = ["ID", "MWE1", "MWE2", "Language", "sentence_1", "sentence_2", "sim", "alternative_1", "alternative_2", "sentence_previous", "sentence_next", "label", "lemma"]
  writer.writerow(header)

  ds_csv = open(ds_folder_path, "r", encoding='utf-8-sig')
  ds_reader = csv.reader(ds_csv)
  next(ds_reader, None)  # skip the headers
  
  sentence_counter = 0
  
  for ds_row in ds_reader:
 
    sentence_1_ds = ds_row[4]

    sentence_1_ds = sentence_1_ds.translate(str.maketrans('', '', string.punctuation))
    sentece_list = [i for i in word_tokenize(sentence_1_ds.lower()) if i not in stopwords] 
    lemmatized_sentence = [lemmatizer.lemmatize(w) for w in sentece_list]
    
    ds_row.append(lemmatized_sentence)
    writer.writerow(ds_row)
    
    sentence_counter += 1
  
  print("Dataset \"" + ds_name + "\" has been lemmatized (" + str(sentence_counter) + " sentences)")
  
  return 'lemmaSentences/all_idiomatic_sentences_lemma_' + ds_name + '.csv'

def generateBronzeThread(startIndex, endIndex, thread_num, word_list, empty_vector, bronze_folder_path, gold_folder_path, sim_threshold):
  
   # your output file
  out_csvfile = open('idiomaticSentences/all_idiomatic_sentences_silver_thread_' + str(thread_num) + '.csv', "w", newline='',encoding='utf-8')
  writer = csv.writer(out_csvfile)
  
  gold_ds = open(gold_folder_path, "r", encoding='utf-8-sig')
  reader = csv.reader(gold_ds)
  
  gold_ds_list = list(reader)
  gold_ds_list.pop(0) # skip the headers
  
  bronze_ds_csv = open(bronze_folder_path, "r", encoding='utf-8-sig')
  bronze_ds_reader = csv.reader(bronze_ds_csv)
  if thread_num == 1:
   next(bronze_ds_reader, None)  # skip the headers
  
  for x in range(startIndex):
    next(bronze_ds_reader, None)  # skip the headers    
  
  iterator = startIndex
  
  sentence_counter = 0
   
  for bronze_row in bronze_ds_reader:
    
    start_time = time.time()
    
    #FOR TESTING
    sim_array = []
    
    
    current_mwe = bronze_row[1]
    
    if iterator >= endIndex:
      break
    
    iterator += 1

    #index 9 while testing with gold, otherwise index 12
    lemmatized_sentence_bronze = bronze_row[12]
    
    word_dict_bronze = dict(zip(word_list, empty_vector))
      
    for lemma_word in lemmatized_sentence_bronze:
      
      try:
        word_dict_bronze[lemma_word] += 1
      except KeyError:
        pass
      
    sentence_bronze_vector = list(word_dict_bronze.values())
    
    for gold_row in gold_ds_list:
      
      gold_mwe = gold_row[1]
      
      if current_mwe == gold_mwe:
        
        lemmatized_sentence_gold = gold_row[9]
        
        word_dict_gold = dict(zip(word_list, empty_vector))
        
        for lemma_word in lemmatized_sentence_gold:
          try:
            word_dict_gold[lemma_word] += 1
          except KeyError:
            pass
          
        sentence_gold_vector = list(word_dict_gold.values())  
        
        cos_sim = dot(sentence_bronze_vector, sentence_gold_vector)/(norm(sentence_bronze_vector)*norm(sentence_gold_vector))

        #FOR TESTING
        sim_array.append(cos_sim)
    
    try:
      bronze_row.append(max(sim_array))
      writer.writerow(bronze_row)
      
      # end_time = time.time()

      # time_elapsed = end_time - start_time
      
      # print("Elapsed time: {:0>8}".format(str(timedelta(seconds=time_elapsed))) + " - thread " + str(thread_num))
      
    except ValueError:
      pass
    
    sentence_counter += 1
    
    if sentence_counter % 500 == 0:
      print("Sentenes covered: " + str(sentence_counter) + " - thread " + str(thread_num))

    # if bronze_sentence_counter % 1000 == 0:
    #   print("Bronze sentences checked: " + str(bronze_sentence_counter))

def generateSilverDS(bronze_folder_path, gold_folder_path, sim_threshold):
  
  if __name__ == '__main__':
  
    print("Generating silver dataset")
    print("Similarity " + str(sim_threshold))
    
    # your output file
    out_csvfile = open('idiomaticSentences/all_idiomatic_sentences_gold.csv', "w", newline='',encoding='utf-8-sig')
    writer = csv.writer(out_csvfile)

    header = ["ID", "MWE1", "MWE2", "Language", "sentence_1", "sentence_2", "sim", "alternative_1", "alternative_2", "sentence_previous", "sentence_next", "label"]
    writer.writerow(header)

    bronze_ds_csv = open(bronze_folder_path, "r", encoding='utf-8-sig')
    bronze_ds_reader = csv.reader(bronze_ds_csv)
    next(bronze_ds_reader, None)  # skip the headers
  
    word_list = set()
    
    for bronze_row in bronze_ds_reader:
  
      sentence_1_bronze = bronze_row[4]

      sentence_1_bronze = sentence_1_bronze.translate(str.maketrans('', '', string.punctuation))
      sentece_list = [i for i in word_tokenize(sentence_1_bronze.lower()) if i not in stopwords] 
      lemmatized_sentence = [lemmatizer.lemmatize(w) for w in sentece_list]
      
      for word in lemmatized_sentence:
        word_list.add(word)
      
    word_list = list(word_list)
    word_num = len(word_list)
    empty_vector = [0] * word_num
    
    # #LENGTH OF FILE(ROWS)
    bronze_ds_csv = open(bronze_folder_path, "r", encoding='utf-8-sig')
    bronze_ds_reader = csv.reader(bronze_ds_csv)
    next(bronze_ds_reader, None)  # skip the headers

    row_count = sum(1 for row in bronze_ds_reader) - 1
    cpu_thread_count = multiprocessing.cpu_count() 
    
    print("------------------------------------")
    
    bronze_lemma_sentences_csv = generateDSlemma(bronze_folder_path, "bronze")
    gold_lemma_sentences_csv = generateDSlemma(gold_folder_path, "gold")
    
    print("------------------------------------")
    
    arg_list = []
    
    for thread_num in range(cpu_thread_count):
      
        startIndex = math.floor((row_count / cpu_thread_count) * thread_num)
        endIndex = math.floor((row_count / cpu_thread_count) * (thread_num + 1))
        thread_number = thread_num + 1
        
        arg_list.append((startIndex, endIndex, thread_number, word_list, empty_vector, bronze_lemma_sentences_csv, gold_lemma_sentences_csv, sim_threshold))

    print("Starting dataset creation")
    
    #Uncomment when general function is done
    with multiprocessing.Pool() as pool:
      L = pool.starmap(generateBronzeThread, arg_list)
      
    print("Dataset creation finished")
    #---------------------------------------------------

if __name__ == '__main__':
  
  start_time = time.time()

  #Bronze dataset - idiomaticSentences/all_idiomatic_sentences_bronze_1.csv
  #Gold semeval dataset - idiomaticSentences/semeval_gold.csv
  #Test bronze sample - idiomaticSentences/all_chunks.csv
  
  #Chunks folder = chunksBronze/
  #Bronze chunk example = chunksBronze/chunk_1.csv

  generateSilverDS(
    "chunksBronze/chunk_1.csv",
    "idiomaticSentences/semeval_gold.csv",
    0.00)

  end_time = time.time()

  time_elapsed = end_time - start_time
  
  print("------------------------------------")
  print("Elapsed time: {:0>8}".format(str(timedelta(seconds=time_elapsed))))