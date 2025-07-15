import time
from decimal import Decimal


#todo make sure you understand what you write Done :)
def clean_decimals(obj):

    # given a decimal value convert if to float
    if isinstance(obj, Decimal):
        return float(obj)

    # given a list recursively call each element of list to clean_decimals then make a fresh list.
    if isinstance(obj, list):
        cleaned_list = []
        for item in obj:
            cleaned_item = clean_decimals(item)
            cleaned_list.append(cleaned_item)
        return cleaned_list

    # given a dict recursively call each key_value_pair of list to clean_decimals then make a fresh list.
    if isinstance(obj, dict):
        cleaned_dict = {}
        for key, value in obj.items():
            cleaned_value = clean_decimals(value)
            cleaned_dict[key] = cleaned_value
        return cleaned_dict

    #return your cleaned dict
    return obj

#   File "C:\serverless\get_weather.py", line 97, in lambda_handler
#     passed_time = hf.time_difference(db_date_time)
#   File "C:\serverless\helper_functions.py", line 35, in time_difference
#     database_time = int(weather_time_received_from_db)
# ValueError: invalid literal for int() with base 10: 'None'

def time_difference(weather_time_received_from_db):

    #convert time received from database to int
    database_time = int(weather_time_received_from_db)


    #get the time_epoch value for your zone
    current_epoch_time = int(time.time())

    #subtract to find time difference
    passed_time = int(current_epoch_time - database_time)

    #return your time difference (int)
    return passed_time


if __name__ == "__main__":
    print(time_difference("990021"))