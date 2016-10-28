# AWS Lambda - EC2 - AutoSnapshot

## Python

##EC2 Tag
Key = AutoSnapshot  
Value = Generaton Number  

Example(1 week)  
Rate(1 day)  
Key : AutoSnapshot  
Value : 7

##IAM
    {  
        "Version": "2012-10-17",  "Statement": [  
            {  
                "Effect": "Allow",  
                "Action": [  
                    "ec2:Describe*",  
                    "ec2:CreateSnapshot",  
                    "ec2:DescribeSnapshots",  
                    "ec2:DeleteSnapshot",  
                    "ec2:CreateTags"  
                ],  
                "Resource": "*"
            },
            {
                "Effect": "Allow",
                "Action": "elasticloadbalancing:Describe*",
                "Resource": "*"
            },
            {
                "Effect": "Allow",
                "Action": [
                    "cloudwatch:ListMetrics",
                    "cloudwatch:GetMetricStatistics",
                    "cloudwatch:Describe*"
                ],
                "Resource": "*"
            },
            {
                "Effect": "Allow",
                "Action": "autoscaling:Describe*",
                "Resource": "*"
            }
        ]
    }
