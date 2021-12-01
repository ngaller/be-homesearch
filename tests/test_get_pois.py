import tempfile
from unittest.mock import MagicMock

from dagster import build_op_context

from localize_be.ops.get_pois import get_pois


def test_do_geocode():
    with tempfile.NamedTemporaryFile() as f:
        f.write(b"Category;Weight;Address\n")
        f.write(b"School;3;Rue du Culot 2, 1360 Thorembais-Saint-Trond\n")
        f.flush()
        mock_mapquest = MagicMock()
        mock_mapquest.geocode.return_value = (1, 2)
        context = build_op_context(resources={
            "mapquest": mock_mapquest
        }, op_config={
            "path": f.name
        })
        pois = get_pois(context)
        assert len(pois) == 1
        assert pois.iloc[0].Category == "School"
        assert pois.iloc[0].Lat == 1
        assert pois.iloc[0].Lng == 2


def test_do_not_geocode_already_coded():
    with tempfile.NamedTemporaryFile() as f:
        f.write(b"Category;Weight;Address;Lat;Lng\n")
        f.write(b"School;3;Rue du Culot 2, 1360 Thorembais-Saint-Trond;11;22\n")
        f.flush()
        context = build_op_context(resources={
            "mapquest": {}
        }, op_config={
            "path": f.name
        })
        pois = get_pois(context)
        assert pois.iloc[0].Category == "School"
        assert pois.iloc[0].Lat == 11
        assert pois.iloc[0].Lng == 22
