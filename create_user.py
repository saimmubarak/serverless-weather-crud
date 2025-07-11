import boto3
import json
import uuid

dynamodb = boto3.resource(
    'dynamodb',
    region_name='eu-north-1'
)

table = dynamodb.Table('users')


def lambda_handler(event, context):
    # generating unique user ida
    user_id = str(uuid.uuid4())

    # recieving everything that is sent in post request
    print("Recieve event:", json.dumps(event))

    # load the json data into python
    body = json.loads(event["body"])
    # no error handling

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




    # adding id into data
    item = body.copy()
    item["id"] = user_id
    item["postal_code"] = postal_code
    item["city"] = city

    #remove location
    item.pop("location", None)

    # put item in DynamoDB
    table.put_item(Item=item)
    # no error handling

    return {
        'statusCode': 200,
        'body': json.dumps({'message': 'User Created locally locally' , 'user_id': user_id})
    }

