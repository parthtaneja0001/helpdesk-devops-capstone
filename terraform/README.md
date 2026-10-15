# Terraform — AWS VPC + EKS

Creates a VPC (2 public + 2 private subnets, NAT gateway) and an EKS cluster with a managed node group.

```bash
aws configure                 # credentials stay on your machine, never in git
cp terraform.tfvars.example terraform.tfvars
terraform init
terraform plan
terraform apply
$(terraform output -raw configure_kubectl)
# ... deploy the app ...
terraform destroy             # always destroy afterwards to avoid AWS charges
```
