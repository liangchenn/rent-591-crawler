from lib.crawler import Rent591Crawler



if __name__ == "__main__":

    from tqdm.auto import tqdm

    regions = range(1, 2)
    
    for region in tqdm(regions):
        worker = Rent591Crawler(region)
        worker.crawl()
