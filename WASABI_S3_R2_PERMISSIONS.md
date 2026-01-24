# Wasabi / S3 / R2 IAM Roles & Permissions Guide

This guide explains the IAM roles and permissions needed for Wasabi, AWS S3, and Cloudflare R2 so that users can save files to buckets via presigned URLs.

## Overview

Your application uses **presigned URLs** for user uploads/downloads, which means:
- ✅ **Users don't need their own credentials** - they upload directly to storage using temporary presigned URLs
- ✅ **Backend service needs permissions** - your Render service generates presigned URLs and performs direct operations
- ✅ **Secure** - presigned URLs expire after a set time (default: 1 hour)
- ❌ **NEVER give users root/admin access** - users don't get any credentials at all
- ❌ **NEVER give backend service root access** - use minimal required permissions only

## Architecture

```
User Browser → Render Service (generates presigned URL) → Wasabi/S3/R2 Bucket
                ↑
                └── Needs IAM permissions to generate presigned URLs
```

## Required Permissions

Your backend service needs these S3 permissions:

### Minimum Required Permissions

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "s3:PutObject",        // Generate presigned upload URLs + direct uploads
        "s3:GetObject",        // Generate presigned download URLs + direct downloads
        "s3:DeleteObject",     // Delete files
        "s3:ListBucket"        // List files in bucket
      ],
      "Resource": [
        "arn:aws:s3:::your-bucket-name",
        "arn:aws:s3:::your-bucket-name/*"
      ]
    }
  ]
}
```

### Recommended Permissions (with additional features)

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "s3:PutObject",
        "s3:PutObjectAcl",      // Set object ACLs (if needed)
        "s3:GetObject",
        "s3:GetObjectVersion",  // Access object versions
        "s3:DeleteObject",
        "s3:DeleteObjectVersion", // Delete object versions
        "s3:ListBucket",
        "s3:ListBucketVersions", // List object versions
        "s3:GetBucketLocation"  // Get bucket region
      ],
      "Resource": [
        "arn:aws:s3:::your-bucket-name",
        "arn:aws:s3:::your-bucket-name/*"
      ]
    }
  ]
}
```

---

## Wasabi Setup

### Step 1: Create IAM User

1. Log in to [Wasabi Console](https://console.wasabi.com)
2. Go to **Access Keys** → **Create Access Key**
3. Save the **Access Key ID** and **Secret Access Key** securely
4. These will be your `WASABI_ACCESS_KEY_ID` and `WASABI_SECRET_ACCESS_KEY`

### Step 2: Create Bucket

1. Go to **Buckets** → **Create Bucket**
2. Name: `variosync-data` (or your preferred name)
3. Region: Choose closest to your Render service (e.g., `us-east-1`)
4. Note the endpoint: `https://s3.us-east-1.wasabisys.com`

### Step 3: Configure Bucket Policy (Optional)

Wasabi uses IAM users with access keys, so bucket policies are optional. However, you can add a bucket policy for additional security:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "AllowBackendService",
      "Effect": "Allow",
      "Principal": {
        "AWS": "*"
      },
      "Action": [
        "s3:PutObject",
        "s3:GetObject",
        "s3:DeleteObject",
        "s3:ListBucket"
      ],
      "Resource": [
        "arn:aws:s3:::variosync-data",
        "arn:aws:s3:::variosync-data/*"
      ],
      "Condition": {
        "StringEquals": {
          "aws:PrincipalAccessKeyId": "YOUR_ACCESS_KEY_ID"
        }
      }
    }
  ]
}
```

**Note:** Wasabi primarily uses IAM users, so the bucket policy is mainly for additional restrictions. The access keys themselves provide the permissions.

### Step 4: Set Environment Variables

In your Render dashboard, set:

```bash
WASABI_ACCESS_KEY_ID=your-access-key-id
WASABI_SECRET_ACCESS_KEY=your-secret-access-key
WASABI_ENDPOINT=https://s3.us-east-1.wasabisys.com
WASABI_BUCKET=variosync-data
```

---

## AWS S3 Setup

### Step 1: Create IAM User

1. Go to [AWS IAM Console](https://console.aws.amazon.com/iam/)
2. **Users** → **Create User**
3. Username: `variosync-backend`
4. Select **"Provide user access to the AWS Management Console"** → **No** (programmatic access only)
5. Click **Next**

### Step 2: Attach Permissions Policy

1. Select **"Attach policies directly"**
2. Click **"Create policy"** (opens new tab)
3. Switch to **JSON** tab
4. Paste this policy:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "s3:PutObject",
        "s3:GetObject",
        "s3:DeleteObject",
        "s3:ListBucket"
      ],
      "Resource": [
        "arn:aws:s3:::your-bucket-name",
        "arn:aws:s3:::your-bucket-name/*"
      ]
    }
  ]
}
```

