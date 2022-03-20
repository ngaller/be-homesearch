import json
import sqlite3
from contextlib import closing
from sqlite3 import Row

from localize_be.config import config


class HomeCache:
    def __init__(self, path):
        self.con = sqlite3.connect(path)
        with closing(self.con.cursor()) as cur:
            cur.execute("""
            create table if not exists homes (
                id int primary key, city text, postal_code text, price int, 
                property_type text, synced int default 0, geocoded int default 0, 
                details text
            )
            """)
            self.con.commit()

    def close(self):
        self.con.close()

    def add_home(self, data, details, synced=False):
        """
        Add a home to the cache.  If it is already there, update the data and set the synced flag to 0.
        """
        with closing(self.con.cursor()) as cur:
            cur.execute("""
            insert into homes (id, property_type, city, postal_code, price, details, synced)
            values (:id, :property_type, :city, :postal_code, :price, :details, :synced) 
            on conflict(id) do update set price=excluded.price, 
                                          details=excluded.details, 
                                          synced=:synced
            """, dict(details=json.dumps(details),
                      synced=1 if synced else 0,
                      **data))
            self.con.commit()

    def update_home(self, id_, details):
        """Update home details and set synced to 0"""
        with closing(self.con.cursor()) as cur:
            cur.execute("update homes set synced=0, details=? where id=?", (json.dumps(details), id_))
            self.con.commit()

    def set_synced(self, id_):
        with closing(self.con.cursor()) as cur:
            cur.execute("update homes set synced=1 where id=?", (id_,))
            self.con.commit()

    def set_geocoded(self, id_):
        with closing(self.con.cursor()) as cur:
            cur.execute("update homes set geocoded=1 where id=?", (id_,))
            self.con.commit()

    def has_home(self, id_, price):
        with closing(self.con.cursor()) as cur:
            # TODO we should have some way to update the ones that have a modified price...
            cur.execute("select id from homes where id=?", (id_,))
            return cur.fetchall()

    def get_homes_geocoded(self):
        """Get already geocoded homes (synced or not)"""
        with closing(self.con.cursor()) as cur:
            cur.execute("select id, details from homes where geocoded=1 and details <> '{}'")
            return [(row[0], json.loads(row[1])) for row in cur.fetchall()]

    def get_homes_to_sync(self):
        with closing(self.con.cursor()) as cur:
            cur.execute("select id, details from homes where geocoded=1 and synced=0 and details <> '{}'")
            return [(row[0], json.loads(row[1])) for row in cur.fetchall()]

    def get_homes_to_geocode(self):
        with closing(self.con.cursor()) as cur:
            cur.execute("select id, details from homes where geocoded=0 and details <> '{}'")
            return [(row[0], json.loads(row[1])) for row in cur.fetchall()]

    def get_homes_missing_details(self):
        with closing(self.con.cursor()) as cur:
            sql = "select id, property_type, postal_code, city from homes where details = '{}'"
            cur.execute(sql)
            self.con.row_factory = Row
            return cur.fetchall()

    def get_synced_ids(self):
        with closing(self.con.cursor()) as cur:
            cur.execute("select id from homes where synced=1")
            return [row[0] for row in cur.fetchall()]


def get_home_cache():
    db = HomeCache(config["HOME_CACHE"]["PATH"])
    return db
