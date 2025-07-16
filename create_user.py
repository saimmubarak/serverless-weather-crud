import boto3
import json
import uuid
import base64
from requests_toolbelt.multipart import decoder
import helper_functions as hf


# An object created to refer to client and table name
# Specifies dynamodb usage and the table used (table_name)
# Specifies client that is used for invoke (lambda)
AwsInfo = hf.AwsResources('s3', "users", "profilepicusers")


def lambda_handler(event, context):

    # Generating unique user id using uuid library
    user_id = str(uuid.uuid4())

    # Initialize variables used in code
    item = {}
    image_url = None
    location = None

    # To Handle both application/json type and form data we must get content type that is in headers{}
    headers =event.get('headers',{})

    # Convert uppercase letters to lowers case to avoid errors
    headers_normalized = {}
    for k, v in headers.items():
        lower_key = k.lower()
        headers_normalized[lower_key] = v

    # Content type info is placed in content_type within header that we normalized by converting to lowercase
    content_type = headers_normalized.get("content-type", "")


    # Deal with the payload according to content_type
    if "application/json" in content_type:
        # Place code to deal with application/json

        # Load the json data into python
        # Gets the string value stored under the "body" key in the event dictionary
        body = hf.parse_data(event, context)

        # Produce an error message if location isn't entered
        location = body.get("location")
        if not location:
            return {
                'statusCode': 400,
                'body': json.dumps({'message': 'location is required in format postal_code,city'})
            }


        # Adding id into data
        item = body.copy()

        # Remove location
        item.pop("location", None)


    elif "multipart/form-data" in content_type:
        # Place code to deal with multipart/form-data

        # In multipart/form-data out data in base64 encoded
        # Decode Base64
        body_bytes = base64.b64decode(event["body"])

        # Our multipart body is split into individual parts with each part representing a text/file field
        # Parse multipart
        multipart_data = decoder.MultipartDecoder(body_bytes, content_type)
        # We will later loop over multipart_data.parts to process each key value pair

        # Loop through multipart_data and record the key value pairs
        for i in multipart_data.parts:
            cd = i.headers[b"Content-Disposition"].decode() #I dont understand this code

            # Extract field name
            field_name = None
            fieldname_split = cd.split('name="')
            if len(fieldname_split) > 1:
                rest = fieldname_split[1]
                field_name = rest.split('"')[0]

            if not field_name:
                continue

            # Image file handling
            if field_name == "image":
                filename = None
                filename_split = cd.split('filename="')
                if len(filename_split) > 1:
                    rest = filename_split[1]
                    filename = rest.split('"')[0]

                content_type_part = i.headers[b"Content-Type"].decode()
                file_bytes = i.content
                s3_key = f"users/{user_id}/{filename}"

                #put image in s3
                AwsInfo.s3.put_object(
                    Bucket=AwsInfo.s3_bucket,
                    Key=s3_key,
                    Body=file_bytes,
                    ContentType=content_type_part
                )


                image_url = f"https://{AwsInfo.s3_bucket}.s3.amazonaws.com/{s3_key}"

            # Location needs separate handling
            elif field_name == "location":
                location = i.text

            # All other text fields (generic handling)
            else:
                item[field_name] = i.text

    else:
        return {
            'statusCode': 400,
            'body': json.dumps({'message': 'Unsupported Content-Type'})
        }


    if not location:
        return {
            'statusCode': 400,
            'body': json.dumps({'message': 'location is required in format postal_code,city'})
        }

    #placing url in body
    if image_url:
        item["image_url"] = image_url


    # Split location into postal_code and city
    postal_code, city = location.split(",")
    postal_code = postal_code.strip()
    city = city.strip()

    # adding id into data
    #item = body.copy()
    item["id"] = user_id
    item["postal_code"] = postal_code
    item["city"] = city

    # either application/json or multipart/form-data you have to place data in db
    # put item in DynamoDB
    #specify name of table (AwsInfo.table)
    #Dict to be placed on db (item)
    hf.put_to_db(AwsInfo.table, item)


    return {
        'statusCode': 200,
        'body': json.dumps({'message': 'User Created' , 'user_id': user_id})
    }

if __name__ == "__main__":
    # This simulates an API Gateway event sending JSON
    event = {
        "headers": {
            "Content-Type": "application/json"
        },
        "body": json.dumps({
            "name": "Samar",
            "email": "samar@example.com",
            "location": "12345,Lahore"
        })
    }

    context = None

    # Call the Lambda handler
    response = lambda_handler(event, context)

    # Print the result
    print("Response:")
    print(json.dumps(response, indent=2))