import boto3
import json


#todo improve convention

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('users')


def lambda_handler(event, context):
    body = json.loads(event["body"])
    user_id = body.get("id")
    name = body.get("name")

    # Using a loop to exclude id and name
    keys_to_exclude = ['id', 'name']
    expr_attr_values_pre = {}
    for key, value in body.items():
        if key not in keys_to_exclude:
            expr_attr_values_pre[key] = value

    # Adding : infront of every key name
    q__expr_attr_values = {}
    for key, value in expr_attr_values_pre.items():
        q__expr_attr_values[':' + key] = value

    # creating update_expr
    parts = []
    for key in expr_attr_values_pre.keys():
        parts.append(f"{key} = :{key}")
    q__update_expr = 'SET ' + ', '.join(parts)


    response = table.update_item(
        Key={
            "id": user_id,
            "name": name
        },
        UpdateExpression=q__update_expr,
        ExpressionAttributeValues=q__expr_attr_values,
        ReturnValues="ALL_NEW"
    )

    return {
        "statusCode": 200,
        "body": json.dumps({"message": "Update successful", "updated": response.get("Attributes")})
    }
