import json
import sqlite3
from contextlib import closing

from dagster import InitResourceContext, resource


class HomeCache:
    def __init__(self, path):
        self.con = sqlite3.connect(path)
        with closing(self.con.cursor()) as cur:
            cur.execute("""
            create table if not exists homes (
                id int primary key, city text, postal_code text, price int, 
                synced int default 0, geocoded int default 0, 
                details text
            )
            """)
            self.con.commit()

    def close(self):
        self.con.close()

    def add_home(self, data, details):
        """
        Add a home to the cache.  If it is already there, update the data and set the synced flag to 0.
        """
        with closing(self.con.cursor()) as cur:
            cur.execute("""
            insert into homes (id, city, postal_code, price, details)
            values (:id, :city, :postal_code, :price, :details) 
            on conflict do update set price=excluded.price, details=excluded.details, synced=0
            """, dict(**data, details=json.dumps(details)))
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
            cur.execute("select id from homes where id=? and price=?", (id_, price))
            return cur.fetchall()

    def get_homes_to_sync(self):
        with closing(self.con.cursor()) as cur:
            cur.execute("select id, details from homes where geocoded=1 and synced=0")
            return [(row[0], json.loads(row[1])) for row in cur.fetchall()]

    def get_homes_to_geocode(self):
        with closing(self.con.cursor()) as cur:
            cur.execute("select id, details from homes where geocoded=0")
            return [(row[0], json.loads(row[1])) for row in cur.fetchall()]


@resource(config_schema={"path": str})
def home_cache(init_context: InitResourceContext):
    db = HomeCache(init_context.resource_config["path"])
    return db