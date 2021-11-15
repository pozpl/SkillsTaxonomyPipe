import datetime

from sqlalchemy import create_engine, Column, Table, ForeignKey, UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import (Integer, SmallInteger, String, Date, DateTime, Float, Boolean, Text, LargeBinary, DateTime)
from sqlalchemy.orm import relationship

from utils import common_parameters

DeclarativeBase = declarative_base()


def db_connect():
    """
    Performs database connection using database settings from settings.py.
    Returns sqlalchemy engine instance
    """
    db_con_str = common_parameters()['db']['jobs']['connection_string']
    print('Connecting to ' + db_con_str)
    return create_engine(db_con_str)


def create_table(engine):
    DeclarativeBase.metadata.create_all(engine)


class Category(DeclarativeBase):
    __tablename__ = 'category'
    id = Column(Integer, primary_key=True)
    title = Column('title', Text(), unique=True)

    __table_args__ = (UniqueConstraint('title', name='_category_title_uc'),)


class SubCategory(DeclarativeBase):
    __tablename__ = 'sub_category'
    id = Column(Integer, primary_key=True)
    title = Column('title', Text())
    category_id = Column(Integer, ForeignKey('category.id', ondelete="CASCADE"))
    category = relationship(Category)

    __table_args__ = (UniqueConstraint('category_id', 'title', name='_category_sub_category_title_uc'),)


class Country(DeclarativeBase):
    __tablename__ = 'country'

    id = Column(Integer, primary_key=True)
    title = Column('title', Text(), unique=True)


class State(DeclarativeBase):
    __tablename__ = 'state'

    id = Column(Integer, primary_key=True)
    title = Column('title', Text())
    country_id = Column(Integer, ForeignKey('country.id', ondelete="CASCADE"))
    country = relationship(Country)

    __table_args__ = (UniqueConstraint('country_id', 'title', name='_country_state_uc'),)


class City(DeclarativeBase):
    __tablename__ = 'city'

    id = Column(Integer, primary_key=True)
    title = Column('title', Text())
    state_id = Column(Integer, ForeignKey('state.id', ondelete="CASCADE"))
    state = relationship(State)

    __table_args__ = (UniqueConstraint('state_id', 'title', name='_state_city_uc'),)


class Skill(DeclarativeBase):
    __tablename__ = 'skill'
    id = Column(Integer, primary_key=True)
    title = Column('title', Text(), unique=True)


class Vacancy(DeclarativeBase):
    __tablename__ = 'vacancy'

    id = Column(Integer, primary_key=True)
    title = Column('title', Text())
    description = Column('description', Text(), nullable=False)
    created_date = Column(DateTime, default=datetime.datetime.utcnow)
    uid = Column('uid', Integer, nullable=False, unique=True)
    roleTitles = ('role_titles', Text())
    listingDate = Column(DateTime)
    sub_category_id = Column(Integer, ForeignKey('sub_category.id', ondelete="CASCADE"))
    sub_category = relationship(SubCategory)

    country = relationship(Country, secondary='vacancy_country')
    city = relationship(City, secondary='vacancy_city')
    skills = relationship(Skill, secondary='vacacny_skill')

    __table_args__ = (UniqueConstraint('uid', name='_uid_uc'),)


class VacancyCountryAssociationTable(DeclarativeBase):
    __tablename__ = 'vacancy_country'
    vacancy_id = Column(Integer, ForeignKey('vacancy.id'), primary_key=True)
    country_id = Column(Integer, ForeignKey('country.id'), primary_key=True)


class VacancyCityAssociationTable(DeclarativeBase):
    __tablename__ = 'vacancy_city'
    vacancy_id = Column(Integer, ForeignKey('vacancy.id'), primary_key=True)
    city_id = Column(Integer, ForeignKey('city.id'), primary_key=True)

class VacacnySkillAssociationTable(DeclarativeBase):
    __tablename__='vacancy_skill'
    vacancy_id=Column(Integer, ForeignKey('vacancy.id'), primary_key=True)
    skill_id=Column(Integer, ForeignKey('skill.id'), primary_key=True)
                              