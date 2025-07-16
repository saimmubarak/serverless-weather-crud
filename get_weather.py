# get_weather Lambda
import json
import boto3
import visual_crossing_request as vc
import helper_functions as hf


#An object created to refer to client and table name
#Specifies dynamodb usage and the table used (table_name)
#specifies client that is used for invoke (lambda)
AwsInfo = hf.AwsResources("lambda", "weather", None)


def lambda_handler(event, context):

    #extract postal code from payload
    postal_code = event.get("postal_code")
    city = event.get("city")


    # Get item from DynamoDB
    # specify the partition and sort keys of Database and their values
    key = {
        "postal_code": postal_code,
        "city": city
    }

    # requires table_name(AwsInfo.table), key_dit (key)
    response = hf.read_from_db(AwsInfo.table, key)

    #initialize variables that will be used in the if statements
    resource = ""
    db_date_time = ""
    vc_limit_reached = False
    is_location_valid = False
    expression_attribute_values = {}
    expression_attribute_names = {}
    parts = []

    if "Item" not in response:
        # todo if your vc limit is over give user the data currenly available in db. DONE
        #print("It was not in the database")

        #receive weather data dict from visual_crossing and process it
        cleaned_item = hf.get_and_handle_data_from_visual_crossing(postal_code, city)

        resource = "Got Data From Visual Crossing"

        #extracting location_valid boolean from dict
        is_location_valid = cleaned_item.get("Is_location_valid")

        if is_location_valid:
            #entered location is valid

            # extracting visual_crossing_limit_reached boolean from dict
            vc_limit_reached = cleaned_item.get("visual_crossing_limit_reached")

            if vc_limit_reached:
                print("Weather Data Not Available")


            # Updating the weather db
            for key, value in cleaned_item.items():
                if key not in ("postal_code", "city"):
                    attr_name_placeholder = f"#{key}"
                    expression_attribute_names[attr_name_placeholder] = key
                    expression_attribute_values[f":{key}"] = value
                    parts.append(f"{attr_name_placeholder} = :{key}")

            update_expr = "SET " + ", ".join(parts)

            # update database function
            key = {
                "postal_code": postal_code,
                "city": city
            }
            # requires table_name(AwsInfo.table), key_dit (key)
            hf.update_db(AwsInfo.table, key, update_expr, expression_attribute_names,
                                    expression_attribute_values)

        else:
            return {
                "resource": resource,
                "statusCode": 200,
                "body": json.dumps(cleaned_item),
                "Is_Location_valid": is_location_valid,
                "message": "Your entered location was not valid"
            }

    else:
        # .................
        print("It was in the database")
        resource = "Got Data From DynamoDB"
        item = response.get("Item")
        cleaned_item = hf.clean_decimals(item)

        is_location_valid = True

        #make a temp value for db data
        temp_cleaned_item = cleaned_item

        db_date_time = cleaned_item.get("datetimeEpoch_val")

        print("database_time", db_date_time)

        if db_date_time:
            # -------------------------------------------------------------------------
            passed_time = hf.time_difference(db_date_time)
            # --------------------------------------------------------------------------

            print("passed_time",passed_time)

            if passed_time >= 21600:
                print("It was in the database but the record was too old")

                # receive weather data dict from visual_crossing and process it
                visual_crossing_item = hf.get_and_handle_data_from_visual_crossing(postal_code, city)

                # extracting visual_crossing_limit_reached boolean from dict
                vc_limit_reached = visual_crossing_item.get("visual_crossing_limit_reached")

                if vc_limit_reached:
                    resource = "Got Data From DynamoDB"
                    cleaned_item = temp_cleaned_item
                else:
                    resource = "Got Data From Visual Crossing"
                    cleaned_item = visual_crossing_item

                    for key, value in cleaned_item.items():
                        if key not in ("postal_code", "city"):
                            attr_name_placeholder = f"#{key}"
                            expression_attribute_names[attr_name_placeholder] = key
                            expression_attribute_values[f":{key}"] = value
                            parts.append(f"{attr_name_placeholder} = :{key}")

                    update_expr = "SET " + ", ".join(parts)

                    # update database function
                    key = {
                        "postal_code": postal_code,
                        "city": city
                    }
                    # requires table_name(AwsInfo.table), key_dit (key)
                    response = hf.update_db(AwsInfo.table, key, update_expr, expression_attribute_names,
                                            expression_attribute_values)



    cleaned_item.pop("visual_crossing_limit_reached", None)

    #cleaned_item = hf.clean_decimals(cleaned_item)

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
