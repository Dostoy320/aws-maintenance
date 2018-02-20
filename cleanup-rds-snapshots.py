
# 
# Run this function with the following environment variables set to clean up RDS snapshots:
# instances = comma-separated string of rds instance names
# region = AWS region - ie: us-east-1
# retentionDays = number of days to retain snapshots
# outerLimitDays = ignore snapshots older than this many days
#

import json
import boto3
import os
from datetime import datetime, timedelta, tzinfo

class Zone(tzinfo):
    def __init__(self,offset,isdst,name):
        self.offset = offset
        self.isdst = isdst
        self.name = name
    def utcoffset(self, dt):
        return timedelta(hours=self.offset) + self.dst(dt)
    def dst(self, dt):
        return timedelta(hours=1) if self.isdst else timedelta(0)
    def tzname(self,dt):
        return self.name

UTC = Zone(5,False,'UTC')

region= os.environ.get("region")
instances = os.environ.get("instances").split(",")

retentionDays = int(os.environ.get("retentionDays"));
outerLimitDays = int(os.environ.get("outerLimitDays"));
retentionDate = datetime.now(UTC) - timedelta(days=retentionDays)
outerLimitDate = datetime.now(UTC) - timedelta(days=outerLimitDays)


def lambda_handler(event, context):
    
    print("Connecting to RDS")
    rds = boto3.setup_default_session(region_name=region)
    client = boto3.client('rds')
    
    for instance in instances:
        
        print('Querying for %s snapshots' % instance)
        
        snapshots = client.describe_db_snapshots(SnapshotType='manual',DBInstanceIdentifier=instance)
        
        print('Deleting all DB Snapshots older than %s and younger than %s' % (retentionDate, outerLimitDate))
    
        for i in snapshots['DBSnapshots']:
            if i['SnapshotCreateTime'] < retentionDate and i['SnapshotCreateTime'] > outerLimitDate:
                print ('Deleting snapshot %s' % i['DBSnapshotIdentifier'])
                client.delete_db_snapshot(DBSnapshotIdentifier=i['DBSnapshotIdentifier'])