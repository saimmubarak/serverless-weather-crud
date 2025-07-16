import boto3
import json
import helper_functions as hf

# An object created to refer to client and table name
# Specifies dynamodb usage and the table used (table_name)
# specifies client that is used for invoke (lambda)
AwsInfo = hf.AwsResources(None, "users", None)


def lambda_handler(event, context):
    # Parse data sent in event according to type of data sent
    # json data in body
    # parameters
    params = hf.parse_data(event, context)

    #extract id and name from parameters
    user_id = params.get("id")
    name = params.get("name")

    #check if user_id and name have been sent
    if not user_id or not name:
        return {
            "statusCode": 400,
            "body": json.dumps({"message": "id and name are required"})
        }

    # Get item from DynamoDB
    # requires table_name(AwsInfo.table), primary_key -> user_id, sort_key -> user_name
    response = hf.delete_from_db(AwsInfo.table,user_id,name)

    #return a status code with indication that user deleted
    return {
        "statusCode": 200,
        "body": json.dumps({"message": "User deleted :)"})
    }

if __name__ == "__main__":

    event = {
        "queryStringParameters": {
            "id": "457744a3-d523-4029-80d3-52cc35306437",
            "name": "Samar"
        }
    }

    # Call the lambda handler function
    print(lambda_handler(event, None))
