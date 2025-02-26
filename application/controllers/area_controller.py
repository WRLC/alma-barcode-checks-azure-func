"""
Controllers for area model.
"""
from sqlalchemy import select
from sqlalchemy.orm import Session
from application.extensions import engine
from application.models.area_sql import Area


def get_area_by_name(name: str) -> Area:
    """
    Get area from database by name.

    :param name: Area name
    :return: Area object
    """
    session = Session(engine)  # Create a Session object

    stmt = select(Area).where(Area.name == name)  # Select the area from the database
    area = session.scalars(stmt).one()  # Execute the statement and get the result

    return area
