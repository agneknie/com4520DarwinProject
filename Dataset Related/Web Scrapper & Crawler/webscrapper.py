from bs4 import BeautifulSoup
import requests
import json
import csv
import time
import sys
import pandas as pd

#Provide a .csv file with urls and script will extract desired text
#from the webpage. To change desired text, modify the html elements lookup info
#Do not use sites that require permissions (e.g., Accepting Cookies)

#Files read/created during runtime
csv_urls_file_name = 'urls/URLList_1.csv'        #File being read
csv_scrap_file_name = 'data/dataScrap_1.csv'     #File being written/created

def delete_last_line():
    "Use this function to delete the last line in the STDOUT"

    #cursor up one line
    sys.stdout.write('\x1b[1A')

    #delete last line
    sys.stdout.write('\x1b[2K')

#Load all the links
with open(csv_urls_file_name, 'r', encoding='UTF8', newline='') as f:
  csv_reader = csv.reader(f, delimiter=',')
  urlList = []
  
  for row in csv_reader:
    if row[0] != "URL":
      urlList.append(row[0])

#Start scrapping the data
with open(csv_scrap_file_name, 'a', encoding='UTF8', newline='') as f:
  header = ['Text']
  writer = csv.writer(f) 
  counter = 0
  
  print("---- Scrapping Link Data ----")
  print("---- Scrapping ----")
  
  #Scrape desired text from those links
  for csv_url in urlList:  
    url = csv_url
    response = requests.get(url, allow_redirects=False)
    content = BeautifulSoup(response.content, "html.parser")
    #Modify to change targeted text
    data = content.findAll('p', attrs={"class": ""})
    
    for p in data:
      if p != None:
        writer.writerow([p.text.strip()])
    
    counter += 1

    if counter % 1 == 0 :
      delete_last_line()
      print("---- Links scrapped: " + str(counter) + " ----")

#Remove duplicates
print("---- Removing Duplicates ----")
df = pd.read_csv(csv_scrap_file_name)
df.drop_duplicates(inplace=True)    
df.to_csv(csv_scrap_file_name, index=False)      
print("---- Task Completed ----")