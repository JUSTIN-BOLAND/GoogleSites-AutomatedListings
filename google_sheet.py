'''
Created on Jan 24, 2018

@author: Victor Fateh
'''

from __future__ import print_function
import httplib2
import os

from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage
import gspread
import main

try:
    import argparse

    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None

# If modifying these scopes, delete your previously saved credentials
# at ~/.credentials/sheets.googleapis.com-python-quickstart.json
SCOPES = 'https://www.googleapis.com/auth/spreadsheets'
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'Google Sheets API Python Quickstart'

REMOVE_LIST = []


def get_credentials():
    """Gets valid user credentials from storage.

    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth2 flow is completed to obtain the new credentials.

    Returns:
        Credentials, the obtained credential.
    """
    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, '.credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir,
                                   'sheets.googleapis.com-python-quickstart.json')

    store = Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        if flags:
            credentials = tools.run_flow(flow, store, flags)
        else:  # Needed only for compatibility with Python 2.6
            credentials = tools.run(flow, store)
        print('Storing credentials to ' + credential_path)
    return credentials


# Updates Inbound spreadsheet B column with 'y' if the URL was successfully posted to google sites
def update_post(url, out_link):
    credentials = get_credentials()
    gc = gspread.authorize(credentials)
    wks = gc.open("Craigslist Listings").worksheet("Inbound")

    cell = wks.find(url)
    wks.update_cell(cell.row, cell.col+1, 'y')
    wks.update_cell(cell.row, cell.col + 2, out_link)


def clean_expired():
    credentials = get_credentials()
    gc = gspread.authorize(credentials)
    wks = gc.open("Craigslist Listings").worksheet("Inbound")

    values_list = wks.col_values(1)

    for url in values_list:
        if main.not_deleted(url):
            cell = wks.find(url)
            wks.delete_row(cell.row)


# Returns list of URLs from Inbound sheet to be scraped
def pull_listings():
    """
    Pull from inbound sheet
    https://docs.google.com/spreadsheets/d/1bg3ZKf9e6qLRqyuZwCUT4-iZARHnEPw9pedwkcDxZ1o/edit
    """

    url_list = []

    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    discoveryUrl = ('https://sheets.googleapis.com/$discovery/rest?'
                    'version=v4')
    service = discovery.build('sheets', 'v4', http=http,
                              discoveryServiceUrl=discoveryUrl)

    spreadsheetId = '1bg3ZKf9e6qLRqyuZwCUT4-iZARHnEPw9pedwkcDxZ1o'
    rangeName = 'Inbound!A1:B'
    result = service.spreadsheets().values().get(spreadsheetId=spreadsheetId, range=rangeName).execute()
    values = result.get('values', [])

    if not values:
        print('No data found.')
    else:
        try:
            for row in values:
                if row[1] == 'n':
                    if main.not_deleted(row[0]):
                        url_list.append(row[0])
                    else:
                        pass
                if row[1] == 'x':
                    REMOVE_LIST.append(row[0])
        except IndexError:
            pass
    return url_list


# Uploads scraped content to Listings spreadsheet
def send_listings(listing_sheet):
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    discoveryUrl = ('https://sheets.googleapis.com/$discovery/rest?'
                    'version=v4')
    service = discovery.build('sheets', 'v4', http=http,
                              discoveryServiceUrl=discoveryUrl)

    spreadsheetId = '1bg3ZKf9e6qLRqyuZwCUT4-iZARHnEPw9pedwkcDxZ1o'
    rangeName = 'Listings!A1:F'
    my_body = {
        "range": "Listings!A1:F",
        "majorDimension": "ROWS",
        "values": listing_sheet
    }

    service.spreadsheets().values().append(spreadsheetId=spreadsheetId, range=rangeName, body=my_body, valueInputOption='USER_ENTERED').execute()
    print("Listings Sheet Updated with non-posted urls")

