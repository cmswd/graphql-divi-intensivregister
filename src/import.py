import csv
from datetime import datetime
import logging
import os

from sqlalchemy import Integer, Column, String, ForeignKey, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relation
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

logging.basicConfig(format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p', level=logging.INFO)
Base = declarative_base()


class State(Base):
    __tablename__ = 'states'
    code = Column(String, primary_key=True)
    name = Column(String)


class County(Base):
    __tablename__ = 'counties'
    code = Column(String, primary_key=True)
    name = Column(String)

    state_code = Column(String, ForeignKey('states.code'))
    state = relation("State", backref="state")


class Dataset(Base):
    __tablename__ = 'datasets'
    id = Column(Integer, primary_key=True)

    county_code = Column(String, ForeignKey('counties.code'))
    state_code = Column(String, ForeignKey('states.code'))

    county = relation("County")
    state = relation("State")

    # NOTE: These data result from state_code and county_code and should be added dynamically
    bundesland = Column(String)
    gemeindeschluessel = Column(String)

    anzahl_meldebereiche = Column(Integer)
    faelle_covid_aktuell = Column(Integer)
    faelle_covid_aktuell_invasiv_beatmet = Column(Integer)
    anzahl_standorte = Column(Integer)
    betten_frei = Column(Integer)
    betten_belegt = Column(Integer)
    daten_stand = Column(DateTime)
    betten_belegt_nur_erwachsen = Column(Integer)
    betten_frei_nur_erwachsen = Column(Integer)


def dbconnect():
    engine = create_engine('postgresql://postgres:password@localhost:5432/postgres')
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    return Session()


def addCounty(session, data):

    # NOTE: Each county can occur only once
    if session.query(County).filter(County.code == data["code"]).count() > 0:
        return

    logging.debug("Adding %s" % data["name"])

    state_code = data["code"][:2]
    state = session.query(State).filter(State.code == state_code).one()

    county = County()
    county.code = data["code"]
    county.name = data["name"]
    county.state = state

    session.add(county)
    session.commit()


def addMissingCounty(session, data):
    # NOTE: The code of urban counties ends with 000
    if data["code"][-3:] != "000":
        return

    # NOTE: Each county can occur only once
    if session.query(County).filter(County.code == data["code"][:-3]).count() > 0:
        return

    logging.debug("Adding %s" % data["name"])

    state_code = data["code"][:2]
    state = session.query(State).filter(State.code == state_code).one()

    county = County()
    county.code = data["code"][:-3]
    county.name = data["name"]
    county.state = state

    session.add(county)
    session.commit()


def addState(session, data):

    # NOTE: Each state can occur only once
    if session.query(State).filter(State.code == data["code"]).count() > 0:
        return

    logging.debug("Adding %s" % data["name"])

    state = State()
    state.code = data["code"]
    state.name = data["name"]

    session.add(state)
    session.commit()


def addDataset(session, data):
    logging.debug("Adding %s" % data["gemeindeschluessel"])

    county_code = data["gemeindeschluessel"]
    county = session.query(County).filter(County.code == county_code).one()

    state_code = data["bundesland"]
    state = session.query(State).filter(State.code == state_code).one()

    daten_stand = datetime.strptime(data["daten_stand"], "%Y-%m-%d %H:%M:%S")

    # NOTE: Only one entry per day, county and state
    if session.query(Dataset).filter(Dataset.state == state,
                                     Dataset.county == county,
                                     Dataset.daten_stand == daten_stand).count() > 0:
        return

    dataset = Dataset()

    dataset.county = county
    dataset.state = state

    # NOTE: These data result from state_code and county_code and should be added dynamically
    dataset.bundesland = state_code
    dataset.gemeindeschluessel = county_code

    dataset.anzahl_meldebereiche = data["anzahl_meldebereiche"]
    dataset.faelle_covid_aktuell = data["faelle_covid_aktuell"]
    dataset.faelle_covid_aktuell_invasiv_beatmet = data["faelle_covid_aktuell_invasiv_beatmet"]
    dataset.anzahl_standorte = data["anzahl_standorte"]
    dataset.betten_frei = data["betten_frei"]
    dataset.betten_belegt = data["betten_belegt"]
    dataset.daten_stand = daten_stand
    dataset.betten_belegt_nur_erwachsen = data["betten_belegt_nur_erwachsen"]
    dataset.betten_frei_nur_erwachsen = data["betten_frei_nur_erwachsen"]

    session.add(dataset)
    session.commit()


# NOTE: import states
with open(r"data/bundesland.csv") as fp:
    reader = csv.DictReader(fp)
    session = dbconnect()
    for line in reader:
        addState(session, line)

# NOTE: import urban counties
with open(r"data/gemeinden.csv") as fp:
    reader = csv.DictReader(fp)
    session = dbconnect()
    for line in reader:
        addMissingCounty(session, line)

# NOTE: import counties
with open(r"data/landkreise.csv") as fp:
    reader = csv.DictReader(fp)
    session = dbconnect()
    for line in reader:
        addCounty(session, line)

# NOTE: import data
for entry in os.scandir("data"):
    if entry.is_file and os.path.basename(entry.path).startswith("divi-intensivregister"):
        logging.debug("Importing %s" % entry.path)
        with open(entry.path) as fp:
            reader = csv.DictReader(fp)
            session = dbconnect()
            for line in reader:
                addDataset(session, line)
