#!/bin/bash

# Exit immediately if a command exits with a non-zero status.
set -e

# Define colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}Running Terraform Deployment Script...${NC}"

# --- Terraform Steps ---

# 1. Format the code
echo -e "\n${YELLOW}Step 1: Formatting Terraform code...${NC}"
terraform fmt -recursive
echo -e "${GREEN}Formatting complete.${NC}"

# 2. Initialize Terraform
echo -e "\n${YELLOW}Step 2: Initializing Terraform...${NC}"
terraform init
echo -e "${GREEN}Initialization complete.${NC}"

# 3. Validate the configuration
echo -e "\n${YELLOW}Step 3: Validating Terraform configuration...${NC}"
terraform validate
echo -e "${GREEN}Validation successful.${NC}"

# 4. Create a plan
echo -e "\n${YELLOW}Step 4: Creating Terraform execution plan...${NC}"
terraform plan -out=tfplan -var-file="terraform.tfvars"
echo -e "${GREEN}Plan created: tfplan${NC}"

# 5. Apply the plan
echo -e "\n${YELLOW}Step 5: Applying Terraform plan...${NC}"
echo -e "${RED}WARNING: Applying with -auto-approve. Review the plan carefully before running in production.${NC}"
terraform apply -auto-approve tfplan

echo -e "\n${GREEN}Terraform apply complete!${NC}"

# Optional: Output ALB URL
echo -e "\n${YELLOW}Fetching outputs...${NC}"
APP_URL=$(terraform output -raw application_url)
echo -e "${GREEN}Application URL: ${APP_URL}${NC}"

echo -e "\n${GREEN}Deployment finished.${NC}"