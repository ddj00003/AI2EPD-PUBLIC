from datetime import datetime

import pytz
from pymongo import MongoClient

def get_db_handle(db_name, host, port, username, password, auth_source):
    """
    Returns a MongoDB client object to interact with a specific database.

    Args:
    - db_name (str): Name of the database to connect to.
    - host (str): IP address or hostname of the MongoDB server.
    - port (int): Port number of the MongoDB server.
    - username (str): User name for authentication on the MongoDB server.
    - password (str): Password for authentication on the MongoDB server.
    - auth_source (str): Name of the database to be used for authentication.

    Returns:
    - A tuple of two elements containing a MongoDB client object and a database object.

    Raises:
    - ValueError: If any of the required arguments is None or an empty string.
    - pymongo.errors.OperationFailure: If authentication fails.
    - pymongo.errors.ConnectionFailure: If the connection to the server fails.
    """

    client = MongoClient(
        host=host,
        port=int(port),
        username=username,
        password=password,
        authSource=auth_source,
    )
    return client[db_name], client

def timestamp_now():
    """
    Get the current time with the timezone Europe/Madrid.
    """
    _utc_timezone = pytz.timezone("UTC")
    _new_timezone = pytz.timezone("Europe/Madrid")

    # Get an 'offset-aware' datetime.
    _utc_datetime = datetime.utcnow()
    _my_datetime = _utc_timezone.localize(_utc_datetime)

    # Convert datetime in the new timezone.
    _date_in_timezone_str = _my_datetime.astimezone(_new_timezone).strftime("%d-%m-%Y %H:%M:%S.%f")
    return datetime.strptime(_date_in_timezone_str, "%d-%m-%Y %H:%M:%S.%f").timestamp()

def date_utc(timestamp, format):
    """
    Get the date from timestamp with the timezone Europe/Madrid.
    """
    _utc_timezone = pytz.timezone("UTC")
    _new_timezone = pytz.timezone("Europe/Madrid")

    # Get an 'offset-aware' datetime.
    _utc_datetime = datetime.fromtimestamp(timestamp)
    _my_datetime = _utc_timezone.localize(_utc_datetime)

    # Convert datetime in the new timezone.
    _date_in_timezone_str = _my_datetime.astimezone(_new_timezone).strftime(format)
    return _date_in_timezone_str

def get_datetime_utc_now():
    """
    Get the current time with the timezone Europe/Madrid.
    """
    _utc_timezone = pytz.timezone("UTC")
    _new_timezone = pytz.timezone("Europe/Madrid")

    # Get an 'offset-aware' datetime.
    _utc_datetime = datetime.utcnow()
    _my_datetime = _utc_timezone.localize(_utc_datetime)

    # Convert datetime in the new timezone.
    _date_in_timezone_str = _my_datetime.astimezone(_new_timezone).strftime("%d-%m-%Y %H:%M:%S.%f")
    return datetime.strptime(_date_in_timezone_str, "%d-%m-%Y %H:%M:%S.%f")
