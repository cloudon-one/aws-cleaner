import json
import boto3
import os

keep_instances = ["sftp-bot"]
keep_tag_key = os.environ['KEEP_TAG_KEY']
dry_run = os.environ['DRY_RUN']

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
                                if tag["Key"] == keep_tag_key:
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
            if dry_run == 'false':
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
            if dry_run == 'false':
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
                    if dry_run == 'false':
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
                delete_vol = True

                # Check if the volume is connected to a running EKS cluster
                tags = volume['Tags'] if 'Tags' in volume else []
                for tag in tags:
                    if tag['Key'].startswith('kubernetes.io/cluster'):
                        eks_cluster_name = tag['Key'].split('/')[2]
                        try:
                            eks_specific_region = boto3.client('eks', region_name=region)
                            response = eks_specific_region.describe_cluster(name=eks_cluster_name)
                            delete_vol = False # Don't delete volume is it's connected to existing EKS cluster
                        # Exception thrown if cluster with the name doesn't exist
                        except eks_specific_region.exceptions.ResourceNotFoundException:
                            delete_vol = True
                        break

                if delete_vol is True:
                    try:
                        print(f'[INFO]: Deleting EBS volume with ID: {volume_id}')
                        if dry_run == 'false':
                            response = ec2_specific_region.delete_volume(VolumeId=volume_id)
                    except:
                        print(f'[ERROR]: Failed to delete volume with ID: {volume_id}')

def delete_empty_load_balancers(regions):
    """Delete al empty (classic) load balancers

    This will delete all empty (with no instances) classic load balancers
    in all the regions in the input

    :param regions: List of AWS region names
    """

    print("====== Classic Load Balancers ======")
    for region in regions:
        print(f'[INFO]: Getting all empty (with no instances) classic load balancers in region: {region}')
        elb_specific_region = boto3.client('elb', region_name='{}'.format(region))
        response = elb_specific_region.describe_load_balancers()
        for lb in response['LoadBalancerDescriptions']:
            if len(lb['Instances']) == 0:
                lb_name = lb['LoadBalancerName']
                try:
                    print(f'[INFO]: Deleting classic load balancer: {lb_name}')
                    if dry_run == 'false':
                        response = elb_specific_region.delete_load_balancer(LoadBalancerName=lb_name)
                except:
                    print(f'[ERROR]: Failed to delete classic load balancer: {lb_name}')

def add_created_on_tag(regions):
    """Add "CreatedOn" tag on resources

    This will check the resource creation date against AWS Config
    and add it as a tag to the resource

    :param regions: List of AWS region names
    """

    for region in regions:
        print(f'[INFO]: Getting instances in region: {region}')
        ec2_specific_region = boto3.client('ec2', region_name=region)
        config_specific_region = boto3.client('config', region_name=region)

        # Check if there are discover resources in AWS Config
        response = config_specific_region.get_discovered_resource_counts()
        if response['totalDiscoveredResources'] == 0:
            continue

        response = ec2_specific_region.describe_instances()
        if "Reservations" in response:
            for reservation in response["Reservations"]:
                if "Instances" in reservation:
                    for instance in reservation["Instances"]:
                        # Ignore spot instances
                        if 'InstanceLifecycle' in instance and instance['InstanceLifecycle'] == 'spot':
                            continue

                        # Skip instance if tag already present
                        found_tag = False
                        if "Tags" in instance:
                            for tag in instance["Tags"]:
                                if tag["Key"] == "CreatedOn":
                                    found_tag = True
                                    break
                        if found_tag:
                            continue

                        instance_id = instance["InstanceId"]
                        response = config_specific_region.get_resource_config_history(
                                        resourceType='AWS::EC2::Instance',
                                        resourceId=instance_id)
                        created_on = response['configurationItems'][0]['resourceCreationTime']
                        created_on = created_on.strftime("%d/%m/%Y")
                        print(f'[INFO] Instance {instance_id} created on {created_on}')

                        # Create tag on instance
                        if dry_run == 'false':
                            ec2_specific_region.create_tags(
                                Resources=[instance_id],
                                Tags=[
                                    {
                                        'Key': 'CreatedOn',
                                        'Value': created_on
                                    },
                                ]
                            )

def lambda_handler(event, context):
    check_all_regions = os.environ['CHECK_ALL_REGIONS']
    if check_all_regions == 'true':
        regions = get_aws_regions()
    elif check_all_regions == 'false':
        regions = USED_REGIONS

    stop_all_instances(regions)
    add_created_on_tag(regions)
    unmonitor_all_instances(regions)
    release_unassociated_eip(regions)
    delete_available_ebs_volumes(regions)
    delete_empty_load_balancers(regions)

    return {
        'statusCode': 200,
        'body': json.dumps('Success!')
    }