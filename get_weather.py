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

    print("postal_code:", postal_code)
    print("city:", city)


    # Get item
    response = table.get_item(
        Key={
            "postal_code": postal_code,
            "city": city
        }
    )

    resource = ""
    db_date_time = ""
    vc_limit_reached = False
    is_location_valid = False
    if "Item" not in response:
        # todo if your vc limit is over give user the data currenly available in db. DONE
        print("It was not in the database")
        cleaned_item = vc.get_weather_data_from_visual_crossing(postal_code, city)
        resource = "Got Data From Visual Crossing"

        is_location_valid = cleaned_item.get("Is_location_valid")

        if is_location_valid:
            print("Location is valid")
            #entered location is valid
            vc_limit_reached = cleaned_item.get("visual_crossing_limit_reached")
            if vc_limit_reached:
                print("Weather Data Not Available")


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
        else:
            return {
                "resource": resource,
                "statusCode": 200,
                "body": json.dumps(cleaned_item),
                "Is_Location_valid": is_location_valid
            }

    else:
        # .................
        print("It was in the database")
        resource = "Got Data From DynamoDB"
        item = response.get("Item")
        cleaned_item = hf.clean_decimals(item)
        db_date_time1 = cleaned_item.get("datetime_val")
        db_date_time = cleaned_item.get("datetimeEpoch_val")

        if db_date_time:
            # -------------------------------------------------------------------------
            passed_time = hf.time_difference(db_date_time)
            # --------------------------------------------------------------------------



            if passed_time >= 21600:
                print("It was in the database but the record was too old")
                visual_crossing_item = vc.get_weather_data_from_visual_crossing(postal_code, city)
                vc_limit_reached = visual_crossing_item.get("visual_crossing_limit_reached")
                if vc_limit_reached:
                    print("Resent weather record could not be found")
                else:
                    resource = "Got Data From Visual Crossing"
                    cleaned_item = visual_crossing_item


    cleaned_item.pop("visual_crossing_limit_reached", None)
    return {
        "resource": resource,
        "statusCode": 200,
        "body": json.dumps(cleaned_item),
        "Is_Location_valid": is_location_valid
    }

if __name__ == "__main__":
    test_event = {
        "postal_code": "90004",
        "city": "Los Angeles",
    }
    print(lambda_handler(test_event, None))

