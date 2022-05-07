import requests, pickle
from time import sleep
from selenium import webdriver
import chromedriver_binary
from bs4 import BeautifulSoup
import logging
import datetime

# URL = "https://megapersonals.eu/public/post_list/113/1/1"

# driver = webdriver.Chrome()
# driver.get(URL)
# sleep(20)

# cookies_dict = {}
# for cookie in driver.get_cookies():
#     cookies_dict[cookie['name']] = cookie['value']
# driver.close()


logger = logging.getLogger()  # This will be the same logger object as the one configured in main.py

class Scrapper:
    def __init__(self):
        self.cookies_dict = {
            'backURL': 'https%3A%2F%2Fmegapersonals.eu%2Fpublic%2Fpost_list%2F113%2F1%2F1',
            '_gat_gtag_UA_113349993_1': '1',
            '_gid': 'GA1.2.1148061863.1651760402',
            '_ga': 'GA1.2.1295710554.1651760402',
            'JSESSIONID': '00D6D0B20A71EA7D8E56CB7CEE58E1A7',
            'confirmAge': '2',
            '_ym_isad': '2',
            'city': '113',
            '_ym_uid': '1651760400946315569', 
            '_ym_d': '1651760400'
        }
        self.ads_listings_url ="https://megapersonals.eu/public/post_list/113/1/1"
        self.ads_list = self._get_ads_page(self.ads_listings_url)
    
    def _make_request(self, url):
        try:
            response = requests.get(
            url,
            cookies=self.cookies_dict,
            headers={'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36',
                    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
                    'accept-encoding': 'gzip, deflate, br',
                    'accept-language': 'en-US,en;q=0.9',
                    'upgrade-insecure-requests': '1',
                    'scheme': 'https'}
            )
        except Exception as e:
            logger.error("Connection error while making %s request to %s: %s", url, e)
            return None
        
        if response.status_code == 200:  # 200 is the response code of successful requests
            return response
        else:
            logger.error("Error while making %s request to %s: %s (error code %s)", url, response.json(), response.status_code)
            return None
    
    def _get_ads_page(self, url):
        ads_list = []
        page = self._make_request(url)
        soup = BeautifulSoup(page.content, "html.parser")
        ads_elements = soup.find_all("div", class_="listadd")
        
        for ad in ads_elements:
            images = []
            videos = []
            result = dict()
            
            linkElement = ad.find("div", class_="listinfo").find("a", class_="listtitle")
            result['title'] = linkElement.text.strip()
            
            result['link'] = "https://megapersonals.eu" + linkElement['href']
            ad_page = self._make_request(result['link'])
            ad_soup = BeautifulSoup(ad_page.content, "html.parser")
            
            phoneElement = ad_soup.find("span", class_="toShowPhone")
            result['phone'] = phoneElement.find("a").text.strip()        
            if ad_soup.find("span", class_="fromRight"):
                result['name'] = ad_soup.find("span", class_="fromRight").text.strip()[6:]
            else:
                result['name'] = None
            result['date'] = ad_soup.find("div", class_="post_preview_date_time").text.strip()
            result['age'] = ad_soup.find("div", class_="post_preview_age").text.strip()
            result['body'] = ad_soup.find("span", class_="postbody").text.strip()
            if ad_soup.find("p", class_="prev_location"):
                result['location'] = ad_soup.find("p", class_="prev_location").find("span").text.strip()[9:]
            else:
                result['location'] = ad_soup.find("p", class_="prev_city").find("span").text.strip()[5:]
            
            imageElements = ad_soup.find_all("img", class_="post_preview_image")
            videoElements = ad_soup.find_all("video")
            
            for image in imageElements:
                images.append(image['src'])
            result['images'] = images
            
            for video in videoElements:
                video_hash = dict()
                video_hash['thumbnail'] = video['poster']
                video_hash['src'] = video.find("source")['src']
                videos.append(video_hash)
            result['videos'] = videos
            
            ads_list.append(result)
        return ads_list
    
    