5. Replace `your-bucket-name` with your actual bucket name
6. Click **"Next"** → Name: `VariosyncS3Access` → **Create policy**
7. Go back to user creation tab, refresh policies, select `VariosyncS3Access`
8. Click **Next** → **Create user**

### Step 3: Create Access Keys

1. Click on the newly created user
2. Go to **Security credentials** tab
3. Click **Create access key**
4. Select **"Application running outside AWS"**
5. Click **Next** → **Create access key**
6. **Save the Access Key ID and Secret Access Key** (you won't see the secret again!)

### Step 4: Create S3 Bucket

1. Go to [S3 Console](https://s3.console.aws.amazon.com/)
2. **Create bucket**
3. Name: `variosync-data` (must be globally unique)
4. Region: Choose closest to your Render service
5. **Block Public Access**: Keep enabled (presigned URLs work without public access)
6. Click **Create bucket**

### Step 5: Set Environment Variables

In your Render dashboard:

```bash
AWS_ACCESS_KEY_ID=your-access-key-id
AWS_SECRET_ACCESS_KEY=your-secret-access-key
AWS_ENDPOINT_URL=https://s3.us-east-1.amazonaws.com  # or your region endpoint
AWS_BUCKET_NAME=variosync-data
```

---

## Cloudflare R2 Setup

### Step 1: Create API Token

1. Go to [Cloudflare Dashboard](https://dash.cloudflare.com/)
2. Select your account
3. Go to **R2** → **Manage R2 API Tokens**
4. Click **Create API Token**
5. Permissions:
   - **Object Read & Write** (for your bucket)
   - **Admin Read** (optional, for bucket management)
6. Click **Create API Token**
7. **Save the Access Key ID and Secret Access Key**

### Step 2: Create R2 Bucket

1. Go to **R2** → **Create bucket**
2. Name: `variosync-data`
3. Location: Choose closest to your Render service
4. Click **Create bucket**

### Step 3: Get R2 Endpoint

1. Click on your bucket
2. Go to **Settings** tab
3. Note the **S3 API** endpoint (e.g., `https://xxx.r2.cloudflarestorage.com`)

### Step 4: Set Environment Variables

In your Render dashboard:

```bash
AWS_ACCESS_KEY_ID=your-r2-access-key-id
AWS_SECRET_ACCESS_KEY=your-r2-secret-access-key
AWS_ENDPOINT_URL=https://xxx.r2.cloudflarestorage.com
AWS_BUCKET_NAME=variosync-data
```

**Note:** R2 uses S3-compatible API, so use the same `AWS_*` environment variables.

---

## User-Specific Paths (Recommended)

For better organization and security, use user-specific paths in your bucket:

```
bucket-name/
  ├── users/
  │   ├── user-123/
  │   │   ├── uploads/
  │   │   ├── exports/
  │   │   └── processed/
  │   └── user-456/
  │       └── ...
```

### Path-Based Permissions (Optional)

If you want to restrict users to their own paths, you can use IAM policy conditions:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "s3:PutObject",
        "s3:GetObject",
        "s3:DeleteObject"
      ],
      "Resource": "arn:aws:s3:::your-bucket-name/users/${aws:userid}/*",
      "Condition": {
        "StringLike": {
          "s3:prefix": "users/${aws:userid}/*"
        }
      }
    },
    {
      "Effect": "Allow",
      "Action": "s3:ListBucket",
      "Resource": "arn:aws:s3:::your-bucket-name",
      "Condition": {
        "StringLike": {
          "s3:prefix": "users/${aws:userid}/*"
        }
      }
    }
  ]
}
```

**Note:** This requires using IAM roles with user-specific identifiers. For most use cases, the backend service handles all operations, so this is optional.

---

## Testing Permissions

### Test Presigned URL Generation

```python
from integrations.wasabi_client import WasabiClientFactory

wasabi = WasabiClientFactory.create_from_env()

# Generate upload URL
upload_url = wasabi.get_upload_url("test/file.csv", expires_in=3600)
print(f"Upload URL: {upload_url}")

# Generate download URL
download_url = wasabi.get_download_url("test/file.csv", expires_in=3600)
print(f"Download URL: {download_url}")
```

### Test Direct Operations

```python
# Upload file
wasabi.upload_file("local_file.csv", "test/file.csv")

# List files
files = wasabi.list_files(prefix="test/")
print(f"Files: {files}")

