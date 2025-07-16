import boto3
import json
import requests
import helper_functions as hf

#todo improve convention


#An object created to refer to client and table name
#Specifies dynamodb usage and the table used (table_name)
#specifies client that is used for invoke (lambda)
AwsInfo = hf.AwsResources("lambda", "users", None)

def lambda_handler(event, context):

    # Read from query string parameters (used in GET requests)
    params = hf.parse_data(event, context)

    #extract name and id from params
    user_id = params.get("id")
    name = params.get("name")

    #error message if id and name not sent
    if not user_id or not name:
        return {
            "statusCode": 400,
            "body": json.dumps({"message": "id and name are required"})
        }


    # Get item from DynamoDB
    # specify the partition and sort keys of Database and their values
    key = {
        "id": user_id,
        "name": name
        }
    # requires table_name(AwsInfo.table), key_dit (key)
    response = hf.read_from_db(AwsInfo.table, key)

    item = response.get("Item")
    if not item:
        return {
            "statusCode": 404,
            "body": json.dumps({"message": "User not found"})
        }

    # get postal_code, city, and image_url
    postal_code = item.get("postal_code")
    city = item.get("city")
    image_url = item.get("image_url")



    # We will get weather data for the user from either visual_crossing or dynamodb
    # Invoke get_weather() "a lambda that handles getting weather data"

    # Getweather requires a payload with postal_code and city
    payload = {
        "postal_code": postal_code,
        "city": city
    }
    # The function aws_lambda_invoke invokes the lambda specified
    # The function requires Function_Name, Invocation_Type, Payload, s3 Client
    # The function return a dictionary containing weather data or error message
    weatherdata= hf.aws_lambda_invoke("serverless-crud-dev-getWeather","RequestResponse",payload,AwsInfo.client)

    print("weather_data",weatherdata)

    # Extract resource string that specifies where the data comes from Visual Crossing or DynamoDB
    resource = weatherdata.get("resource")



    # Extract is_location_valid boolean that specifies is the location provided by user exists or not
    is_location_valid = weatherdata.get("Is_Location_valid")

    # A check for valid location
    if is_location_valid:
        #location is valid

        # storing response in weather dict
        if weatherdata.get("statusCode") == 200:
            weather_dict = json.loads(weatherdata["body"])

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

    event = {
        "queryStringParameters": {
            "id": "473a072e-80c8-48d7-a598-b16df6ec8568",
            "name": "fahad"
        }
    }

    # Call the lambda handler function
    print(lambda_handler(event, None))



