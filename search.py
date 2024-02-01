import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
from urllib.parse import urljoin
from xml.etree import ElementTree as ET

def search_site_for_string(url, search_string):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    text_content = soup.get_text()

    return search_string in text_content

def get_child_xml_urls(parent_xml_url):
    response = requests.get(parent_xml_url)
    root = ET.fromstring(response.content)
    child_urls = [elem.text for elem in root.iter('{http://www.sitemaps.org/schemas/sitemap/0.9}loc')]
    return child_urls

def crawl_page_with_delay(child_xml_url, search_string, delay=1):
    print('Processing child XML:', child_xml_url)
    
    child_urls = get_child_urls_from_xml(child_xml_url)
    
    for url in child_urls:
        print('Processing page:', url)
        
        if search_site_for_string(url, search_string):
            data = [[url]]
            df = pd.DataFrame(data, columns=['Url'])
            df.to_csv('urls_with_search_string.csv', mode='a', header=False, index=False)
            print('CSV has been updated for:', url)
        else:
            print('String not found on this page:', url)

        # Delay before making the next request
        time.sleep(delay)

def get_child_urls_from_xml(child_xml_url):
    response = requests.get(child_xml_url)
    root = ET.fromstring(response.content)
    child_urls = [elem.text for elem in root.iter('{http://www.sitemaps.org/schemas/sitemap/0.9}loc')]
    return child_urls

def check_all_pages_with_delay(parent_xml_url, search_string, delay=1):
    child_xml_urls = get_child_xml_urls(parent_xml_url)
    string_found = False
    
    for child_url in child_xml_urls:
        crawl_page_with_delay(child_url, search_string, delay)
        string_found = string_found or search_site_for_string(child_url, search_string)

    if not string_found:
        print('String not found on any pages.')

if __name__ == "__main__":
    parent_sitemap_url = '#'  # Replace with the actual parent sitemap URL
    search_string = '#'  # Replace with the actual string you want to search for
    delay_between_requests = 1  # Adjust the delay as needed (in seconds)
    
    check_all_pages_with_delay(parent_sitemap_url, search_string, delay_between_requests)
