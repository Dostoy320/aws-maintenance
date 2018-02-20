# 
# Run this function with the following environment variables set to create manual RDS snapshots:
# instances = [comma-separated string of rds instance names]
# region = AWS region - ie: us-east-1
#

import botocore  
import datetime  
import re  
import logging
import boto3
import os
 
region= os.environ.get("region"); 
instances = os.environ.get("instances").split(",");
 
print('Loading function')
 
def lambda_handler(event, context):  
    source = boto3.client('rds', region_name=region)
    for instance in instances:
        try:
            timestamp1 = str(datetime.datetime.now().strftime('%Y-%m-%d-%H-%-M-%S')) + "lambda-snap"
            snapshot = "{0}-{1}-{2}".format("auto-manual", instance,timestamp1)
            response = source.create_db_snapshot(DBSnapshotIdentifier=snapshot, DBInstanceIdentifier=instance)
            print(response)
        except botocore.exceptions.ClientError as e:
            raise Exception("Could not create snapshot: %s" % e)