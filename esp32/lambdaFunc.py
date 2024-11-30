### this is the code for a lambda function that supports a API gateway endpoint that fetches data from a DynamoDB table. ###

import json
import boto3
from boto3.dynamodb.conditions import Key
from decimal import Decimal

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('esp32water')

# Helper function to convert Decimal types to floats
def decimal_default(obj):
    if isinstance(obj, Decimal):
        return float(obj)
    raise TypeError
    
    

def lambda_handler(event, context):
    # Get and parse the device_id parameter
    device_id = event.get('queryStringParameters', {}).get('device_id')
    
    # Check if device_id is provided
    if not device_id:
        return {
            'statusCode': 400,
            'body': json.dumps('device_id is required')
        }
    
    # If device_id is expected as a number, cast to int
    try:
        device_id = int(device_id)  # This line parses it as an integer
    except ValueError:
        return {
            'statusCode': 400,
            'body': json.dumps('Invalid device_id format, expected a number')
        }
    
    # Query DynamoDB
    response = table.query(
        KeyConditionExpression=Key('device_id').eq(device_id)
    )
    
    # Use json.dumps with default=decimal_default to convert Decimal to float
    return {
        'statusCode': 200,
        'body': json.dumps(response['Items'], default=decimal_default),
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
        }
    }
