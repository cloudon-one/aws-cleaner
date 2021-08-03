import json
import boto3
import os

keep_instances = ["sftp-bot"]
keep_tag = os.environ['KEEP_TAG']

USED_REGIONS = [
    'us-east-1',
    'us-east-2',
    'us-west-1',
    'us-west-2',
    'eu-central-1',
    'eu-west-1'
]

def get_aws_regions():
    """Get all AWS regions

    :return: List of AWS region names
    """

    print("[INFO]: Getting all available AWS regions")
    client = boto3.client('ec2')
    regions = [region['RegionName'] for region in client.describe_regions()['Regions']]
    
    return regions

def stop_all_instances(regions):
    """Stop all EC2 instances

    This will stop all instances in all the regions in the input

    :param regions: List of AWS region names
    """

    print("====== EC2 ======")
    for region in regions:
        instances_to_stop = []
        print(f'[INFO]: Getting instances in region: {region}')
        ec2_specific_region = boto3.client('ec2', region_name='{}'.format(region))
        response = ec2_specific_region.describe_instances()
        if "Reservations" in response:
            for reservation in response["Reservations"]:
                if "Instances" in reservation:
                    for instance in reservation["Instances"]:
                        # Ignore spot instances
                        if 'InstanceLifecycle' in instance and instance['InstanceLifecycle'] == 'spot':
                            continue
                        instance_id = instance["InstanceId"]
                        state = instance["State"]["Name"]
                        instance_name = ""
                        instance_owner = ""
                        instance_project = ""
                        if "Tags" in instance:
                            for tag in instance["Tags"]:
                                if tag["Key"] == keep_tag:
                                    keep_instances.append(instance_id)
                                if tag["Key"] == "Name":
                                    instance_name = tag["Value"]
                                if tag["Key"] == "Owner":
                                    instance_owner = tag["Value"]
                                if tag["Key"] == "Project":
                                    instance_project = tag["Value"]
                        if state == "running" and instance_name not in keep_instances and instance_id not in keep_instances:
                            print(f'[INFO]: Instance with ID "{instance_id}" and name "{instance_name}" will be stopped.')
                            instances_to_stop.append(instance_id)
        
        if instances_to_stop:
            ec2_specific_region.stop_instances(InstanceIds=instances_to_stop)
            print(f'[INFO]: Stopped instances: {str(instances_to_stop)}')

def unmonitor_all_instances(regions):
    """Stop detailed monitoring on all EC2 instances

    This will stop CloudWatch detailed monitoring on all instances 
    in all the regions in the input

    :param regions: List of AWS region names
    """

    print("====== EC2 - Unmonitor ======")
    for region in regions:
        instances_to_unmonitor = []
        print(f'[INFO]: Getting instances in region: {region}')
        ec2_specific_region = boto3.client('ec2', region_name='{}'.format(region))
        response = ec2_specific_region.describe_instances()
        if "Reservations" in response:
            for reservation in response["Reservations"]:
                if "Instances" in reservation:
                    for instance in reservation["Instances"]:
                        instance_id = instance["InstanceId"]
                        monitor_state = instance["Monitoring"]["State"]
                        if monitor_state == 'enabled':
                            print(f'[INFO]: Instance with ID "{instance_id}" will be unmonitored.')
                            instances_to_unmonitor.append(instance_id)
        
        if instances_to_unmonitor:
            ec2_specific_region.unmonitor_instances(InstanceIds=instances_to_unmonitor)
            print(f'[INFO]: Unmonitored instances: {str(instances_to_unmonitor)}')

def release_unassociated_eip(regions):
    """Release all unassociated Elastic IPs

    This will release all unassociated Elastic IPs in all the regions in the input

    :param regions: List of AWS region names
    """

    print("====== Elastic IPs ======")
    for region in regions:
        print(f'[INFO]: Getting all unassociated Elastic IPs in region: {region}')
        ec2_specific_region = boto3.client('ec2', region_name='{}'.format(region))
        response = ec2_specific_region.describe_addresses(AllocationIds=[])
        for address in response['Addresses']:
            allocation_id = address['AllocationId']
            if not 'InstanceId' in address and not 'NetworkInterfaceId' in address:
                try:
                    print(f'[INFO]: Releasing address with allocation ID: {allocation_id}')
                    response = ec2_specific_region.release_address(AllocationId=allocation_id)
                except:
                    print(f'[ERROR]: Failed to release address with allocation ID: {allocation_id}')
                    
def delete_available_ebs_volumes(regions):
    """Delete all available EBS volumes

    This will delete all available (unassociated with an instance) EBS volumes
    in all the regions in the input

    :param regions: List of AWS region names
    """

    print("====== EBS Volumes ======")
    for region in regions:
        print(f'[INFO]: Getting all available (unused) EBS volumes in region: {region}')
        ec2_specific_region = boto3.client('ec2', region_name='{}'.format(region))
        response = ec2_specific_region.describe_volumes()
        for volume in response['Volumes']:
            if volume['State'] == 'available':
                volume_id = volume['VolumeId']
                try:
                    print(f'[INFO]: Deleting EBS volume with ID: {volume_id}')
                    response = ec2_specific_region.delete_volume(VolumeId=volume_id)
                except:
                    print(f'[ERROR]: Failed to delete volume with ID: {volume_id}')

def lambda_handler(event, context):
    check_all_regions = os.environ['CHECK_ALL_REGIONS']
    if check_all_regions == 'true':
        regions = get_aws_regions()
    elif check_all_regions == 'false':
        regions = USED_REGIONS

    stop_all_instances(regions)
    unmonitor_all_instances(regions)
    release_unassociated_eip(regions)
    delete_available_ebs_volumes(regions)

    return {
        'statusCode': 200,
        'body': json.dumps('Success!')
    }