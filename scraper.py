'''
Created on Jan 24, 2018

@author: Victor Fateh
'''

from bs4 import BeautifulSoup
import requests
import google_sheet
import listing_uploader
import urllib2

def get_title(url):
    soup = BeautifulSoup(requests.get(url).text, 'html.parser')
    full_title = soup.title.get_text().split("-")
    return full_title[0]


def get_price(url):
    soup = BeautifulSoup(requests.get(url).text, 'html.parser')
    price_list = soup.find_all(class_="price")
    return price_list[0].string


def get_body(url):
    soup = BeautifulSoup(requests.get(url).text, 'html.parser')
    full_body = soup.find_all(id="postingbody")
    clean_body = full_body[0].get_text()
    final_body = clean_body.replace('QR Code Link to This Post', '')
    final_body.replace('show contact info', '')
    return final_body.lstrip()


def raw_body(url):
    soup = BeautifulSoup(requests.get(url).text, 'html.parser')
    full_body = (soup.find_all(id="postingbody"))[0]
    return str(full_body)



def get_images(url):
    soup = BeautifulSoup(requests.get(url).text, 'html.parser')
    img_urls = []
    for img in soup.find_all('a'):
        if isinstance(img.get('href'), str):
            if "https://images.craigslist.org/" in img.get('href'):
                img_urls.append(img.get('href'))
    return '\n'.join(img_urls)


def real_images(url):
    html_page = urllib2.urlopen(url)
    soup = BeautifulSoup(html_page, 'html.parser')
    images = []
    for img in soup.findAll('a'):
        if("https://images.craigslist.org/" in str(img.get('href'))):
            images.append(img.get('href'))
    return (images)

# Returns List of posting elements
def sheet_list(url):
    sheet = [url, get_title(url), get_price(url), get_body(url), real_images(url)]
    return sheet


def main():
    # Populate list directly from google sheet with inbounds
    # Filled with Craigslist URLS to scrape
    url_list = google_sheet.pull_listings()

    # Populated with lists for each listing
    # Element : [url, title, price, body, list of img url]

    listing_sheet = []

    try:
        for car in url_list:
            listing_sheet.append(sheet_list(car))
    except IndexError:
        print("End of URL list")

    # Update google sheet with html elements
    #google_sheet.send_listings(listing_sheet)
    #print("Outbound sheet updated")

    # Loop through all listing URLS and create new page under dynamic pages
    # Update Inbound spreadsheet posted parameter
    for car in url_list:
        listing_uploader.upload(sheet_list(car)[0], sheet_list(car)[1], sheet_list(car)[2], sheet_list(car)[3], sheet_list(car)[4])
        #google_sheet.update_post(sheet_list(car)[0])


if __name__=='__main__':
    main()