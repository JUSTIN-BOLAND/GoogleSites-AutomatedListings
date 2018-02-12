'''
Created on Jan 24, 2018

@author: Victor Fateh
'''


from __future__ import print_function
from bs4 import BeautifulSoup
import requests
import google_sheet
import listing_uploader
import urllib2

def get_title(url):
    soup = BeautifulSoup(requests.get(url).text, 'html.parser')
    try:
        full_title = soup.title.get_text().split("-")
        return full_title[0]
    except AttributeError:
        err = "Title parse error for: " + url
        return err


def get_price(url):
    soup = BeautifulSoup(requests.get(url).text, 'html.parser')
    try:
        price_list = soup.find_all(class_="price")
        return price_list[0].string
    except IndexError:
        print("price index out of range")
        return "$$$"


def get_body(url):
    soup = BeautifulSoup(requests.get(url).text, 'html.parser')
    full_body = soup.find_all(id="postingbody")
    try:
        clean_body = full_body[0].get_text()
        final_body = clean_body.replace('QR Code Link to This Post', '')
        final_body.replace('show contact info', '')
        return final_body.lstrip()
    except AttributeError:
        err = "Body parse error for: " + url
        return err


def raw_body(url):
    soup = BeautifulSoup(requests.get(url).text, 'html.parser')
    full_body = (soup.find_all(id="postingbody"))[0]
    return str(full_body)



def get_images(url):
    soup = BeautifulSoup(requests.get(url).text, 'html.parser')
    img_urls = []
    try:
        for img in soup.find_all('a'):
            if isinstance(img.get('href'), str):
                if "https://images.craigslist.org/" in img.get('href'):
                    img_urls.append(img.get('href'))
        return '\n'.join(img_urls)
    except AttributeError:
        err = "Images parse error for: " + url
        return err

def real_images(url):
    html_page = urllib2.urlopen(url)
    soup = BeautifulSoup(html_page, 'html.parser')
    images = []
    try:
        for img in soup.findAll('a'):
            if("https://images.craigslist.org/" in str(img.get('href'))):
                images.append(img.get('href'))
        return (images)
    except AttributeError:
        err = "Title parse error for: " + url
        return err


# Returns List of posting elements
def sheet_list(url):
    sheet = [url, get_title(url), get_price(url), get_body(url), real_images(url)]
    return sheet

def not_deleted(url):
    soup = BeautifulSoup(requests.get(url).text, 'html.parser')
    removedFlag = soup.find_all(class_="removed")
    if not removedFlag:
        return True
    else:
        return False


def main():
    # Populate list directly from google sheet with inbounds
    # Filled with Craigslist URLS to scrape
    url_list = google_sheet.pull_listings()

    # Loop through all listing URLS and create new page under dynamic pages
    # Update Inbound spreadsheet posted parameter
    # [url, title, price, body, list of img url]
    for index in range(len(url_list)):
        if not_deleted(url_list[index]):
            listing_uploader.upload(sheet_list(url_list[index])[0], sheet_list(url_list[index])[1], sheet_list(url_list[index])[2], sheet_list(url_list[index])[3], sheet_list(url_list[index])[4])
        else:
            print(url_list[index] + " has been deleted")

if __name__=='__main__':
    main()