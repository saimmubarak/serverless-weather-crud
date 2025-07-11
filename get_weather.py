# get_weather Lambda
import json
import boto3
import visual_crossing_request as vc
import helper_functions as hf


# invoking another lambda
client = boto3.client("lambda")

#connection with db
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('weather')



def lambda_handler(event, context):
    postal_code = event.get("postal_code")
    city = event.get("city")

    # print("postal_code:", postal_code)
    # print("city:", city)

    # payload = {
    #     "postal_code": postal_code,
    #     "city": city
    # }
    #
    # # Invoke Lambda C
    # response = client.invoke(
    #     FunctionName="serverless-crud-dev-getExistingWeather",
    #     InvocationType="RequestResponse",
    #     Payload=json.dumps(payload)
    # )
    # response_payload = response["Payload"].read().decode("utf-8")
    # parsed_response = json.loads(response_payload)
    #
    # #print(parsed_response)
    #
    # if "errorMessage" in parsed_response:
    #     raise Exception(f"Invoked Lambda failed: {parsed_response['errorMessage']}")


    #..................
    # Get item
    response = table.get_item(
        Key={
            "postal_code": postal_code,
            "city": city
        }
    )

    resource = ""
    db_date_time = ""
    if "Item" in response:
        print("It was in the database")
        resource = "Got Data From DynamoDB"
        item = response.get("Item")
        cleaned_item = hf.clean_decimals(item)
        db_date_time1 = cleaned_item.get("datetime_val")
        db_date_time = cleaned_item.get("datetimeEpoch_val")
        if db_date_time:
            #-------------------------------------------------------------------------
            passed_time = hf.time_difference(db_date_time)
            #--------------------------------------------------------------------------

            #resource = parsed_response.get("resource")
            print(passed_time)
            if passed_time >= 10800:
                print("It was in the database but the record was too old")
                cleaned_item = vc.get_weather_data(postal_code, city)
                resource = "Got Data From Visual Crossing"
    else:
        print("It was not in the database")
        cleaned_item = vc.get_weather_data(postal_code, city)
        resource = "Got Data From Visual Crossing"

        cleaned_item = hf.clean_decimals(cleaned_item)

        # Updating the weather db
        expression_attribute_values = {}
        expression_attribute_names = {}
        parts = []

        for key, value in cleaned_item.items():
            if key not in ("postal_code", "city"):
                attr_name_placeholder = f"#{key}"
                expression_attribute_names[attr_name_placeholder] = key
                expression_attribute_values[f":{key}"] = value
                parts.append(f"{attr_name_placeholder} = :{key}")

        update_expr = "SET " + ", ".join(parts)

        response = table.update_item(
            Key={
                "postal_code": postal_code,
                "city": city
            },
            UpdateExpression=update_expr,
            ExpressionAttributeNames=expression_attribute_names,
            ExpressionAttributeValues=expression_attribute_values,
            ReturnValues="ALL_NEW"
        )







    return {
        "resource": resource,
        "statusCode": 200,
        "body": json.dumps(cleaned_item)
    }

if __name__ == "__main__":
    test_event = {
        "postal_code": "07008",
        "city": "New York"
    }
    print(lambda_handler(test_event, None))

