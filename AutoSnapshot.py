import json
import datetime
import boto3
from pprint import pprint

# Tag
key = "Key"
tag = "AutoSnapshot"

# EC2 Info
def get_ec2_info(tag):
    client = boto3.client('ec2')
    ec2_info = client.describe_instances(
        Filters = [
            {
                'Name': 'tag-key',
                'Values': [
                    tag,
                ]
            },
        ],
    )
    count = len(ec2_info['Reservations'])
    for i in range(count):
        ebs_count = len(ec2_info['Reservations'][i]['Instances'][0]['BlockDeviceMappings'])
        for j in range(ebs_count):
            instance_id = ec2_info['Reservations'][i]['Instances'][0]['InstanceId']
            ebs_id = ec2_info['Reservations'][i]['Instances'][0]['BlockDeviceMappings'][j]['Ebs']['VolumeId']
            instance_name = get_instance_name(instance_id)
            generation = get_genetation(instance_id, tag)
            snapshots = get_snapshot_data(ebs_id, key, tag)
            snapshot_count = len(snapshots['Snapshots'])
            if generation == 0:
                continue
            if snapshot_count >= generation:
                snapshot_list = []
                for k in range(snapshot_count):
                    snapshots = get_snapshot_data(ebs_id, key, tag)
                    snapshot_data = [snapshots['Snapshots'][k]['StartTime'], snapshots['Snapshots'][k]['SnapshotId']]
                    snapshot_list.append(snapshot_data)
                    snapshot_list.sort()
                snapshot_id = snapshot_list[0][1]
                delete_snapshot(snapshot_id)
                create_snapshot(instance_id, ebs_id, instance_name)
            else:
                create_snapshot(instance_id, ebs_id, instance_name)

# Get Generation
def get_genetation(instance_id, tag):
    client = boto3.client('ec2')
    generaton_tag = client.describe_tags(
        Filters = [
            {
                'Name': 'resource-id',
                'Values': [
                    instance_id,
                ]
            },
            {
                'Name': 'tag-key',
                'Values': [
                    tag
                ]
            }
        ]
    )
    return int(generaton_tag['Tags'][0]['Value'])

# Get Instance Name
def get_instance_name(instance_id):
    client = boto3.client('ec2')
    instance_tag = client.describe_tags(
        Filters = [
            {
                'Name': 'resource-id',
                'Values': [
                    instance_id,
                ]
            },
        ]
    )
    instance_count = len(instance_tag['Tags'])
    for l in range(instance_count):
        if instance_tag['Tags'][l]['Key'] == 'Name':
            instance_name = instance_tag['Tags'][l]['Value']
        else:
            continue
    return instance_name

# Delete Snapshot
def delete_snapshot(snapshot_id):
    client = boto3.client('ec2')
    client.delete_snapshot(
        SnapshotId = snapshot_id
    )
    print("Deleted SnapshotID => " + snapshot_id)
    return

# Get Snapshot Data
def get_snapshot_data(ebs_id, key, tag):
    client = boto3.client('ec2')
    snapshot = client.describe_snapshots(
        Filters = [
            {
                'Name': 'volume-id',
                'Values': [
                    ebs_id
                ]
            },
            {
                'Name': 'tag-key',
                'Values': [
                    key,
                ]
            },
            {
                'Name': 'tag-value',
                'Values': [
                    tag
                ]
            },
            
        ]
    )
    return snapshot

# Create Snapshot
def create_snapshot(instance_id, ebs_id, instance_name):
    ec2 = boto3.resource('ec2')
    ebs = ec2.Volume(ebs_id)
    try:
        now = datetime.datetime.now()
        desc = "Created by " + "%s(%s) from %s" % (tag, instance_id, ebs_id)
        snapshot = ebs.create_snapshot(Description = desc)
        snapshot_id = snapshot.id
        print("Create SnapshotID => " + snapshot_id + ' from ' + instance_name +'(' + ebs_id + ')')
        create_snapshot_tag(snapshot_id, instance_name, ebs_id)
    except:
        return 'NG'

# Create Snapshot Tag
def create_snapshot_tag(snapshot_id, instance_name, ebs_id):
    client = boto3.client('ec2')
    client.create_tags(
        Resources = [
            snapshot_id
        ],
        Tags = [
            {
                'Key': 'Name',
                'Value': instance_name + '(' + ebs_id + ')'
            },
            {
                'Key': key,
                'Value': tag
            },
        ],
    )

# Main
def lambda_handler(event, context):
    get_ec2_info(tag)
