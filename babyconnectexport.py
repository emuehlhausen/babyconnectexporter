#! /usr/bin/env python

import logging
import json
import mechanize
import datetime
import getpass
import pandas as pd
from dateutil.relativedelta import relativedelta
from bs4 import BeautifulSoup
from StringIO import StringIO

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("babyconnectexporter")

class BabyConnectExporter(object):
    LOGIN_URL = 'https://www.baby-connect.com/login'
    EXPORT_URL = '/GetCmd?cmd=StatusExport&kid={}&exportType=2&dt={}/1/{}'
    MY_KIDS_KEY = "\"myKids\":"

    @staticmethod
    def find_closing_bracket(text):
        assert text[0] == '[', 'first character must be the opening brace'
    
        position = 1
        num_braces = 1
        while num_braces > 0:
            if text[position] == '[':
                num_braces += 1
            elif text[position] == ']':
                num_braces -= 1
            position += 1
    
        return position
    
    def fetch_all_data(self, kid_name, kid_id, bday):
        logger.info('Fetching all data for ' + kid_name + ' (Id: ' + str(kid_id) + ')')

        data = []

        today = datetime.datetime.now().date()
        birth_date = datetime.datetime.strptime(bday, '%m/%d/%Y')
        current_date = datetime.date(birth_date.year, birth_date.month, 1) # first day of birth month
        while current_date <= today:
            url = self.EXPORT_URL.format(kid_id, current_date.month, current_date.year)
            logger.debug(url)
            export_response = self.br.open_novisit(url)
            csv_contents = StringIO(export_response.read())
            df = pd.read_csv(csv_contents, parse_dates=['Start Time', 'End Time'])

            logger.info(current_date.strftime('%Y-%m-%d') + ': ' + str(len(df)) + ' entries')
            if len(df) > 0: 
                data.append(df)
    
            current_date = current_date + relativedelta(months=+1)

        filename = '{}.csv'.format(kid_name)
        logger.info('Writing ' + filename) 
        all_data = pd.concat(data).sort_values('Start Time')
        all_data.to_csv(filename, index=False)

    def __init__(self):
        self.br = mechanize.Browser()

    def export_data(self, email, password):
        logger.info('Attempting login')
        login_form_response = self.br.open(self.LOGIN_URL)
        self.br.form = self.br.forms()[0]
        self.br['email'] = email
        self.br['pass'] = password
        home_page_response = self.br.submit()
        
        logger.info('Getting list of children')
        home_page = BeautifulSoup(home_page_response.read(), 'html.parser')
        
        # info about children, including the IDs needed to export data, are spit out in
        # a <script> tag for use by embedded javascript.
        script_contents = None
        for s in home_page.find_all('script'):
            if len(s.contents) > 0 and self.MY_KIDS_KEY in s.contents[0]:
                script_contents = s.contents[0]
        
        start_index = script_contents.find(self.MY_KIDS_KEY) + len(self.MY_KIDS_KEY)
        my_kids_json = script_contents[start_index:]
        my_kids_json = my_kids_json[0:self.find_closing_bracket(my_kids_json)]
        
        my_kids = json.loads(my_kids_json)
        
        logger.info('Found kids: {}'.format(", ".join([x['Name'] for x in my_kids])))
        
        for kid in my_kids:
            self.fetch_all_data(kid['Name'], kid['Id'], kid['BDay'])

        logger.info('Done!')

        return 0
        
if __name__ == "__main__":
    import sys

    print("Please enter credentials for babyconnect.com")
    email = raw_input("Email: ")
    password = getpass.getpass()

    exporter = BabyConnectExporter()
    status = exporter.export_data(email, password)

    sys.exit(status)
    
