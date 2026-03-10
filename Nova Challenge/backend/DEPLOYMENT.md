# Backend Deployment Guide

## Quick Deployment via AWS Console (Recommended)

### Step 1: Package the Lambda Function

1. Open PowerShell in the `backend` directory
2. Run these commands:

```powershell
# Create package directory if it doesn't exist
New-Item -ItemType Directory -Path package -Force

# Install dependencies
pip install -r requirements.txt -t package/

# Copy main.py
Copy-Item main.py package/

# Create zip file
Compress-Archive -Path package\* -DestinationPath function.zip -Force
```

### Step 2: Deploy via AWS Console

#### Option A: Using CloudFormation (Easiest)

1. Go to AWS CloudFormation Console: https://console.aws.amazon.com/cloudformation/
2. Click "Create stack" → "With new resources"
3. Choose "Upload a template file"
4. Upload `cloudformation-template.yaml`
5. Click "Next"
6. Stack name: `interviewedge-backend`
7. Click "Next" → "Next"
8. Check "I acknowledge that AWS CloudFormation might create IAM resources"
9. Click "Submit"
10. Wait for stack creation (5-10 minutes)
11. Go to "Outputs" tab and copy the **ApiUrl**

#### Update Lambda Code:

1. Go to AWS Lambda Console: https://console.aws.amazon.com/lambda/
2. Find function: `InterviewEdge-API`
3. Click "Upload from" → ".zip file"
4. Upload `function.zip`
5. Click "Save"

#### Option B: Manual Setup (Alternative)

**Create IAM Role:**
1. Go to IAM Console → Roles → Create role
2. Select "Lambda" as trusted entity
3. Attach policies:
   - AWSLambdaBasicExecutionRole
   - AmazonBedrockFullAccess
   - AmazonPollyFullAccess
4. Name: `InterviewEdge-Lambda-Role`

**Create Lambda Function:**
1. Go to Lambda Console → Create function
2. Function name: `InterviewEdge-API`
3. Runtime: Python 3.11
4. Role: Use existing role `InterviewEdge-Lambda-Role`
5. Upload `function.zip`
6. Handler: `main.handler`
7. Timeout: 30 seconds
8. Memory: 512 MB

**Create API Gateway:**
1. Go to API Gateway Console
2. Create HTTP API
3. Name: `InterviewEdge-API`
4. Add integration: Lambda → Select `InterviewEdge-API`
5. Configure CORS:
   - Allow origins: *
   - Allow methods: GET, POST, PUT, DELETE, OPTIONS
   - Allow headers: *
6. Create route: `$default` → Lambda integration
7. Deploy to stage: `$default`
8. Copy the **Invoke URL**

### Step 3: Get Your API URL

After deployment, your API URL will be in one of these places:

**CloudFormation:**
- Go to CloudFormation → Stacks → `interviewedge-backend` → Outputs tab
- Copy the `ApiUrl` value

**API Gateway:**
- Go to API Gateway → APIs → `InterviewEdge-API`
- Copy the "Invoke URL" from the Stages section

**Example URL format:**
```
https://abc123xyz.execute-api.us-east-1.amazonaws.com
```

### Step 4: Test Your API

```powershell
# Test the API
curl https://YOUR-API-URL/
```

You should see: `{"message":"Mock Interview API","status":"running"}`

### Step 5: Update Frontend

Use this API URL in your Amplify environment variables:
- Variable name: `REACT_APP_API_URL`
- Value: Your API Gateway URL (without trailing slash)

## Troubleshooting

**Lambda timeout errors:**
- Increase timeout in Lambda configuration (up to 900 seconds)

**CORS errors:**
- Verify CORS is configured in API Gateway
- Check that frontend is using correct API URL

**Bedrock access denied:**
- Ensure your AWS account has Bedrock access enabled
- Request access in AWS Console → Bedrock → Model access

**Import errors in Lambda:**
- Verify all dependencies are in the zip file
- Check that `main.py` is at the root of the zip

## Cost Estimate

- Lambda: ~$0.20 per 1M requests
- API Gateway: ~$1.00 per 1M requests
- Bedrock Nova: ~$0.0008 per 1K input tokens
- Estimated cost for 1000 interviews: ~$5-10

## Next Steps

1. ✅ Deploy backend (you're here)
2. Get API URL from CloudFormation/API Gateway
3. Configure Amplify with the API URL
4. Deploy frontend via Amplify Console
5. Test the full application
