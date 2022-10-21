import boto3

def lambda_handler(event, context):
    ACCESS_KEY = "AKIA6BGE6E65ZS7P2MZK"
    SECRET_KEY = "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"
    AWS_REGION = "us-east-2"
    topic = event.get("TOPIC_ARN")
    msg = event.get( "MESSAGE")
    
 
    client = boto3.client('sns',
    aws_access_key_id = ACCESS_KEY,
    aws_secret_access_key = SECRET_KEY,
    region_name = AWS_REGION)
    
    response = client.publish(
        TopicArn = topic,
        Message = msg ,
        Subject='Hello'
    )