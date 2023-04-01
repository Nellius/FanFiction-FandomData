"""Scrape fandom data from Fanfiction.net and write JSON files."""

# -*- coding: utf-8 -*-
import sys
import time
import re
import os
import json
from datetime import datetime, timezone
from functools import reduce
from bs4 import BeautifulSoup
import undetected_chromedriver as uc


class SectionData:
    """Scrape self.url and store section fandom data.

    Attributes:
        url (str): section url
        id (str): section id
        name (str): section name
        crossover (str): 'not_crossover' or 'crossover'
        fandoms (list): list of fandom data {'name': str, 'url': str, 'rough_story_number': int}

    """

    def __init__(self, url: str):
        """Initialize.

        Args:
            url (str): Fanfiction.net section page
                       ex: https://www.fanfiction.net/book/

        """
        url_array = url.split('/')
        self.url = url
        self.id = url_array[-2]
        self.name = ''
        self.crossover = 'crossover' if url_array[-3] == "crossovers" else 'not_crossover'
        self.fandoms = []

    def scrape(self, html: str):
        """Scrape self.url and set self.name and self.fandoms."""
        soup = BeautifulSoup(html, "lxml")

        regex = r"( Crossover)? \| FanFiction$"
        self.name = re.sub(regex, '', soup.find('title').string)

        div_tags = soup.find('div', id='list_output').find_all('div')
        for div_tag in div_tags:
            a_tag = div_tag.find('a')
            url = 'https://www.fanfiction.net' + a_tag.get('href')

            # * a_tag.get('title') might contain "\'" or '\""'
            # * "lxml" can't parse a_tag.get('title') with '\""' correctly
            # * a_tag with long text is abbreviated by '...'
            # If a_tag.get('title') contain '\""',
            if re.search(r"\\$", a_tag.get('title')):
                # If a_tag.text is abbreviated by '...'
                if re.search(r"\.\.\.$", a_tag.text):
                    # Get fandom name by scraping url
                    name = self.get_fandom_name(url)
                else:
                    # Use a_tag.text
                    name = a_tag.text
            else:
                # Replace "\'" with "'" and use a_tag.get('title')
                name = re.sub(r"\\'", "'", a_tag.get('title'))

            str_numbers = div_tag.find('span').text[1:-1] \
                .replace(',', '').replace('K', ' 1000').replace('M', ' 1000000').split(' ')
            numbers = [float(i) for i in str_numbers]
            rough_story_number = int(reduce((lambda x, y: x * y), numbers))

            fandom = {
                'name': name,
                'url': url,
                'rough_story_number': rough_story_number
            }
            self.fandoms.append(fandom)

    @staticmethod
    def get_fandom_name(url: str) -> str:
        """Scrape browse page url and return fandom name.

        Args:
            url (str): url of fandom browse page
                       ex: https://www.fanfiction.net/book/Harry-Potter/

        Returns:
            str: scraped fandom name

        """

        options = uc.ChromeOptions()
        options.add_argument('--headless=new')
        chrome = uc.Chrome(options=options)

        chrome.get(url)
        html = chrome.page_source
        soup = BeautifulSoup(html, "lxml")

        regex = r" (FanFiction Archive|Crossover) \| FanFiction$"
        name = re.sub(regex, '', soup.find('title').string)

        time.sleep(5)
        chrome.quit()
        return name


