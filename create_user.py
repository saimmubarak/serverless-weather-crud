import boto3
import json
import uuid
import base64
from requests_toolbelt.multipart import decoder

#Tell boto3 what db you want to refer to
dynamodb = boto3.resource(
    'dynamodb',
    region_name='eu-north-1'
)

#specify the db table
table = dynamodb.Table('users')

#s3 butcket
s3 = boto3.client('s3')
s3_bucket = "profilepicusers"


def lambda_handler(event, context):
    # generating unique user ida
    user_id = str(uuid.uuid4())

    # Initialize dict and url
    item = {}
    image_url = None
    location = None

    #get the content type sent in post request
    headers =event.get('headers',{})
    #convert uppercase letters to lowers case to avoid errors
    headers_normalized = {}
    for k, v in headers.items():
        lower_key = k.lower()
        headers_normalized[lower_key] = v

    #content type info is placed in content_type
    content_type = headers_normalized.get("content-type", "")

    #deal with the payload according to content_type
    if "application/json" in content_type:
        #place code to deal with application/json

        # load the json data into python
        # gets the string value stored under the "body" key in the event dictionary
        body = json.loads(event["body"])

        location = body.get("location")
        if not location:
            return {
                'statusCode': 400,
                'body': json.dumps({'message': 'location is required in format postal_code,city'})
            }



        # # adding id into data
        item = body.copy()


        # remove location
        item.pop("location", None)


    elif "multipart/form-data" in content_type:
        #place code to deal with multipart/form-data

        #in multipart/formdata out data in base64 encoded
        # Decode Base64
        body_bytes = base64.b64decode(event["body"])

        #our multipart body is split into individual parts with each part representing a text/file feild
        # Parse multipart
        multipart_data = decoder.MultipartDecoder(body_bytes, content_type)
        #we will later loop over multipart_data.parts to process each key value pair

        #loop through multipart_data and record the key value pairs
        for i in multipart_data.parts:
            cd = i.headers[b"Content-Disposition"].decode() #I dont understand this code

            #extract field name
            field_name = None
            fieldname_split = cd.split('name="')
            if len(fieldname_split) > 1:
                rest = fieldname_split[1]
                field_name = rest.split('"')[0]

            if not field_name:
                continue

            #Image file handling
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
                s3.put_object(
                    Bucket=s3_bucket,
                    Key=s3_key,
                    Body=file_bytes,
                    ContentType=content_type_part
                )

                image_url = f"https://{s3_bucket}.s3.amazonaws.com/{s3_key}"

            #location needs separate handling
            elif field_name == "location":
                location = i.text

            #All other text fields (generic handling)
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
    table.put_item(Item=item)


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
