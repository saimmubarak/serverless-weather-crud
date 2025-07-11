import json
import requests
from datetime import date

API_Key = "S37C9TCD3UB38BKH6F7QDS466"
API_Key2 = "LKC7CSJNU53KN6SFMPN3QDDQF"

def get_weather_data(postal_code, city):
    # Get today's date
    today = date.today()
    date1 = today.strftime("%Y-%m-%d")

    location1 = f"{postal_code},{city}"

    URL = (
        f"https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/{location1}/{date1}?unitGroup=us&key={API_Key}&contentType=json"
    )
    response = requests.get(URL)

    data = {}

    if response.status_code == 200:
        data = response.json()
    elif response.status_code == 429:
        print("Request limit reached and alternative account will be used  ")
        URL2 = (
            f"https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/{location1}/{date1}?unitGroup=us&key={API_Key2}&contentType=json"
        )
        response = requests.get(URL2)
    else:
        print("error")

    current = data.get("currentConditions", {})

    # Prepare the filtered dict
    filtered = {
        "datetime_val": str(current.get("datetime")) if current.get("datetime") is not None else None,
        "datetimeEpoch_val": str(current.get("datetimeEpoch")) if current.get("datetime") is not None else None,
        "temp_val": str(current.get("temp")) if current.get("temp") is not None else None,
        "feelsLike_val": str(current.get("feelslike")) if current.get("feelslike") is not None else None,
        "conditions": current.get("conditions"),
        "humidity_val": str(current.get("humidity")) if current.get("humidity") is not None else None,
        "windspeed_val": str(current.get("windspeed")) if current.get("windspeed") is not None else None,
        "pressure_val": str(current.get("pressure")) if current.get("pressure") is not None else None,
    }

    return filtered

if __name__ == "__main__":
    print(get_weather_data('07008', 'New York'))
