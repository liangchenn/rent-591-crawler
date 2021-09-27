import requests
import time
import re

import pandas as pd
from bs4 import BeautifulSoup


class Rent591Crawler(requests.sessions.Session):
    '''
    Rent 591 Crawler API.
    ''' 

    prefix = 'https://rent.591.com.tw'
    api_prefix = 'https://rent.591.com.tw/home/search/rsList?is_format_data=1&is_new_list=1&type=1'

    def __init__(self, region: str):
        super().__init__()
        self.search_page_url = f"{self.prefix}/?regionid={region}" 
        self.region = region
        self.token = None
        self.headers = None
        self.data = None


    def crawl(self):

        self.get_token_from_search_page()
        self.get_data()

        self.rawdata.to_csv(f"data/region-{self.region}.csv")

        return 

    
    
    def get_token_from_search_page(self):

        res = self.get(self.search_page_url)
        soup = BeautifulSoup(res.text, 'lxml')
        token = soup.select_one('meta[name="csrf-token"]')['content']

        self.token = token

        self.headers = {
            'X-CSRF-TOKEN' : self.token, 
            'X-Requested-With' : 'XMLHttpRequest'
        }

        return res

    
    def get_data(self):

        page = 0
        all_page_df = pd.DataFrame()
        NextPageExist = True

        while NextPageExist:
            time.sleep(.5)
            # print(f'[Region = {self.region}][page= {page+1}]')
            apiurl = f"{self.api_prefix}&regionid={self.region}&firstRow={30*page}"
            api_res = self.get(apiurl, headers=self.headers)
            if api_res.status_code == 200:
                api_json_data = api_res.json()
            else:
                raise ValueError('Wrong Status Code.')

            api_df = pd.DataFrame(api_json_data['data']['data'])

            if page == 0:
                raw_info = api_json_data['data']['page']
                try:
                    total_rows = re.search('data-total="(\d+)"', raw_info).group(1)
                    total_page = (int(total_rows) // 30) + 1 
                    # print(total_page, total_rows)
                except:
                    total_page = 1

            if len(api_df) > 0:
                all_page_df = all_page_df.append(api_df)

                print(f'[Region = {self.region}][page= {page+1} / total : {total_page}]')


            else:
                NextPageExist = False
            
            page += 1

        self.rawdata = all_page_df

        return 


if __name__ == '__main__':
    worker = Rent591Crawler(region='25')
    worker.get_token_from_search_page()
    df = worker.get_data()

    # print(len(df))
    # print()
    # print(df)





