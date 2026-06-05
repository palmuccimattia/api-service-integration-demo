import boto3

def lambda_handler(event, context):
    ec2 = boto3.client('ec2', region_name='us-east-1')
    ec2.start_instances(InstanceIds=['i-04698374031a592cf'])  # <-- Sostituisci con ID istanza EC2
    return "EC2 started"
