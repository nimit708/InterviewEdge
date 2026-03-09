# AI Mock Interview Application

A full-stack web application for conducting AI-powered mock interviews with real-time voice interaction.

## Architecture

- **Frontend**: React application with Web Speech API for voice interaction
- **Backend**: FastAPI REST API with AWS Bedrock (Nova models) for AI
- **Hosting**: AWS Amplify for frontend, AWS Lambda for backend

## Features

- Upload CV and job description
- AI-generated interview questions using Amazon Nova
- Voice-based question delivery and answer capture
- Real-time speech-to-text transcription
- Comprehensive feedback generation
- End interview by saying "end the interview"

## Local Development

### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload
```

### Frontend

```bash
cd frontend
npm install
npm start
```

Set environment variable:
```bash
export REACT_APP_API_URL=http://localhost:8000
```

## AWS Amplify Deployment

### Prerequisites

1. AWS Account with Amplify access
2. AWS credentials configured
3. Bedrock access enabled for Nova models

### Deploy Steps

1. **Connect Repository to Amplify**
   - Go to AWS Amplify Console
   - Click "New app" > "Host web app"
   - Connect your Git repository
   - Amplify will detect the `amplify.yml` configuration

2. **Configure Environment Variables**
   - In Amplify Console, go to App Settings > Environment variables
   - Add:
     - `AWS_REGION`: Your AWS region (e.g., us-east-1)
     - `REACT_APP_API_URL`: Your API Gateway URL (after backend deployment)

3. **Deploy Backend to Lambda**
   ```bash
   cd backend
   pip install -r requirements.txt -t package/
   cd package
   zip -r ../function.zip .
   cd ..
   zip -g function.zip main.py
   ```

   Create Lambda function:
   - Runtime: Python 3.11
   - Handler: main.handler
   - Upload function.zip
   - Add API Gateway trigger
   - Set environment variables: AWS_REGION
   - Attach IAM role with Bedrock, Polly, Transcribe permissions

4. **Update Frontend API URL**
   - Copy API Gateway URL
   - Update in Amplify environment variables: `REACT_APP_API_URL`

5. **Deploy**
   - Push to your Git repository
   - Amplify will automatically build and deploy

## AWS IAM Permissions Required

Lambda execution role needs:
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "bedrock:InvokeModel",
        "polly:SynthesizeSpeech",
        "transcribe:StartStreamTranscription"
      ],
      "Resource": "*"
    }
  ]
}
```

## Usage

1. Open the application URL
2. Upload your CV (PDF, DOCX, or TXT)
3. Upload job description
4. Click "Start Interview"
5. Listen to questions and click "Start Recording" to answer
6. Say "end the interview" when finished
7. Review your feedback

## Browser Requirements

- Chrome/Edge (recommended for best speech recognition)
- Firefox (limited speech support)
- Safari (limited speech support)

## Project Structure

```
.
├── backend/
│   ├── main.py              # FastAPI application
│   └── requirements.txt     # Python dependencies
├── frontend/
│   ├── public/
│   │   └── index.html
│   ├── src/
│   │   ├── App.js          # Main React component
│   │   ├── App.css         # Styles
│   │   ├── index.js        # Entry point
│   │   └── index.css
│   └── package.json
├── amplify.yml             # Amplify build configuration
└── README.md
```

## Notes

- Session storage is in-memory (use DynamoDB for production)
- Speech recognition uses browser Web Speech API
- Text-to-speech uses browser SpeechSynthesis API
- For production, implement proper authentication and session persistence
