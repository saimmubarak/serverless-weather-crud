import boto3
import json

# Connect to DynamoDB (adjust region if needed)
dynamodb = boto3.resource('dynamodb', region_name='eu-north-1')

# Reference your table
table = dynamodb.Table('users')

def lambda_handler(event, context):
    # Read from query string parameters (used in GET/DELETE requests)
    params = event.get("queryStringParameters")
    user_id = params.get("id")
    name = params.get("name")

    if not user_id or not name:
        return {
            "statusCode": 400,
            "body": json.dumps({"message": "id and name are required"})
        }

    # Attempt deletion
    response = table.delete_item(
        Key={
            "id": user_id,
            "name": name
        }
    )

    return {
        "statusCode": 200,
        "body": json.dumps({"message": "User deleted"})
    }

