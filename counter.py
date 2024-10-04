import boto3
from botocore.exceptions import ClientError

# Initialize the DynamoDB client
dynamodb = boto3.resource('dynamodb')

def check_or_create_table():
    table_name = 'miguelPuentesCounter'
    try:
        # Check if the table exists
        table = dynamodb.Table(table_name)
        table.load()  # This will throw an error if the table doesn't exist
        print(f"Table {table_name} already exists.")
    except ClientError as e:
        if e.response['Error']['Code'] == 'ResourceNotFoundException':
            # Create the table if it doesn't exist
            table = dynamodb.create_table(
                TableName=table_name,
                KeySchema=[
                    {
                        'AttributeName': 'CounterID',
                        'KeyType': 'HASH'  # Partition key
                    }
                ],
                AttributeDefinitions=[
                    {
                        'AttributeName': 'CounterID',
                        'AttributeType': 'S'  # String type for CounterID
                    }
                ],
                BillingMode='PAY_PER_REQUEST'  # Keep costs low with on-demand pricing
            )
            table.wait_until_exists()
            print(f"Created table {table_name}.")
    return table

def get_and_update_counter():
    table = check_or_create_table()
    # Retrieve the current visitor count
    try:
        response = table.get_item(Key={'CounterID': 'VisitorCount'})
        count = response['Item']['Count']
    except KeyError:
        # If the count doesn't exist, initialize it
        count = 0

    # Increment the count
    new_count = count + 1

    # Update the item with the new count
    table.put_item(
        Item={
            'CounterID': 'VisitorCount',
            'Count': new_count
        }
    )
    return new_count

# Lambda handler
def lambda_handler(event, context):
    new_count = get_and_update_counter()
    return {
        'statusCode': 200,
        'body': f'Visitor Count: {new_count}'
    }
