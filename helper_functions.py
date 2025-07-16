import time
from decimal import Decimal
import boto3
import visual_crossing_request as vc
import json


#get data from visual_crossing and get process it (convert to float value)
def get_and_handle_data_from_visual_crossing(postal_code, city):
    # receive weather data dict from visual_crossing and process it
    cleaned_item = vc.get_weather_data_from_visual_crossing(postal_code, city)
    cleaned_item = clean_decimals(cleaned_item)

    return cleaned_item

# Class definition
#todo change name DONE///
class AwsResources:
    def __init__(self, client_name = None, table_name = None, bucket_name = None):

        if client_name:
            self.client = boto3.client(client_name)
        if table_name:
            self.dynamodb = boto3.resource('dynamodb')
            self.table = self.dynamodb.Table(table_name)
        if bucket_name:
            self.s3_bucket = bucket_name
            self.s3 = boto3.client('s3')


#todo make this method dynamic (work for any table that is given in input) DONE////
#todo pep8 standards

#functions for simple database calls

#1 Put data in database
def put_to_db(table_name, item_dict):
    response = table_name.put_item(Item=item_dict)
    return response

#2 delete from database against id and name
def delete_from_db(table_name, user_id, user_name):
    response = table_name.delete_item(
        Key={
            "id": user_id,
            "name": user_name
        }
    )
    return response

#3 read from database against partition key and sort key
def read_from_db(table_name,table_key):
    response = table_name.get_item(Key=table_key)
    return response

#3 update database against partition key and sort key
def update_db(table_name, table_key, update_expr, expression_attribute_names, expression_attribute_values):
    response = table_name.update_item(
        Key=table_key,
        UpdateExpression=update_expr,
        ExpressionAttributeNames=expression_attribute_names,
        ExpressionAttributeValues=expression_attribute_values,
        ReturnValues="ALL_NEW")
    return response

#todo change name to awslambda invoke
#invoke some lambda
def aws_lambda_invoke(func_name,invo_type,payload,client):
    # Invoke (get_weather)
    response = client.invoke(
        FunctionName=func_name,

        InvocationType=invo_type,
        Payload=json.dumps(payload)
    )
    response_payload = response["Payload"].read().decode("utf-8")
    parsed_response = json.loads(response_payload)

    return parsed_response



#function parse data based on type of data either body or "queryStringParameters"
def parse_data(event,context):
    params = event.get("queryStringParameters")
    if params:
        #data sent as parameters probably a get request
        return params
    if "body" in event and event["body"]:
        body = json.loads(event["body"])
        return body

    return{
        "statusCode": 400
    }



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

    if not db_date_time:
        return 12000

    # Convert string to integer
    epoch_timestamp = int(db_date_time)

    # Get current time as epoch timestamp
    current_epoch = int(time.time())

    passed_time = current_epoch - epoch_timestamp


    return passed_time


#-----------
#check if location value received in get request
#split location input into postal_code and city
def check_and_handle_location(body):
    # a check to verify if location was sent in post request otherwise error produced
    location = body.get("location")
    if not location:
        return {
            'statusCode': 400,
            'body': json.dumps({'message': 'location is required in format postal_code,city'})
        }
    # Split location into postal_code and city
    postal_code, city = location.split(",")
    postal_code = postal_code.strip()
    city = city.strip()

    return {"postal_code":postal_code,
            "city":city}


if __name__ == "__main__":
    print(time_difference(None))