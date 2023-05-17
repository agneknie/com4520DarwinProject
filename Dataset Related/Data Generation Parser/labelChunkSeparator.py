import os
import csv
import random
import requests
import json
import csv
import re
import pandas as pd
import sys
import time
import os
import language_tool_python

grammar_tool = language_tool_python.LanguageTool('en-US')

def separate_big_csv(lines_per_file, chunks_number , input_big_csv):
  
  maxInt = sys.maxsize

  while True:
      # decrease the maxInt value by factor 10 
      # as long as the OverflowError occurs.

      try:
          csv.field_size_limit(maxInt)
          break
      except OverflowError:
          maxInt = int(maxInt/10)
          
  csv_sentence_file_name = input_big_csv
  in_csvfile = open(csv_sentence_file_name, "r", encoding='utf-8-sig')

  # reader, that would read file for you line-by-line
  reader = csv.reader(in_csvfile)
  
  input_as_list = list(reader)
  
  id_list = {}
  required_sentences = lines_per_file * chunks_number
  
  #all to-be labaled sentences
  all_out_csvfile = open('labelChunks/all_chunks.csv', "w", newline='', encoding='utf-8-sig')
  writer_all = csv.writer(all_out_csvfile)

  header = ["ID", "MWE1", "MWE2", "Language", "sentence_1", "sentence_2", "sim", "alternative_1", "alternative_2", "sentence_previous", "sentence_next", "label"]
  writer_all.writerow(header)
  
  test_counter = 0

  while len(id_list) < required_sentences:

    
    chosen_row = random.choice(input_as_list)
    
    con1 = len(chosen_row[4]) < 150
    con2 = len(chosen_row[5]) < 150
    con3 = len(chosen_row[7]) < 150
    con4 = len(chosen_row[8]) < 150
    con5 = len(chosen_row[9]) < 150
    con6 = len(chosen_row[10]) < 150
    
    con7 = con1 and con2 and con3 and con4 and con5 and con6
 
    if not chosen_row[0] in id_list:
      
      if con7 == False:
        
        pass
      
      else:
        
        errors1 = grammar_tool.check(chosen_row[4])
        errors2 = grammar_tool.check(chosen_row[5])
        errors3 = grammar_tool.check(chosen_row[7])
        errors4 = grammar_tool.check(chosen_row[8])
        errors5 = grammar_tool.check(chosen_row[9])
        errors6 = grammar_tool.check(chosen_row[10])
        
        error_con = (len(errors1) + len(errors2) + len(errors3) + len(errors4) + len(errors5) + len(errors6)) > 5
        
        if error_con:
          
          pass
        
        else:
          
          test_counter += 1
          print(test_counter)
        
          id_list[chosen_row[0]] = 1
          writer_all.writerow(chosen_row)
  
  all_out_csvfile.close()
  in_csvfile.close()
  
  all_chunks_csvfile = open('labelChunks/all_chunks.csv', "r", encoding='utf-8-sig')

  # reader, that would read file for you line-by-line
  reader2 = csv.DictReader(all_chunks_csvfile)

  # number of current line read
  num = 0

  # number of output file
  output_file_num = 1

  # your output file
  out_csvfile = open('labelChunks/label_chunk_{}.csv'.format(output_file_num), "w", encoding='utf-8-sig')

  # writer should be constructed in a read loop, 
  # because we need csv headers to be already available 
  # to construct writer object
  writer = None

  for row in reader2:
      num += 1

      # Here you have your data line in a row variable

      # If writer doesn't exists, create one
      if writer is None:
          writer = csv.DictWriter(
              out_csvfile, 
              fieldnames=row.keys(), 
              delimiter=",", quotechar='"', escapechar='"', 
              lineterminator='\n', quoting=csv.QUOTE_NONNUMERIC
          )
          
      if num == 1:
        writer = csv.writer(out_csvfile)
        writer.writerow(header)
        
        writer = csv.DictWriter(
              out_csvfile, 
              fieldnames=row.keys(), 
              delimiter=",", quotechar='"', escapechar='"', 
              lineterminator='\n', quoting=csv.QUOTE_NONNUMERIC
          )
        #writer.writerow({'Sentence': 'Sentence'})

      # Write a row into a writer (out_csvfile, remember?)
      writer.writerow(row)

      # If we got a 10000 rows read, save current out file
      # and create a new one
      if num > lines_per_file:
          output_file_num += 1
          out_csvfile.close()
          writer = None

          # create new file
          out_csvfile = open('labelChunks/label_chunk_{}.csv'.format(output_file_num), "w", encoding='utf-8')

          # reset counter
          num = 0 

  # Closing the files
  all_chunks_csvfile.close()
  out_csvfile.close()
  

#Possible options are: multiword, literal, non-literal, mw_non_lit, all
#getIdiomList("multiword")

csv_sentence_file_name = 'testCombine/silver_ds_10.csv'
separate_big_csv(100, 50, csv_sentence_file_name)