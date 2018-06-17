# -*- coding: utf-8 -*-
"""Dowload data from the Dictionary of American Naval Fighting Ships (DANFS)
"""

import urllib
import requests
from os import path
from bs4 import BeautifulSoup

from sqlalchemy import create_engine, Table, Column, String, MetaData

metadata = MetaData()
table_danfs = Table("danfs_ships", metadata,
                    Column('id', String(), primary_key=True),
                    Column('url', String(), nullable=False),
                    Column('title', String()),
                    Column('subtitle', String()),
                    Column('history', String()))

table_confederate = Table("confederate_ships", metadata,
                          Column('id', String(), primary_key=True),
                          Column('url', String(), nullable=False),
                          Column('title', String()),
                          Column('subtitle', String()),
                          Column('history', String()))


class DANFSClient(object):
    BASE_URL = "http://www.history.navy.mil"

    def api_url(self):
        return urllib.parse.urljoin(self.BASE_URL,
                                    "research/histories/ship-histories/danfs/jcr:content/api.json")

    def api_confed_url(self):
        return urllib.parse.urljoin(self.BASE_URL,
                                    "research/histories/ship-histories/confederate_ships/jcr:content.rollup.json")

    def get_groups_list(self):
        r = requests.get(self.api_url(), params={'get': 'groupsList'})
        return r.json()

    def get_sub_groups(self, first):
        r = requests.get(self.api_url(),
                         params={'get': 'subGroupsList',
                                 'first': first})
        return r.json()

    def get_sub_group_ship_list(self, first, start_char, end_char):
        r = requests.get(self.api_url(),
                         params={'get': 'subGroupShipList',
                                 'first': first,
                                 'second': start_char + '-' + end_char})
        return r.json()

    def get_all_ship_urls(self):
        ships = []
        for group in self.get_groups_list()['groups']:
            for subgroup in self.get_sub_groups(group['group'])['subGroups']:
                if 'isEmpty' not in subgroup:
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
        html = r.text
        soup = BeautifulSoup(html, 'lxml')
        try:
            bodyContainer = soup.find("div", class_="bodyContainer")
            text = ''.join(str(x) for x in bodyContainer.find_all(
                "div", class_="text parbase section"))
        except AttributeError:
            print("Problem with text in %s" % path)
            text = ''
        return text

    def get_confederate_groups(self):
        url = self.api_confed_url()
        r = requests.get(url)
        return r.json()

    def get_confederate_ships(self, limit, offset):
        r = requests.get(self.api_confed_url(),
                         params={'offset': offset,
                                 'limit': limit})
        return r.json()

    def get_confederate_ships_all(self):
        ships = []
        for letter in self.get_confederate_groups()['ranges']:
            if 'isEmpty' not in letter:
                pages = self.get_confederate_ships(
                    letter['limit'], letter['offset'])['pages']
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
            bodyContainer = soup.find("div", class_="bodyContainer")
            text = ''.join(str(x) for x in bodyContainer.find_all(
                "div", class_="text parbase section"))
        else:
            print("Cannot find %s" % path)
            text = ''
        return text


def insert_confederate_ships(con):
    client = DANFSClient()
    ins = table_confederate.insert()
    ships = client.get_confederate_ships_all()
    for ship in ships:
        print(ship['title'])
        data = {'title': ship['title'],
                'subtitle': ship['subtitle'],
                'id': path.basename(ship['path']),
                'history': client.get_confederate_ship_text(ship['path']),
                'url': client.get_confederate_ship_url(ship['path'])
                }
        con.execute(ins, **data)


def insert_danfs(con):
    EXCLUDE = ("What's New", )
    client = DANFSClient()
    ins = table_danfs.insert()
    ships = client.get_all_ship_urls()
    for ship in ships:
        ship_id = path.basename(ship['path'])
        print(ship['title'])
        if ship['title'] not in EXCLUDE:
            data = {'title': ship['title'],
                    'subtitle': ship['subtitle'],
                    'id': ship_id,
                    'history': client.get_ship_text(ship['path']),
                    'url': client.get_ship_url(ship['path'])
                    }
            con.execute(ins, **data)


def main():
    DB = "sqlite:///dfas.sqlite3"
    new = False
    engine = create_engine(DB)
    metadata.bind = engine
    if new:
        metadata.drop_all()
    metadata.create_all(checkfirst=True)
    con = metadata.bind
    insert_danfs(con)
    # insert_confederate_ships(con)


if __name__ == "__main__":
    main()
