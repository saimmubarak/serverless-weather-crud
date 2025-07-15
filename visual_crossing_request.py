import json
import requests
from datetime import date

API_Key = "S37C9TCD3UB38BKH6F7QDS466"
API_Key2 = "LKC7CSJNU53KN6SFMPN3QDDQF"

def get_weather_data_from_visual_crossing(postal_code, city):
    # Get today's date
    today = date.today()
    date1 = today.strftime("%Y-%m-%d")

    location1 = f"{postal_code},{city}"

    url = (
        f"https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/{location1}/{date1}?unitGroup=us&key={API_Key}&contentType=json"
    )
    url2 = (
        f"https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/{location1}/{date1}?unitGroup=us&key={API_Key2}&contentType=json"
    )
    response = requests.get(url)

    data = {}
    apiresponse = ""
    is_location_valid = True
    #todo update this condition for cases where out status code is something other that 200. If it is other that 200 then print the message (I think DONE)
    limit_reached = False
    if response.status_code == 200:
        data = response.json()
    elif response.status_code == 429:
        print("Request limit reached and alternative account will be used  ")
        if response.status_code == 200:
            response = requests.get(url2)
        elif response.status_code == 429:
            limit_reached = True
        else:
            print(f"Error {response.status_code}: {response.text}")
            limit_reached = True
    else:
        apiresponse = response.status_code
        print(f"Error {response.status_code}: {response.text}")



    #condition when location invalid
    if apiresponse == 400:
        print("Invalid Location")

    current = data.get("currentConditions", {})
    #learning .get() will automatically set the variable that is being get to None if it does not exist inside the dict used.


    print(is_location_valid)
    #todo fix the convention of object filtered DONE
    # Prepare the filtered dict DONE
    if apiresponse == 400:
        is_location_valid = False

    filtered = {
        "Is_location_valid": is_location_valid,
        "visual_crossing_limit_reached": limit_reached,
        "datetime_val": str(current.get("datetime")),
        "datetimeEpoch_val": str(current.get("datetimeEpoch")),
        "temp_val": str(current.get("temp")),
        "feelsLike_val": str(current.get("feelslike")),
        "conditions": current.get("conditions"),
        "humidity_val": str(current.get("humidity")),
        "windspeed_val": str(current.get("windspeed")),
        "pressure_val": str(current.get("pressure")),
    }

    return filtered

if __name__ == "__main__":
    print(get_weather_data_from_visual_crossing('0', 'N'))
