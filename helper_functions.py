import time
from decimal import Decimal

def clean_decimals(obj):
    if isinstance(obj, list):
        return [clean_decimals(i) for i in obj]
    elif isinstance(obj, dict):
        return {k: clean_decimals(v) for k, v in obj.items()}
    elif isinstance(obj, Decimal):
        return float(obj)
    else:
        return obj

def time_difference(db_date_time):
    # Convert string to integer
    epoch_timestamp = int(db_date_time)

    # Get current time as epoch timestamp
    current_epoch = int(time.time())

    # Check if timestamp is in milliseconds (more than 10 digits)
    if len(db_date_time) > 10:
        # Convert milliseconds to seconds
        past_epoch = epoch_timestamp // 1000
    else:
        # Already in seconds
        past_epoch = epoch_timestamp

    # Calculate difference in seconds
    passed_time = current_epoch - past_epoch
    return passed_time