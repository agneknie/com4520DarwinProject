from bs4 import BeautifulSoup
import requests
import json
import csv
import re

#Used to quickly generate links for novels that have thousands of chapters
#Make sure that only the number of chapters is changes in the URL

#Files read/created during runtime
file_name = 'urls/URLList_1.csv'     #File being written/created

#Grab chapters for that book
with open(file_name, 'w', encoding='UTF8', newline='') as myFile:
  writer = csv.writer(myFile)
  
  base_url = 'https://lightnovelreader.me/invincible-161711/chapter-'
  
  #Range is chapter numbers
  for x in range(15, 3230):
    full_url = base_url + str(x)
    writer.writerow([full_url])
