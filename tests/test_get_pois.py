import tempfile
from unittest.mock import MagicMock, patch

from localize_be.tasks.get_pois import get_pois


def test_do_geocode():
    with tempfile.NamedTemporaryFile() as f:
        f.write(b"Category;Weight;Address\n")
        f.write(b"School;3;Rue du Culot 2, 1360 Thorembais-Saint-Trond\n")
        f.flush()
        mock_mapquest = MagicMock()
        mock_mapquest.geocode.return_value = (1, 2)
        with patch("localize_be.tasks.get_pois.get_mapquest") as get_mapquest:
            get_mapquest.return_value = mock_mapquest
            pois = get_pois.run(path=f.name)
        assert len(pois) == 1
        assert pois.iloc[0].Category == "School"
        assert pois.iloc[0].Lat == 1
        assert pois.iloc[0].Lng == 2


def test_do_not_geocode_already_coded():
    with tempfile.NamedTemporaryFile() as f:
        f.write(b"Category;Weight;Address;Lat;Lng\n")
        f.write(b"School;3;Rue du Culot 2, 1360 Thorembais-Saint-Trond;11;22\n")
        f.flush()
        pois = get_pois.run(path=f.name)
        assert pois.iloc[0].Category == "School"
        assert pois.iloc[0].Lat == 11
        assert pois.iloc[0].Lng == 22
