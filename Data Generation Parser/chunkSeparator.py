import os
import csv
import requests
import json
import csv
import re
import pandas as pd
import sys
import time
import os

def separate_big_csv(lines_per_file, input_big_csv):
  
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
  in_csvfile = open(csv_sentence_file_name, "r", encoding='utf-8')

  # reader, that would read file for you line-by-line
  reader = csv.DictReader(in_csvfile)

  # number of current line read
  num = 0

  # number of output file
  output_file_num = 1

  # your output file
  out_csvfile = open('chunksBronze/chunk_{}.csv'.format(output_file_num), "w", encoding='utf-8')

  # writer should be constructed in a read loop, 
  # because we need csv headers to be already available 
  # to construct writer object
  writer = None

  for row in reader:
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
          
      # if num == 1:
      #   writer.writerow({'Sentence': 'Sentence'})

      # Write a row into a writer (out_csvfile, remember?)
      writer.writerow(row)

      # If we got a 10000 rows read, save current out file
      # and create a new one
      if num > lines_per_file:
          output_file_num += 1
          out_csvfile.close()
          writer = None

          # create new file
          out_csvfile = open('chunksBronze/chunk_{}.csv'.format(output_file_num), "w", encoding='utf-8')

          # reset counter
          num = 0 

  # Closing the files
  in_csvfile.close()
  out_csvfile.close()
  

#Possible options are: multiword, literal, non-literal, mw_non_lit, all
#getIdiomList("multiword")

csv_sentence_file_name = 'idiomaticSentences/all_idiomatic_sentences_bronze_1.csv'
separate_big_csv(100000, csv_sentence_file_name)