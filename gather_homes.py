import requests
import random
import time
import re
from requests.exceptions import RequestException
from contextlib import closing
from bs4 import BeautifulSoup
import json
import csv
# !pip install fake-useragent
from fake_useragent import UserAgent
from urllib.parse import unquote

BASE="https://www.immoweb.be/fr"
SEARCH="https://www.immoweb.be/fr/recherche?countries=BE&maxBedroomCount=5&maxPrice=2000&maxSurface=900&minBedroomCount=3&minPrice=950&minSurface=140&postalCodes=5140%2C5020%2C5021%2C5000%2C5022%2C5001%2C5002%2C5024%2C5003%2C5004%2C1341%2C1340%2C1360%2C5080%2C5081%2C5380%2C1315%2C1435%2C1457%2C5030%2C5031%2C5032%2C5310%2C6222%2C1495%2C1450%2C1350%2C1470%2C5190%2C1370%2C1490%2C4280%2C5150%2C1325%2C1301%2C1367%2C1300%2C1342%2C4219&priceType=MONTHLY_RENTAL_PRICE&propertySubtypes=BUNGALOW%2CCHALET%2CFARMHOUSE%2CCOUNTRY_COTTAGE%2CHOUSE%2CTOWN_HOUSE%2CMANSION%2CVILLA%2CMANOR_HOUSE%2CPAVILION&propertyTypes=HOUSE&transactionTypes=FOR_RENT&orderBy=newest"
HOME="https://www.immoweb.be/fr/annonce/maison/a-louer/{}/{}/{}"

class API:
    def __init__(self):
        self.session = requests.Session()
        ua = UserAgent()
        self.session.headers['User-Agent'] = ua.random

    # we don't actually need to login to get the info
    # (which is good, because simulating a login to scrape may not be legal)
    # def login(self, user, password):
    #     self.session.get(BASE)
    #     self.session.headers["X-XSRF-TOKEN"] = unquote(s.cookies["XSRF-TOKEN"])
    #     self.session.post(BASE + '/connexion', {
    #         "login-email": user,
    #         "login-password": password,
    #         "login-remember": "false"
    #         })

    def search(self, page=1):
        url = SEARCH
        if page > 1:
            url += '&page={}'.format(page)
        search = self.__get(url)
        # the data is in a JSON
        results = search.find('iw-search').attrs[':results']
        results = json.loads(results)
        # id
        # property:
        #   type
        #   subtype
        #   title
        #   bedroomCount
        #   location:
        #     locality
        #     postalCode
        #   netHabitableSurface
        #   landSurface
        #   latitude
        #   longitude
        return results

    def get_home(self, home_data):
        # https://www.immoweb.be/fr/annonce/maison/a-louer/mont-st-guibert/1435/8736394?searchId=5ecb8fc950a33
        print('Getting home', home_data['id'])
        location = home_data['property']['location']
        url = HOME.format(
                re.sub('[^a-z]', '-', location['locality'].lower()),
                location['postalCode'],
                home_data['id'])
        soup = self.__get(url)
        data = soup.find('script').contents[0]
        data = re.sub('^\\s*window.dataLayer = ', '', data)
        data = re.sub(';\\s*$', '', data)
        ad = json.loads(data)[0]['classified']
        return {
                'Code #': ad['id'],
                'Postal code': ad['zip'],
                'Rent': ad['price'],
                'City': location['locality'],
                'Street': '{} {}'.format(location['street'], location['number']) if location['street'] else '',
                'SqMeter': home_data['property']['netHabitableSurface'],
                'Land': ad['land']['surface'],
                'Lat': location['latitude'],
                'Lng': location['longitude'],
                'Bedrooms': ad['bedroom']['count'],
                'Attic': 'Yes' if ad['atticExists'] else 'No',
                'Basement': 'Yes' if ad['basementExists'] else 'No',
                'Garage': 'Yes' if ad['parking']['parkingSpaceCount']['indoor'] else 'No',
                'Pool': 'Yes' if ad['wellnessEquipment']['hasSwimmingPool'] else 'No',
                'Office': 'Yes' if ad['specificities']['SME']['office']['exists'] else 'No',
                'Energy': home_data['transaction']['certificate'],
                'Image': home_data['media']['pictures'][0]['mediumUrl'],
                'Link': url
                }
        # the data is in a JSON in "classified"

    def __get(self, url):
        time.sleep(random.randrange(10,25))
        r = self.session.get(url)
        r.raise_for_status()
        soup = BeautifulSoup(r.content, "html.parser")
        return soup


api = API()
all_homes = []
for i in range(1, 5):
    search_results = api.search(i)
    if not search_results:
        break
    for house in search_results:
        try:
            all_homes.append(api.get_home(house))
        except e:
            print('Error getting property', house['id'])

with open('homes.csv', 'w', newline='') as csvfile:
    w = csv.DictWriter(csvfile, fieldnames=all_homes[0].keys())
    w.writeheader()
    for row in all_homes:
        w.writerow(row)

