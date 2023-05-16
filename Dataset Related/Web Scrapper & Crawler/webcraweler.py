from asyncio.staggered import staggered_race
from email.policy import strict
import string
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import csv
import pandas as pd
import sys
import os


#Provide a URL and crawler will get all the links present on the webpage.
#Curently made to work with wikipedia as we can spam the Random Article link
#To generate new links, without changing the base URL

# sys.setrecursionlimit(10000)

#Base URL for web crawling
base = 'https://en.wikipedia.org/wiki/Special:Random'

#Files read/created during runtime
csv_file_name = 'urls/URLList_1.csv'     #File being read/written/created

def web(page, WebUrl, mode, link_number):
    if(page > 0):
        url = WebUrl
        code = requests.get(url)
        plain = code.text
        s = BeautifulSoup(plain, 'html.parser')
        links_left = link_number
        header = ['URL']
        
        if os.path.isfile(csv_file_name) == False:
          with open(csv_file_name, 'w', encoding='UTF8', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(header)
            
        #Check if script should append or overwrite the file
        with open(csv_file_name, 'r', encoding='UTF8', newline='') as f:
          csv_reader = csv.reader(f, delimiter=',')
          row_count = sum(1 for row in csv_reader)
          
        if row_count <= 1 or mode == 'overwrite' : 
          open_mode = 'w'
              
        else: 
          open_mode = 'a'
          
        with open(csv_file_name, open_mode, encoding='UTF8', newline='') as f:
            writer = csv.writer(f)
            if open_mode == 'w':
              writer.writerow(header)
            
            #Get the all href links on the current webpage and turn them into abosulute links  
            for link in s.findAll('a', {'class':''}):
                href = link.get('href')
                final_link = str(urljoin(base, href))
                
                #For crawling wikipedia because one page can have dozens of possible edit links etc
                if '&' not in final_link and '#' not in final_link and ':' not in str(href):
                  writer.writerow([final_link])
                  links_left -= 1

                if links_left < 1:
                  break
    
    #For wikipedia random to generate random links until limit is reached
    if links_left > 0:
      web(1, base, 'append', links_left)             
                         
web(1, base, 'overwrite', 20)

#Remove duplicates
df = pd.read_csv(csv_file_name)
df.drop_duplicates(inplace=True)         
df.to_csv(csv_file_name, index=False)  