import requests
import random
import time
import re
from bs4 import BeautifulSoup
import json
import csv
from fake_useragent import UserAgent

BASE = "https://www.immoweb.be/fr"
SEARCH = "https://www.immoweb.be/fr/recherche?propertyTypes=HOUSE&minSurface=150&maxSurface=350&minLandSurface=600&maxLandSurface=5000&postalCodes=BE-1315,BE-1357,BE-1360,BE-1367,BE-1370,BE-1457,BE-5030,BE-5031,BE-5080,BE-5310&transactionTypes=FOR_SALE&minPrice=200000&priceType=PRICE&minBedroomCount=3&countries=BE&maxPrice=460000&orderBy=newest"
HOME = "https://www.immoweb.be/fr/annonce/maison/a-vendre/{}/{}/{}"


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
        data = soup.find('script', string=re.compile("^\\s*window.dataLayer"))
        if not data:
            raise Exception("Could not find dataLayer in document")
        data = data.contents[0]
        data = re.sub('^\\s*window.dataLayer = ', '', data)
        data = re.sub(';\\s*$', '', data)
        ad = json.loads(data)[0]['classified']
        return {
            'Code #': ad['id'],
            'Postal code': ad['zip'],
            'Price': ad['price'],
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
        time.sleep(random.randrange(10, 25))
        r = self.session.get(url)
        r.raise_for_status()
        soup = BeautifulSoup(r.content, "html.parser")
        return soup


def read_existing(path):
    """
    Retrieve existing homes from the CSV file.
    Return a dictionary by code.
    """
    with open(path, "r") as f:
        reader = csv.DictReader(f)
        return {
            row['Code #']: row
            for row in reader
        }


def get_homes(api, existing_homes):
    for i in range(1, 5):
        search_results = api.search(i)
        if not search_results:
            break
        for house in search_results:
            try:
                existing = existing_homes.get(house["id"])
                if existing:
                    # to speed up retrieval, use existing home data if we have it.
                    print(f"Using existing home data for {existing['Code #']}")
                    # in case the price was updated, we'll have it in the search results
                    existing["Price"] = house["price"]
                    yield existing
                else:
                    yield api.get_home(house)
            except Exception as e:
                print('Error getting property', house['id'], ': ', str(e))
                continue


w = None
existing_homes = read_existing("homes.csv")
new_homes = list(get_homes(API(), existing_homes))
if new_homes:
    with open("homes.csv", 'w', newline='') as csvfile:
        for home in new_homes:
            if not w:
                w = csv.DictWriter(csvfile, fieldnames=home.keys())
                w.writeheader()
            w.writerow(home)
