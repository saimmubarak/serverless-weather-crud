import boto3
import json
import requests



client = boto3.client("lambda")
dynamodb = boto3.resource('dynamodb')
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
    print(postal_code)
    city = item.get("city")
    print(city)

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

    print("Parsed response:", parsed_response)

    #storing response in weather dict
    if parsed_response.get("statusCode") == 200:
        weather_dict = json.loads(parsed_response["body"])
    else:
        weather_dict = None


    print(weather_dict)

    selected_weather = {
        "temp": weather_dict.get("temp_val"),
        "feelsLike": weather_dict.get("feelsLike_val"),
        "conditions": weather_dict.get("conditions"),
        "humidity": weather_dict.get("humidity_val"),
        "windspeed": weather_dict.get("pressure_val"),
        "pressure": weather_dict.get("pressure_val")
    }



    combined = {
        "resource": resource,
        "user": item,
        "weather": selected_weather
    }

    return {
        "statusCode": 200,
        "body": json.dumps(combined)
    }

if __name__ == "__main__":

    event = {
        "queryStringParameters": {
            "id": "60f3995c-d37b-4e85-b858-841ebeca435e",
            "name": "Abdullah"
        }
    }

    # Call the lambda handler function
    print(lambda_handler(event, None))




