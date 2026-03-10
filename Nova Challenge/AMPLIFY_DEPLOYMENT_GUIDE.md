# InterviewEdge - Amplify Deployment Guide

## Backend Deployment Summary

✅ **Deployment Status**: COMPLETE

### Deployed Resources

**API Gateway URL:**
```
https://c2kxx0qry9.execute-api.eu-west-2.amazonaws.com
```

**Lambda Function:**
- Name: `InterviewEdge-API`
- ARN: `arn:aws:lambda:eu-west-2:923906573163:function:InterviewEdge-API`
- Runtime: Python 3.11
- Region: eu-west-2

**Lambda Layer:**
- ARN: `arn:aws:lambda:eu-west-2:923906573163:layer:interview-edge-dependencies:1`
- Contains: boto3, click, colorama, and other Python dependencies

**CloudFormation Stack:**
- Name: `InterviewEdge-Backend`
- Status: CREATE_COMPLETE
- Region: eu-west-2

---

## Amplify Configuration Steps

### 1. Configure Environment Variables

Go to your Amplify Console and add the following environment variable:

**Environment Variables:**
```
REACT_APP_API_URL=https://c2kxx0qry9.execute-api.eu-west-2.amazonaws.com
```

**Steps:**
1. Open AWS Amplify Console
2. Select your app: `InterviewEdge`
3. Go to **App settings** > **Environment variables**
4. Click **Manage variables**
5. Add new variable:
   - Key: `REACT_APP_API_URL`
   - Value: `https://c2kxx0qry9.execute-api.eu-west-2.amazonaws.com`
6. Click **Save**

### 2. Verify amplify.yml Configuration

Your `amplify.yml` is already configured correctly:

```yaml
version: 1
applications:
  - frontend:
      phases:
        preBuild:
          commands:
            - cd frontend
            - npm ci
        build:
          commands:
            - npm run build
      artifacts:
        baseDirectory: frontend/build
        files:
          - '**/*'
      cache:
        paths:
          - frontend/node_modules/**/*
    appRoot: frontend
```

### 3. Redeploy Frontend

After adding the environment variable:

**Option A: Automatic (Recommended)**
- Push any change to your connected Git repository
- Amplify will automatically rebuild with the new environment variable

**Option B: Manual**
1. Go to Amplify Console
2. Click **Run build** or **Redeploy this version**
3. Wait for the build to complete

### 4. Test the Integration

Once deployed, test your application:

1. Open your Amplify app URL
2. Try the interview features
3. Check browser console for any API errors
4. Verify API calls are going to: `https://c2kxx0qry9.execute-api.eu-west-2.amazonaws.com`

---

## API Endpoints

Your backend exposes the following endpoints:

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Health check endpoint |
| POST | `/interview/start` | Start a new interview session |
| POST | `/interview/question` | Get next interview question |
| POST | `/interview/answer` | Submit candidate answer |
| POST | `/interview/end` | End interview and get feedback |

---

## CORS Configuration

The API Gateway is configured with CORS to allow:
- **Origins**: `*` (all origins)
- **Methods**: GET, POST, PUT, DELETE, OPTIONS
- **Headers**: `*` (all headers)

**For Production**: Update the CloudFormation template to restrict origins to your Amplify domain only.

---

## Monitoring & Debugging

### CloudWatch Logs
- Lambda function logs: [CloudWatch Logs Console](https://eu-west-2.console.aws.amazon.com/cloudwatch/home?region=eu-west-2#logsV2:log-groups/log-group/$252Faws$252Flambda$252FInterviewEdge-API)

### Lambda Console
- Function details: [Lambda Console](https://eu-west-2.console.aws.amazon.com/lambda/home?region=eu-west-2#/functions/InterviewEdge-API)

### API Gateway Console
- API details: [API Gateway Console](https://eu-west-2.console.aws.amazon.com/apigateway/main/apis?region=eu-west-2)

---

## Updating the Backend

To update the Lambda function code:

```powershell
cd backend
powershell -ExecutionPolicy Bypass -File deploy-complete.ps1
```

This will:
1. Update the CloudFormation stack (if template changed)
2. Republish the Lambda layer (if dependencies changed)
3. Update the Lambda function code
4. Attach the latest layer version

---

## Cost Optimization

**Current Configuration:**
- Lambda: 512 MB memory, 30s timeout
- API Gateway: HTTP API (cheaper than REST API)
- Layer: Shared dependencies (reduces deployment package size)

**Free Tier Coverage:**
- Lambda: First 1M requests/month free
- API Gateway: First 1M API calls/month free
- CloudWatch Logs: 5GB ingestion free

**Estimated Monthly Cost (beyond free tier):**
- ~$0.20 per 1M requests (Lambda)
- ~$1.00 per 1M requests (API Gateway)

---

## Troubleshooting

### Issue: API returns 502 Bad Gateway
**Solution**: Check Lambda function logs in CloudWatch for errors

### Issue: CORS errors in browser
**Solution**: Verify API Gateway CORS configuration allows your Amplify domain

### Issue: Lambda timeout
**Solution**: Increase timeout in CloudFormation template (currently 30s)

### Issue: Missing dependencies
**Solution**: Redeploy the Lambda layer with updated requirements.txt

---

## Security Recommendations

1. **Restrict CORS**: Update CloudFormation to allow only your Amplify domain
2. **Add Authentication**: Integrate AWS Cognito for user authentication
3. **API Keys**: Add API Gateway API keys for rate limiting
4. **IAM Roles**: Review Lambda execution role permissions
5. **Encryption**: Enable encryption at rest for sensitive data

---

## Next Steps

1. ✅ Backend deployed successfully
2. ⏳ Configure Amplify environment variables
3. ⏳ Redeploy frontend with new API URL
4. ⏳ Test end-to-end integration
5. ⏳ Implement authentication (optional)
6. ⏳ Add monitoring and alerts

---

## Support Files

- **Deployment Info**: `backend/deployment-info.json`
- **API URL**: `backend/api-url.txt`
- **CloudFormation Template**: `backend/cloudformation-template.yaml`
- **Lambda Code**: `backend/main.py`

---

**Deployment Date**: $(Get-Date)
**Region**: eu-west-2
**Stack Status**: CREATE_COMPLETE