# Delete file
wasabi.delete_file("test/file.csv")
```

---

## ⚠️ IMPORTANT: Do NOT Give Root Access

### Users: NO Credentials Needed
- ❌ **Don't create IAM users for each end-user**
- ❌ **Don't give users access keys**
- ❌ **Don't give users any S3 credentials**
- ✅ **Users only get temporary presigned URLs** (generated by your backend)

### Backend Service: Minimal Permissions Only
- ❌ **Don't use `s3:*` (full access)**
- ❌ **Don't use admin/root IAM policies**
- ❌ **Don't grant permissions to all buckets**
- ✅ **Use only the 4 required permissions** listed above
- ✅ **Restrict to your specific bucket only**

### Why Root Access is Dangerous

If you give root/admin access:
- 🚨 **Users could delete all files** in the bucket
- 🚨 **Users could access other users' files**
- 🚨 **Users could modify bucket settings**
- 🚨 **No audit trail** of who did what
- 🚨 **Compliance violations** (GDPR, HIPAA, etc.)

### The Secure Approach

```
✅ CORRECT:
User → Backend (with minimal permissions) → Generates presigned URL → User uploads
   (no user credentials)   (only 4 permissions)      (expires in 1 hour)

❌ WRONG:
User → Direct access with root credentials → Can do anything
   (has full access)        (dangerous!)
```

## Security Best Practices

### 1. **Never Expose Access Keys to Frontend**
- ✅ Access keys stay in backend (Render environment variables)
- ✅ Users only get temporary presigned URLs
- ❌ Never put access keys in client-side code

### 2. **Use Least Privilege**
- ✅ Only grant permissions your app actually needs
- ✅ Start with minimum permissions, add more if needed
- ❌ Don't use `s3:*` (full access) unless absolutely necessary

### 3. **Rotate Access Keys Regularly**
- ✅ Rotate access keys every 90 days
- ✅ Use different keys for dev/staging/production
- ✅ Monitor for unauthorized access

### 4. **Enable Bucket Versioning** (Optional)
- Useful for recovery and audit trails
- Requires `s3:GetObjectVersion` and `s3:DeleteObjectVersion` permissions

### 5. **Use Bucket Policies for Additional Security**
- Restrict by IP address (if your Render service has static IPs)
- Add time-based restrictions
- Log all access via CloudTrail (AWS) or Wasabi audit logs

---

## Troubleshooting

### Error: "Access Denied" when generating presigned URL

**Cause:** IAM user/role doesn't have required permissions

**Solution:**
1. Verify access keys are correct
2. Check IAM policy includes `s3:PutObject` and `s3:GetObject`
3. Ensure bucket name matches in policy

### Error: "InvalidAccessKeyId"

**Cause:** Access key ID is incorrect or doesn't exist

**Solution:**
1. Verify `WASABI_ACCESS_KEY_ID` or `AWS_ACCESS_KEY_ID` is correct
2. Check for typos or extra spaces
3. Regenerate access keys if needed

### Error: "SignatureDoesNotMatch"

**Cause:** Secret access key is incorrect

**Solution:**
1. Verify `WASABI_SECRET_ACCESS_KEY` or `AWS_SECRET_ACCESS_KEY` is correct
2. Check for typos or extra spaces
3. Regenerate access keys if needed

### Error: "NoSuchBucket"

**Cause:** Bucket name is incorrect or doesn't exist

**Solution:**
1. Verify bucket name in environment variables
2. Check bucket exists in Wasabi/S3/R2 console
3. Verify endpoint URL is correct

### Presigned URLs work but direct operations fail

**Cause:** Missing permissions for direct operations

**Solution:**
- Add `s3:ListBucket` for listing
- Add `s3:DeleteObject` for deletion
- Verify all required actions are in IAM policy

---

## Summary

### Quick Checklist

- [ ] Created IAM user/access keys
- [ ] Attached policy with required S3 permissions
- [ ] Created bucket
- [ ] Set environment variables in Render
- [ ] Tested presigned URL generation
- [ ] Tested direct upload/download operations

### Required Permissions Summary

| Operation | Required Permission | Used For |
|-----------|-------------------|----------|
| Generate upload URL | `s3:PutObject` | Presigned upload URLs |
| Generate download URL | `s3:GetObject` | Presigned download URLs |
| Direct upload | `s3:PutObject` | Server-side uploads |
| Direct download | `s3:GetObject` | Server-side downloads |
| Delete file | `s3:DeleteObject` | File deletion |
| List files | `s3:ListBucket` | File listing |

---

## Additional Resources

- [Wasabi IAM Documentation](https://wasabi-support.zendesk.com/hc/en-us/articles/360044599331-How-do-I-create-an-IAM-user-and-access-key-)
- [AWS S3 IAM Policies](https://docs.aws.amazon.com/AmazonS3/latest/userguide/access-policy-language-overview.html)
- [Cloudflare R2 API Tokens](https://developers.cloudflare.com/r2/api/s3/api/)
- [boto3 Presigned URLs](https://boto3.amazonaws.com/v1/documentation/api/latest/guide/s3-presigned-urls.html)
