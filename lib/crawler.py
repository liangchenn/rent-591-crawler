import requests
import time
import re
import os
import arrow

import pandas as pd
from bs4 import BeautifulSoup
from requests import exceptions


class Rent591Crawler(requests.sessions.Session):
    '''
    A Basic Rent 591 Crawler.
    ''' 

    prefix = 'https://rent.591.com.tw'
    api_prefix = 'https://rent.591.com.tw/home/search/rsList?is_format_data=1&is_new_list=1&type=1'

    def __init__(self, region: str, datafolder: str = './data/'):
        super().__init__()
        self.search_page_url = f"{self.prefix}/?regionid={region}" 
        self.region = region
        self.folder = datafolder
        self.token = None
        self.headers = None
        self.data = None


    def crawl(self):

        self.get_token_from_search_page()
        self.get_data()
        self.save(f"region-{self.region}.csv")

        return 


    def get_data(self):
        '''
        Get the whole house data in the given region.
        '''

        # empty DataFrame for results from all pages
        all_pages_df = pd.DataFrame()
        
        # crawler loop 
        page = 0
        isNextPageExist = True
        while isNextPageExist:     
            time.sleep(.5)
            data_json = self._get_data_from_one_page(page)
            one_page_df = pd.DataFrame(data_json['data']['data'])

            # get the total page number at first loop
            if page == 0:
                total_page = self.get_total_page_number(data_json)

            if len(one_page_df) > 0:
                all_pages_df = all_pages_df.append(one_page_df)
                print(f'[Region = {self.region}][page= {page+1} / total : {total_page}]')

            else:
                isNextPageExist = False
            page += 1
        self.rawdata = all_pages_df

        return 

    
    def _get_data_from_one_page(self, page: int):
        '''
        Get the house data from one page in the given region.

        Parameters
        ----------
            self (Rent591Crawler) : A  Rent591Crawler object
            page (int): The current page number to collect data

        Returns
        -------
            data (JSON): The house data from given page  
        '''

        try:
            data_url = f"{self.api_prefix}&regionid={self.region}&firstRow={30*page}"
            data_res = self.get(data_url, headers=self.headers)

        except requests.exceptions.RequestException as e:
            raise SystemExit(e)

        
        return data_res.json()
    

    def get_token_from_search_page(self):
        '''
        Get the necessary CSRF token from the search page given the region.
        '''

        # create the crawler session and get to search page
        res = self.get(self.search_page_url)
        # extract CSRF token from page
        soup = BeautifulSoup(res.text, 'lxml')
        token = soup.select_one('meta[name="csrf-token"]')['content']

        # store the token and append it to the header for main crawler
        self.token = token
        self.headers = {
            'X-CSRF-TOKEN' : self.token, 
            'X-Requested-With' : 'XMLHttpRequest'
        }

        return


    def save(self, filename: str):

        folder = self.folder + arrow.now().format('YYYYMMDD')

        if not os.path.exists(folder):
            os.makedirs(f"{folder}")

        path = f"{folder}/{filename}.csv"
        self.rawdata.to_csv(path)

        return 


    @staticmethod
    def get_total_page_number(data):
        '''
        Get the total number of searched results from JSON data.

        Parameters
        ----------
            data (JSON): A JSON data obtained from one page
        
        Returns
        -------
            total_number (int): Total number of searched results
            total_page (int)  : Total number of searched pages 
        '''

        try:
            raw_info = data['data']['page']
            total_rows = re.search('data-total="(\d+)"', raw_info).group(1)
            total_page = (int(total_rows) // 30) + 1 

        except:
            total_page = 1

        return total_page




if __name__ == '__main__':
    worker = Rent591Crawler(region='25', datafolder='../data/')
    worker.crawl()




