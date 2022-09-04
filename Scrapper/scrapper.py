from urllib import response
import requests
import shutil
from time import sleep
from selenium import webdriver
import chromedriver_binary
from bs4 import BeautifulSoup
from nudenet import NudeDetector
from nudenet import NudeClassifier
import logging
import os
import asyncio
import aiohttp
import html5lib

from censor import Censor


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
        self.Censor = Censor()
        self._headers = {
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36',
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
            'accept-encoding': 'gzip, deflate, br',
            'accept-language': 'en-US,en;q=0.9',
            'upgrade-insecure-requests': '1',
            'scheme': 'https'
        }
        self._cookies_dict = {
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
        self.page_url ="https://megapersonals.eu/public/post_list/113/1/"
        self.ads_list = self._get_ads()
    
    
    def _make_request(self, url):
        """
        With requests time: 3:03.04 minutes
        """
        try:
            response = requests.get(url, cookies=self._cookies_dict, headers=self._headers)
        except Exception as e:
            logger.error("Connection error while making GET request to %s: %s", url, e)
            return None
        if response.status_code == 200:  # 200 is the response code of successful requests
            return response
        else:
            logger.error("Error while making %s request to %s: %s (error code %s)", url, response.json(), response.status_code)
            return None
    
    
    async def _get_site_content(self, url):
        """
        With aiohttp time: 3:03.94 minutes
        """
        try:
            async with aiohttp.ClientSession(headers=self._headers,cookies=self._cookies_dict) as session:
                async with session.get(url) as res:
                    text = await res.read()
        except Exception as e:
            logger.error("Connection error while making GET request to %s: %s", url, e)
            return None
        if text:
            return BeautifulSoup(text.decode('utf-8'), 'html5lib')
        else:
            logger.error("Error while making %s request to %s: %s (error code %s)", url)
            return None
    
    
    def _get_ads_page(self, url):
        ads_page = []
        
        # loop = asyncio.get_event_loop()
        # soup = loop.run_until_complete(self._get_site_content(url))
        page = self._make_request(url)
        soup = BeautifulSoup(page.content, "html.parser")
        
        ads_elements = soup.find_all("div", class_="listadd")
        for ad in ads_elements:
            linkElement = ad.find("div", class_="listinfo").find("a", class_="listtitle")
            ad_page = self._get_ad("https://megapersonals.eu" + linkElement['href'],
                                    linkElement.text.strip())
            ads_page.append(ad_page)
        return ads_page
    
    
    def _get_ad(self, url, title):
        images = []
        videos = []
        result = dict()
        
        ad_page = self._make_request(url)
        ad_soup = BeautifulSoup(ad_page.content, "html.parser")
        
        result['url'] = url
        result['title'] = title
        phoneElement = ad_soup.find("span", class_="toShowPhone")
        result['phone'] = phoneElement.find("a").text.strip().split()[-1]   
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
        
        if not os.path.exists('./media/' + result['phone']):
            os.makedirs('./media/' + result['phone'])
        if imageElements and not os.path.exists('./media/' + result['phone'] + '/images'):
            os.makedirs('./media/' + result['phone'] + '/images')
        if imageElements and not os.path.exists('./media/' + result['phone'] + '/censored'):
            os.makedirs('./media/' + result['phone'] + '/censored')
        if videoElements and not os.path.exists('./media/' + result['phone'] + '/videos'):
            os.makedirs('./media/' + result['phone'] + '/videos')
        
        for image in imageElements:
            image_data = dict()
            image_data['filename'] = image['src'].split('/')[-1]
            image_data['src'] = image['src']
            image_data['location'] = self._save_from_url(type="IMAGE", url=image_data['src'],
                                                        file_path=result['phone'],
                                                        file_name=image_data['filename'])
            image_data['censored'] = self.Censor.censored_image(file_location=image_data['location'],file_path=result['phone'])
            images.append(image_data)
        
        for video in videoElements:
            video_data = dict()
            video_data['thumbnail'] = video['poster']
            video_data['src'] = video.find("source")['src']
            video_data['filename'] = video_data['src'].split('/')[-1]
            video_data['location'] = self._save_from_url(type="VIDEO", url=video_data['src'],
                                                        file_path=result['phone'],
                                                        file_name=video_data['filename'])
            videos.append(video_data)
        
        result['images'] = images
        result['videos'] = videos
        
        # print(result)
        return result
    
    
    def _get_ads(self):
        ads_list = []
        for page_idx in range(1,2):
            ads_list.append(self._get_ads_page(self.page_url + str(page_idx)))
        return ads_list
    
    
    def _save_from_url(self, type, url, file_path, file_name):
        if type == "IMAGE":
            full_path = 'media/' + file_path + '/images/' + file_name
        elif type == "VIDEO":
            full_path = 'media/' + file_path + '/videos/' + file_name
        try:
            # Open the url image, set stream to True, this will return the stream content.
            res = requests.get(url, stream=True, cookies=self._cookies_dict, headers=self._headers)
        except Exception as e:
            logger.error("Connection error while making GET request to %s: %s", url, e)
        # Check if the image was retrieved successfully
        if res.status_code == 200:
            # Set decode_content value to True, otherwise the downloaded image file's size will be zero.
            res.raw.decode_content = True
            # Open a local file with wb ( write binary ) permission.
            with open(full_path, 'wb') as f:
                shutil.copyfileobj(res.raw, f)
        else:
            logger.error("Could not save %s -- %s file to %s", url,type,full_path)
        
        return full_path
    
    