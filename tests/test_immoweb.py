from unittest.mock import patch, PropertyMock, MagicMock

import pytest
from requests import Session

from localize_be.resources.immoweb import ImmowebAPI

test_ads = {
    "iw_ad": {"Price": 215000},
    "iw_ad_2": {"Price": 280000},
    "iw_ad_3": {"Price": 319000, "Garage": "Yes", "Office": "No"}
}


@pytest.mark.parametrize("ad", test_ads.items())
@patch.object(Session, 'get')
def test_get_home(mock_get, ad):
    name, data_to_check = ad
    with open(f"./samples/{name}.html") as f:
        content = MagicMock()
        type(content).content = PropertyMock(return_value=f.read())
        mock_get.return_value = content
    iw = ImmowebAPI(get_delay_range=(0, 1))
    home = iw.get_home(444, "Home", name, 6990)
    for k, v in data_to_check.items():
        assert home[k] == v
