
# AWS resource auto-deletion

## Purpose
This defines the policy that we want to implement to auto-delete AWS resources based on certain criteria. The principal reason is to save costs, but this also benefits security.
﻿
We want to regularly delete all resources that aren't tagged in a certain way.
We will start with the "Dev/Testing" AWS account (*********625) and possibly extend into other accounts from there.
Policies
The script should run once a day around 23:00 (IL time).
﻿
If something has tag with Key=auto-deletion,Value=skip-resource, don’t delete.
If something has Key=auto-deletion,Value=stop-resource, stop it (if that is possible for this type of resource). People can restart it if they need it.
If something has tag with Key=auto-deletion,Value=skip-notify, don’t notify even if the rules below say we should.
If an EC2 instance has a tag with Key=spotinst:accountId (any value), ignore it and ignore the EBS volumes and EIPs attached to it.
﻿
In all other cases:
﻿
EIPs not associated with an EC2 instance: delete
RDS databases: stop
Load balancers: delete
Kinesis streams:
if they match the regexp upsolver_* : notify
otherwise: delete
MSK streams: delete
OpenSearch domains: delete
EC2 instances: terminate and delete all EBS volumes
EBS volumes not attached to EC2 instance: delete
S3 buckets: ignore
﻿
The script should log the deleted resources and send an email listing deleted resources to  infra@upsolver.com .
Resources for which there will only be notification should be included in a separate paragraph in the same email.