# Amplify Backend Configuration

## Environment Variables for Amplify

Add these environment variables to your Amplify app configuration:

### Frontend Environment Variables
```
REACT_APP_API_URL=<YOUR_API_GATEWAY_URL>
```

The API Gateway URL will be output after running the deployment script.

## Amplify Build Settings

Update your `amplify.yml` to include the backend API URL:

```yaml
version: 1
frontend:
  phases:
    preBuild:
      commands:
        - npm ci
    build:
      commands:
        - npm run build
  artifacts:
    baseDirectory: build
    files:
      - '**/*'
  cache:
    paths:
      - node_modules/**/*
```

## Backend Integration Steps

1. **Deploy the Backend**
   ```powershell
   cd backend
   .\deploy-complete.ps1
   ```

2. **Get the API URL**
   After deployment completes, the script will output:
   - API Gateway URL
   - Lambda Function ARN
   - Lambda Layer ARN
   
   These will also be saved to `backend/deployment-info.json`

3. **Configure Amplify Environment Variables**
   - Go to AWS Amplify Console
   - Select your app
   - Go to "Environment variables" in the left menu
   - Add: `REACT_APP_API_URL` with the value from deployment

4. **Redeploy Frontend**
   - Amplify will automatically redeploy when you push to your repository
   - Or manually trigger a redeploy from the Amplify Console

## API Endpoints

Your backend will be available at:
```
https://<api-id>.execute-api.eu-west-2.amazonaws.com
```

### Available Endpoints:
- `GET /health` - Health check
- `POST /interview/start` - Start interview session
- `POST /interview/question` - Get next question
- `POST /interview/answer` - Submit answer
- `POST /interview/end` - End interview and get feedback

## CORS Configuration

The API Gateway is configured with CORS to allow:
- All origins (`*`)
- All methods (GET, POST, PUT, DELETE, OPTIONS)
- All headers

For production, update the CloudFormation template to restrict origins to your Amplify domain.

## Monitoring

- **CloudWatch Logs**: Lambda function logs are available in CloudWatch
- **API Gateway Logs**: Enable in API Gateway settings if needed
- **Lambda Metrics**: View in Lambda console (invocations, errors, duration)

## Troubleshooting

If the API is not responding:
1. Check Lambda function logs in CloudWatch
2. Verify IAM role has correct permissions
3. Test Lambda function directly in AWS Console
4. Check API Gateway integration settings

## Cost Optimization

- Lambda: First 1M requests/month are free
- API Gateway: First 1M API calls/month are free
- Consider setting up Lambda reserved concurrency for production
