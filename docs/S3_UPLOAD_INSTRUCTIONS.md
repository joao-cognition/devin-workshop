# S3 Upload Instructions for Workshop Data

## Overview

The workshop data files need to be uploaded to the S3 bucket `devin-workshop` in the `eu-north-1` region for participants to access during the workshop.

## Files to Upload

The following files are located in `/home/ubuntu/santander-workshop/data/`:

| File | Description | Size |
|------|-------------|------|
| `santander_customers.xlsx` | Customer demographics and account data (500 records) | ~100KB |
| `santander_transactions.xlsx` | Transaction history (5000 records) | ~500KB |
| `customer_complaints.csv` | Complaints data with outliers (1000 records) | ~150KB |
| `product_holdings.csv` | Product metrics for bubble charts (12 records) | ~2KB |
| `database_schema.sql` | SQL schema documentation | ~5KB |

## Upload Commands

### Using AWS CLI

```bash
# Configure AWS CLI (if not already done)
aws configure
# Enter your AWS Access Key ID, Secret Access Key, and region (eu-north-1)

# Upload all files to S3
aws s3 cp /home/ubuntu/santander-workshop/data/santander_customers.xlsx s3://devin-workshop/santander-workshop/ --region eu-north-1
aws s3 cp /home/ubuntu/santander-workshop/data/santander_transactions.xlsx s3://devin-workshop/santander-workshop/ --region eu-north-1
aws s3 cp /home/ubuntu/santander-workshop/data/customer_complaints.csv s3://devin-workshop/santander-workshop/ --region eu-north-1
aws s3 cp /home/ubuntu/santander-workshop/data/product_holdings.csv s3://devin-workshop/santander-workshop/ --region eu-north-1
aws s3 cp /home/ubuntu/santander-workshop/data/database_schema.sql s3://devin-workshop/santander-workshop/ --region eu-north-1

# Or upload entire directory at once
aws s3 sync /home/ubuntu/santander-workshop/data/ s3://devin-workshop/santander-workshop/ --region eu-north-1

# Verify upload
aws s3 ls s3://devin-workshop/santander-workshop/ --region eu-north-1
```

### Using AWS Console

1. Navigate to: https://eu-north-1.console.aws.amazon.com/s3/buckets/devin-workshop?region=eu-north-1
2. Click "Create folder" and name it `santander-workshop`
3. Navigate into the folder
4. Click "Upload"
5. Drag and drop all files from the `data/` directory
6. Click "Upload"

## Setting Public Access (for Workshop)

To allow workshop participants to download files without AWS credentials:

### Option 1: Bucket Policy (Recommended for Workshop)

Add this bucket policy to allow public read access to the workshop folder:

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "PublicReadWorkshopData",
            "Effect": "Allow",
            "Principal": "*",
            "Action": "s3:GetObject",
            "Resource": "arn:aws:s3:::devin-workshop/santander-workshop/*"
        }
    ]
}
```

### Option 2: Pre-signed URLs

Generate pre-signed URLs that expire after the workshop:

```bash
# Generate pre-signed URL valid for 24 hours
aws s3 presign s3://devin-workshop/santander-workshop/santander_customers.xlsx --expires-in 86400 --region eu-north-1
```

## Public URLs (After Setting Public Access)

Once public access is configured, files will be accessible at:

```
https://devin-workshop.s3.eu-north-1.amazonaws.com/santander-workshop/santander_customers.xlsx
https://devin-workshop.s3.eu-north-1.amazonaws.com/santander-workshop/santander_transactions.xlsx
https://devin-workshop.s3.eu-north-1.amazonaws.com/santander-workshop/customer_complaints.csv
https://devin-workshop.s3.eu-north-1.amazonaws.com/santander-workshop/product_holdings.csv
https://devin-workshop.s3.eu-north-1.amazonaws.com/santander-workshop/database_schema.sql
```

## Verification

After upload, verify files are accessible:

```bash
# Test download
curl -I https://devin-workshop.s3.eu-north-1.amazonaws.com/santander-workshop/santander_customers.xlsx
```

Expected response should include `HTTP/1.1 200 OK`.

## Cleanup (After Workshop)

To remove workshop data after the session:

```bash
aws s3 rm s3://devin-workshop/santander-workshop/ --recursive --region eu-north-1
```

Or remove public access by deleting the bucket policy.
