# SWOT FastAPI AWS Deployment using Terraform
This project uses Terraform to provision a complete AWS infrastructure for deploying a FastAPI application (from the `UAH-SWOT-GWIS/SWOT-Pixel_Cloud` repository) that integrates with S3 and CloudWatch. It includes VPC, public/private subnets, NAT Gateway, security groups, IAM roles, an EC2 Auto Scaling Group, and an Application Load Balancer (ALB).

📦 The infrastructure includes:
* A VPC with public and private subnets across two Availability Zones.
* An Application Load Balancer (ALB) to distribute traffic.
* An Auto Scaling Group (ASG) managing EC2 instances running the application in Docker containers within the private subnets.
* A NAT Gateway to allow outbound internet access from private subnets.
* An S3 bucket for application data storage.
* IAM roles and policies with least-privilege principles (attempted).
* Security Groups configured to restrict traffic appropriately.
* CloudWatch Agent configured for log collection.

## Prerequisites
1.  **Terraform:** Install Terraform CLI (>= 1.0).
2.  **AWS Account & Credentials:** You'll need an AWS Access Key ID and Secret Access Key.
3.  **AWS CLI:** Optional but useful for managing AWS resources (`aws configure`).
4.  **SSH Key Pair:** Create an SSH key pair in the target AWS region (`us-east-1` by default). You will need the name of the key pair.
5.  **Git:** Required by the `user_data` script.

## Configuration

1.  **Clone this repository.**. Switch to the branch swot-aws-ec2
2.  **Create/edit `terraform.tfvars` file:**
    * or Copy the example : `cp terraform.tfvars.example terraform.tfvars`
    * Edit the new `terraform.tfvars` file and fill in your **actual** secrets:
        * `earthdata_username`
        * `earthdata_password`
3.  **Edit `terraform.tfvars`:**
    * Review and update non-sensitive configuration values like:
        * `aws_region`
        * `project_name`
        * `instance_type`
        * `key_name` (must match an existing key pair in your AWS account/region)
        * `s3_bucket` (must be globally unique)
        * `allowed_ssh_cidr` (**Change this from `0.0.0.0/0` to your IP!**)

## Deployment

The `build_and_deploy.sh` script handles running the Terraform workflow.

1.  **Make the script executable:**
    ```bash
    chmod +x build_and_deploy.sh
    ```
2.  **Run the script:**
    ```bash
    ./build_and_deploy.sh
    ```

This script will:
* Load environment variables from `terraform.tfvars`.
* Format your Terraform code (`terraform fmt`).
* Initialize Terraform (`terraform init`).
* Validate your configuration (`terraform validate`).
* Create an execution plan (`terraform plan -out=tfplan -var-file="terraform.tfvars"`).
* **Apply the plan automatically (`terraform apply -auto-approve tfplan`)**. Review the plan output carefully.

## Accessing the Application

After successful deployment, the script outputs the `Application URL`. Access it via your browser (e.g., `http://your-alb-dns-name.us-east-1.elb.amazonaws.com`).

## Connecting via SSH (Use Session Manager!)

**RECOMMENDED:** Use [AWS Systems Manager Session Manager](https://docs.aws.amazon.com/systems-manager/latest/userguide/session-manager.html). (Requires `AmazonSSMManagedInstanceCore` policy on the EC2 role - uncomment in `main.tf` if needed). Connect using `aws ssm start-session --target <instance-id>`.

If you must use SSH, connect via a Bastion host or ensure your `allowed_ssh_cidr` is correct and you are connecting from that IP to the instance's **private IP** (if connecting from within the VPC).

## Destroying the Infrastructure

**WARNING:** This deletes *all* created resources. Data in S3 may prevent bucket deletion.

```bash
# Ensure .env is loaded if AWS keys are needed for destroy operation state locks etc.
export $(grep -v '^#' .env | xargs)
terraform destroy -var-file="terraform.tfvars"
```
Confirm by typing yes.