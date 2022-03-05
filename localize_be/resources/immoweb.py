"""
Wrapper for Immoweb scraping
"""
import re
from dataclasses import dataclass

import requests
import random
import time
import json

from localize_be.config import logger
from bs4 import BeautifulSoup
from fake_useragent import UserAgent

BASE = "https://www.immoweb.be/fr"
MAX_SEARCH_PAGES = 5


@dataclass
class SearchConfig:
    search_url: str
    home_url: str


SEARCHES = {
    "Home": SearchConfig(
        search_url="https://www.immoweb.be/fr/recherche?propertyTypes=HOUSE"
                   "&minSurface=140&maxSurface=350&maxLandSurface=5000"
                   "&postalCodes=BE-1315,BE-1357,BE-1360,BE-1367,BE-1370,BE-1457,BE-5030,BE-5031,BE-5080,BE-5310"
                   "&transactionTypes=FOR_SALE&minPrice=175000&priceType=PRICE&minBedroomCount=3&countries=BE"
                   "&maxPrice=470000&orderBy=newest",
        home_url="https://www.immoweb.be/fr/annonce/maison/a-vendre/{}/{}/{}"
    ),
    "Land": SearchConfig(
        search_url="https://www.immoweb.be/fr/recherche/terrain-a-batir/a-vendre?"
                   "countries=BE&maxLandSurface=5000&maxPrice=180000&minLandSurface=800&minPrice=50000&"
                   "postalCodes=BE-5081,1315,1357,1360,1370,5031,5310&priceType=PRICE&orderBy=newest",
        home_url="https://www.immoweb.be/fr/annonce/terrain-a-batir/a-vendre/{}/{}/{}"
    )
}


class ImmowebAPI:
    def __init__(self, get_delay_range=(3, 10)):
        self.get_delay_range = get_delay_range
        self.session = requests.Session()
        ua = UserAgent()
        self.session.headers['User-Agent'] = ua.random

    def search_homes(self):
        for property_type, search in SEARCHES.items():
            for page in range(1, MAX_SEARCH_PAGES + 1):
                logger.debug(f"search {property_type}: retrieving page {page}")
                url = search.search_url
                if page > 1:
                    url += '&page={}'.format(page)
                search_page = self._download(url)
                # the data is in a JSON
                results = search_page.find('iw-search').attrs[':results']
                results = json.loads(results)
                for home in results:
                    price = home["price"]["mainValue"] or home["price"]["maxRangeValue"]
                    if not price:
                        continue
                    yield {
                        "id": int(home["id"]),
                        "city": home["property"]["location"]["locality"],
                        "postal_code": str(home["property"]["location"]["postalCode"]),
                        "price": price,
                        "property_type": property_type,
                    }

    def get_home(self, id_, property_type, locality, postal_code):
        # https://www.immoweb.be/fr/annonce/maison/a-louer/mont-st-guibert/1435/8736394?searchId=5ecb8fc950a33
        logger.debug(f'Getting home {id_}')
        url = SEARCHES[property_type].home_url.format(
            re.sub('[^a-z]', '-', locality.lower()),
            postal_code,
            id_)
        soup = self._download(url)
        data = soup.find('script', string=re.compile("^\\s*window.classified = "))
        if not data:
            raise Exception("Could not find classified in document")
        script_content = data.contents[0]
        assert isinstance(script_content, str)
        script_content = re.sub('^\\s*window.classified = ', '', script_content)
        script_content = re.sub(';\\s*$', '', script_content)
        # the data is in a JSON in "classified"
        ad = json.loads(script_content)
        prop_data = ad['property']
        location = prop_data['location']
        price = ad["price"]["mainValue"] or ad["price"]["maxRangeValue"]
        return {
            'Code #': ad['id'],
            'Type': property_type,
            'Postal code': prop_data['location']['postalCode'],
            'Price': price,
            'City': locality,
            'Street': '{} {}'.format(location['street'], location['number'] or '') if location['street'] else '',
            'SqMeter': prop_data['netHabitableSurface'],
            'Land': (prop_data['land'] or {}).get('surface', 0),
            'Lat': location['latitude'],
            'Lng': location['longitude'],
            'Bedrooms': prop_data['bedroomCount'],
            'Attic': 'Yes' if prop_data['hasAttic'] else 'No',
            'Basement': 'Yes' if prop_data['hasBasement'] else 'No',
            'Garage': 'Yes' if prop_data['parkingCountIndoor'] else 'No',
            'Pool': 'Yes' if prop_data['hasSwimmingPool'] else 'No',
            'Office': 'Yes' if ((prop_data.get('specificities') or {}).get('office') or {}).get('surface') else 'No',
            'Energy': (ad['transaction']['certificates'] or {}).get('epcScore'),
            'Image.Url': ad['media']['pictures'][0]['mediumUrl'],
            'Link.Url': url
        }

    def _download(self, url):
        time.sleep(random.randrange(*self.get_delay_range))
        r = self.session.get(url)
        r.raise_for_status()
        soup = BeautifulSoup(r.content, "html.parser")
        return soup


def get_immoweb():
    return ImmowebAPI()
