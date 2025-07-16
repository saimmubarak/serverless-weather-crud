import boto3
import json
import helper_functions as hf


#An object created to refer to client and table name
#Specifies dynamodb usage and the table used (table_name)
#specifies client that is used for invoke (lambda)
AwsInfo = hf.AwsResources(None, "users", None)


def lambda_handler(event, context):

    # Parse data sent in event according to type of data sent
    # json data in body
    # parameters
    body = hf.parse_data(event, context)

    #extract userid and name from params
    user_id = body.get("id")
    name = body.get("name")
    # Exclude id and name
    keys_to_exclude = {'id', 'name'}

    # Build the expressions
    expression_attribute_values = {}
    expression_attribute_names = {}
    update_parts = []

    for key, value in body.items():
        if key not in keys_to_exclude:
            placeholder_name = f"#{key}"
            placeholder_value = f":{key}"

            # Build the parts
            expression_attribute_names[placeholder_name] = key
            expression_attribute_values[placeholder_value] = value
            update_parts.append(f"{placeholder_name} = {placeholder_value}")

    # Join parts into SET expression
    update_expression = "SET " + ", ".join(update_parts)

    print("Sending update to DynamoDB...")

    # Key dictionary
    key = {
        "id": user_id,
        "name": name
    }

    # Update database
    response = hf.update_db(
        AwsInfo.table,
        key,
        update_expression,
        expression_attribute_names,
        expression_attribute_values
    )

    print("Update response:", response)

    return {
        "statusCode": 200,
        "body": json.dumps({"message": "Update successful", "updated": response.get("Attributes")})
    }

if __name__ == "__main__":
    # This simulates an API Gateway event sending JSON
    event = {
        "headers": {
            "Content-Type": "application/json"
        },
        "body": json.dumps({
            "id": "1f7acab2-e199-4648-9a59-523d0ebda5b1",
            "name": "saim",
            "email": "saim@example.com",
            "bloodtype": "A",
            "age":"22"
        })
    }

    context = None

    # Call the Lambda handler
    print(lambda_handler(event, context))

