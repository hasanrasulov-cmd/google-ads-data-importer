# AWS OIDC Setup Guide

## Problem
The error `Not authorized to perform sts:AssumeRoleWithWebIdentity` indicates that the IAM role's trust policy doesn't allow GitHub Actions OIDC to assume the role.

## Solution

### Step 1: Configure GitHub OIDC Provider in AWS (if not already done)

1. Go to AWS IAM Console → Identity providers
2. Click "Add provider"
3. Select "OpenID Connect"
4. Provider URL: `https://token.actions.githubusercontent.com`
5. Audience: `sts.amazonaws.com`
6. Click "Add provider"

### Step 2: Update IAM Role Trust Policy

The IAM role `arn:aws:iam::776117903063:role/pipelines-cd-rvjbng` needs a trust policy that allows GitHub Actions to assume it.

#### Option A: Allow all repositories in your GitHub organization/account

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Federated": "arn:aws:iam::776117903063:oidc-provider/token.actions.githubusercontent.com"
      },
      "Action": "sts:AssumeRoleWithWebIdentity",
      "Condition": {
        "StringEquals": {
          "token.actions.githubusercontent.com:aud": "sts.amazonaws.com"
        }
      }
    }
  ]
}
```

#### Option B: Restrict to specific repository (RECOMMENDED)

Replace `YOUR_GITHUB_ORG` and `YOUR_REPO_NAME` with your actual GitHub organization/username and repository name:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Federated": "arn:aws:iam::776117903063:oidc-provider/token.actions.githubusercontent.com"
      },
      "Action": "sts:AssumeRoleWithWebIdentity",
      "Condition": {
        "StringEquals": {
          "token.actions.githubusercontent.com:aud": "sts.amazonaws.com"
        },
        "StringLike": {
          "token.actions.githubusercontent.com:sub": "repo:YOUR_GITHUB_ORG/YOUR_REPO_NAME:*"
        }
      }
    }
  ]
}
```

#### Option C: Restrict to specific branch (MOST SECURE)

Replace `YOUR_GITHUB_ORG`, `YOUR_REPO_NAME`, and `main` with your actual values:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Federated": "arn:aws:iam::776117903063:oidc-provider/token.actions.githubusercontent.com"
      },
      "Action": "sts:AssumeRoleWithWebIdentity",
      "Condition": {
        "StringEquals": {
          "token.actions.githubusercontent.com:aud": "sts.amazonaws.com"
        },
        "StringLike": {
          "token.actions.githubusercontent.com:sub": "repo:YOUR_GITHUB_ORG/YOUR_REPO_NAME:ref:refs/heads/main"
        }
      }
    }
  ]
}
```

### Step 3: Apply the Trust Policy

1. Go to AWS IAM Console → Roles
2. Find the role: `pipelines-cd-rvjbng`
3. Click on the role → "Trust relationships" tab
4. Click "Edit trust policy"
5. Paste one of the JSON policies above (Option B or C recommended)
6. Click "Update policy"

### Step 4: Verify the OIDC Provider ARN

Make sure the OIDC provider ARN in the trust policy matches the actual provider ARN in your AWS account. The format should be:
- `arn:aws:iam::776117903063:oidc-provider/token.actions.githubusercontent.com`

If your OIDC provider has a different ARN, update the trust policy accordingly.

## Testing

After updating the trust policy, re-run your GitHub Actions workflow. The OIDC authentication should now work.

## Additional Notes

- The workflow file has been updated to include `audience: sts.amazonaws.com` in all AWS credential configuration steps
- Make sure the `permissions` section includes `id-token: write` (already present in your workflow)
- The OIDC provider must be created in the same AWS account (776117903063) where the role exists
