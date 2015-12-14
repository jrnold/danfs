# -*- coding: utf-8 -*-
"""Dowload data from the Dictionary of American Naval Fighting Ships (DANFS)
"""

import urllib
import requests
import json
from bs4 import BeautifulSoup



class DANFSClient(object):
    BASE_URL =  "http://www.history.navy.mil"
   
    def api_url(self):
        return urllib.parse.urljoin(self.BASE_URL,
                                    "research/histories/ship-histories/danfs/jcr:content/api.json")
                                    
    def api_confed_url(self):
        return urllib.parse.urljoin(self.BASE_URL,
        "research/histories/ship-histories/confederate_ships/jcr:content.rollup.json")
    
    def get_groups_list(self):
        r = requests.get(self.api_url(), params = {'get' : 'groupsList'})
        return r.json()
    
    def get_sub_groups(self, first):
        r = requests.get(self.api_url(),
                         params = {'get' : 'subGroupsList',
                         'first': first})
        return r.json()
    
    def get_sub_group_ship_list(self, first, start_char, end_char):
        r = requests.get(self.api_url(),
                         params = {'get' : 'subGroupShipList',
                         'first': first,
                         'second': start_char + '-' + end_char})
        return r.json()
    
    def get_all_ship_urls(self):
        ships = []
        for group in self.get_groups_list()['groups']:
            for subgroup in self.get_sub_groups(group['group'])['subGroups']:
                if not 'isEmpty' in subgroup:
                    newships = self.get_sub_group_ship_list(group['group'], 
                                                     subgroup['rangeStartChar'],
                                                     subgroup['rangeEndChar'])['DANFs']
                    ships += newships           
        return ships

    def get_ship_url(self, path):
        return urllib.parse.urljoin(self.BASE_URL, path + '.html')

    def get_ship_text(self, path):
        shipurl = self.get_ship_url(path)
        r = requests.get(shipurl)
        if r.status_code == requests.codes.ok:
            html = r.text
            soup = BeautifulSoup(html, 'lxml')
            bodyContainer = soup.find("div", class_ = "bodyContainer")
            text = ''.join(str(x) for x in bodyContainer.find_all("div", class_ = "text parbase section"))
        else:
            print("Cannot find %s" % path)
            text = ''
        return text 
       
    def get_confederate_groups(self):
        url = self.api_confed_url()
        r = requests.get(url)
        return r.json()
        
    def get_confederate_ships(self, limit, offset):
        r = requests.get(self.api_confed_url(), 
                         params = {'offset': offset,
                                   'limit': limit})
        return r.json() 
        
    def get_confederate_ships_all(self):
        ships = []
        for letter in self.get_confederate_groups()['ranges']:
            if not 'isEmpty' in letter:
                pages = self.get_confederate_ships(letter['limit'], letter['offset'])['pages']
                ships += pages
        return ships
        
    def get_confederate_ship_url(self, path):
        return urllib.parse.urljoin(self.BASE_URL, path + '.html')
        
    def get_confederate_ship_text(self, path):
        shipurl = self.get_confederate_ship_url(path)
        r = requests.get(shipurl)
        if r.status_code == requests.codes.ok:
            html = r.text
            soup = BeautifulSoup(html, 'lxml')
            bodyContainer = soup.find("div", class_ = "bodyContainer")
            text = ''.join(str(x) for x in bodyContainer.find_all("div", class_ = "text parbase section"))
        else:
            print("Cannot find %s" % path)
            text = ''
        return text

def get_confederate_ships():
    client = DANFSClient()
    data = []
    for ship in client.get_confederate_ships_all():
        print(ship['title'])
        data.append({'url': client.get_confederate_ship_url(ship['path']),
                 'title': ship['title'],
                 'subtitle': ship['subtitle'],
                 'text': client.get_confederate_ship_text(ship['path'])})
    return data

def get_danfs():
    client = DANFSClient()
    data = []
    for ship in client.get_all_ship_urls():
        print(ship['title'])
        data.append({'url': client.get_ship_url(ship['path']),
                 'title': ship['title'],
                 'subtitle': ship['subtitle'],
                 'text': client.get_ship_text(ship['path'])})
    return data
       
def main():
    DANFS_FILE = "danfs.json"
    CONFED_FILE = "confederate_ships.json"
    with(open(DANFS_FILE, "w")) as f:
        print("Writing to %s" % DANFS_FILE)
        json.dump(get_danfs(), f)
    with(open(CONFED_FILE, "w")) as f:
        print("Writing to %s" % CONFED_FILE)
        json.dump(get_confederate_ships(), f)
    
if __name__ == "__main__": 
    main()

#engine = create_engine("sqlite:///:memory:")
#metadata.bind = engine
#metadata.drop_all()
#metadata.create_all()
#con = metadata.bind
#ins = table_danfs.insert()

#ships = client.get_all_ship_urls()
#for ship in ships[:10]:
#    ship['text'] = client.get_ship_text(ship['path'])
#    con.execute(ins, **ship)

    


    

