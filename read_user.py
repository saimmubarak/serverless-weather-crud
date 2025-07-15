import boto3
import json
import requests

#todo improve convention

#Tell boto3 what db you want to refer to
client = boto3.client("lambda")
dynamodb = boto3.resource('dynamodb')

#specify the db table
table = dynamodb.Table('users')

def lambda_handler(event, context):

    # Read from query string parameters (used in GET requests)
    params = event.get("queryStringParameters")
    user_id = params.get("id")
    name = params.get("name")

    if not user_id or not name:
        return {
            "statusCode": 400,
            "body": json.dumps({"message": "id and name are required"})
        }


    # Get item from DynamoDB
    response = table.get_item(
        Key={
            "id": user_id,
            "name": name
        }
    )

    item = response.get("Item")
    if not item:
        return {
            "statusCode": 404,
            "body": json.dumps({"message": "User not found"})
        }

    # get_postal_code and city
    postal_code = item.get("postal_code")
    city = item.get("city")
    image_url = item.get("image_url")

    # invoke get_weather()
    payload = {
        "postal_code": postal_code,
        "city": city
    }
    # Invoke (get_weather)
    response = client.invoke(
        FunctionName="serverless-crud-dev-getWeather",
        InvocationType="RequestResponse",
        Payload=json.dumps(payload)
    )
    response_payload = response["Payload"].read().decode("utf-8")
    parsed_response = json.loads(response_payload)

    resource = parsed_response.get("resource")
    is_location_valid = parsed_response.get("Is_Location_valid")


    # invoke open_profile_pic()
    payload = {
        "url": image_url
    }
    # Invoke (get_weather)
    response = client.invoke(
        FunctionName="serverless-crud-dev-getWeather",
        InvocationType="RequestResponse",
        Payload=json.dumps(payload)
    )
    response_payload = response["Payload"].read().decode("utf-8")
    parsed_response = json.loads(response_payload)


    if is_location_valid:
        #location is valid
        # storing response in weather dict
        if parsed_response.get("statusCode") == 200:
            weather_dict = json.loads(parsed_response["body"])
        else:
            weather_dict = None

        selected_weather = {
            "temp": weather_dict.get("temp_val"),
            "feelsLike": weather_dict.get("feelsLike_val"),
            "conditions": weather_dict.get("conditions"),
            "humidity": weather_dict.get("humidity_val"),
            "windspeed": weather_dict.get("pressure_val"),
            "pressure": weather_dict.get("pressure_val")
        }

        if image_url:
            combined = {
                "user": item,
                "weather": selected_weather,
                "profile_pic": image_url
            }
        else:
            combined = {
                "user": item,
                "weather": selected_weather
            }
    else:
        #location is not valid
        if image_url:
            combined = {
                "resource": resource,
                "user": item,
                "profile_pic": image_url,
                "location_error": "Unable to get weather data of your location"
            }
        else:
            combined = {
                "resource": resource,
                "user": item,
                "location_error": "Unable to get weather data of your location"
            }



    return {
        "statusCode": 200,
        "body": json.dumps(combined)
    }

if __name__ == "__main__":

    #4e60f549-76ca-4b75-ba27-ff3125575491
    #ali
    #c3b4f53f-7375-4709-a6f5-2e779c821efb
    #Samar

    event = {
        "queryStringParameters": {
            "id": "7d4ffa2d-fec7-404a-b030-91565d60842e",
            "name": "wajhee"
        }
    }

    # Call the lambda handler function
    print(lambda_handler(event, None))