class FandomData:
    """Make fandom database by each SectionData and write json file.

    Attributes:
        sections (list): list of SectionData
        date (str): ISO 8601 date when json file was written
        database (dict): fandom database
                         overridden by make_database(), make_unified_database(),
                         and make_exceptional_fandom_database()

    """

    def __init__(self, urls: list):
        """Initialize.

        Args:
            urls (list): fandom url list for SectionData

        """
        self.sections = [SectionData(url) for url in urls]
        self.date = datetime.now(timezone.utc).isoformat()
        self.database = {}

    def scrape(self):
        """Scrape all urls of self.sections."""
        print("Start scraping...")

        length = len(self.sections)
        for i, section in enumerate(self.sections):
            options = uc.ChromeOptions()
            options.add_argument('--headless=new')
            chrome = uc.Chrome(options=options)

            print(section.url)
            try:
                chrome.get(section.url)
                html = chrome.page_source
                section.scrape(html)
            except Exception as e:
                print("Get page source error!")
                print(e)

            chrome.quit()
            if i != length - 1:
                time.sleep(10)

    def make_database(self):
        """Make self.database which has the same structure of Fanfiction.net."""
        print("Make fandom database")
        self.database = {'date': self.date}

        for section in self.sections:
            if section.crossover not in self.database:
                self.database[section.crossover] = {}
            self.database[section.crossover][section.id] = {}
            database = self.database[section.crossover][section.id]

            database['name'] = section.name
            database['url'] = section.url
            database['fandoms'] = section.fandoms

    def make_unified_database(self):
        """Make self.database as unified fandom database sorted by fandom['name'] key."""
        print("Make unified fandom database")
        self.database = {
            'date': self.date,
            # ! all [] generated by dict.fromkeys(['a', 'b', 'c'], []) have same address
            'sections': dict.fromkeys([section.id for section in self.sections])
        }

        for section in self.sections:
            if not isinstance(self.database['sections'][section.id], dict):
                self.database['sections'][section.id] = {}
            section_dict = self.database['sections'][section.id]

            if 'name' not in section_dict:
                section_dict['name'] = section.name
            section_dict[section.crossover + "_url"] = section.url

        fandom_names = [fandom['name']
                        for section in self.sections for fandom in section.fandoms]
        # ! all [] generated by dict.fromkeys(['a', 'b', 'c'], []) have same address
        self.database['fandoms'] = dict.fromkeys(sorted(fandom_names))

        for section in self.sections:
            for fandom in section.fandoms:
                if not isinstance(self.database['fandoms'][fandom['name']], list):
                    self.database['fandoms'][fandom['name']] = []

                self.database['fandoms'][fandom['name']].append({
                    'section_id': section.id,
                    'crossover': section.crossover == 'crossover',
                    'url': fandom['url'],
                    'rough_story_number': fandom['rough_story_number']
                })

    def make_exceptional_fandom_database(self):
        """Make self.database as crossover fandom database which name contain ' & '."""
        print("Make exceptional fandom crossover database")
        self.database = {'date': self.date}

        exceptional_fandomlist = [
            fandom['name'] for section in self.sections for fandom in section.fandoms
            if section.crossover == 'crossover' and ' & ' in fandom['name']
        ]
        self.database['fandoms'] = sorted(list(dict.fromkeys(exceptional_fandomlist)))

    def write_json_file(self, filename: str):
        """Write self.database as json file by filename.

        Args:
            filename (str): json filename

        """
        print("Write " + filename)

        file_path = os.path.dirname(filename)
        if not os.path.exists(file_path):
            os.makedirs(file_path)

        with open(filename, 'w') as json_file:
            json.dump(self.database, json_file, indent=4, ensure_ascii=False)


def main():
    """Scrape section_urls and write json files."""
    section_urls = [
        'https://www.fanfiction.net/anime/',
        'https://www.fanfiction.net/book/',
        'https://www.fanfiction.net/cartoon/',
        'https://www.fanfiction.net/comic/',
        'https://www.fanfiction.net/game/',
        'https://www.fanfiction.net/misc/',
        'https://www.fanfiction.net/play/',
        'https://www.fanfiction.net/movie/',
        'https://www.fanfiction.net/tv/',
        'https://www.fanfiction.net/crossovers/anime/',
        'https://www.fanfiction.net/crossovers/book/',
        'https://www.fanfiction.net/crossovers/cartoon/',
        'https://www.fanfiction.net/crossovers/comic/',
        'https://www.fanfiction.net/crossovers/game/',
        'https://www.fanfiction.net/crossovers/misc/',
        'https://www.fanfiction.net/crossovers/play/',
        'https://www.fanfiction.net/crossovers/movie/',
        'https://www.fanfiction.net/crossovers/tv/',
    ]

    fandom_data = FandomData(section_urls)
    fandom_data.scrape()

    json_filename = './json/fandom.json'
    unified_json_filename = './json/unified-fandom.json'
    exceptional_fandom_json_filename = './json/exceptional-fandom.json'

    fandom_data.make_database()
    fandom_data.write_json_file(json_filename)
    fandom_data.make_unified_database()
    fandom_data.write_json_file(unified_json_filename)
    fandom_data.make_exceptional_fandom_database()
    fandom_data.write_json_file(exceptional_fandom_json_filename)


if __name__ == '__main__':
    main()
