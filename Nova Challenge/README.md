# InterviewEdge - AI Mock Interview

A full-stack web application for conducting AI-powered mock interviews with real-time voice interaction. No data is stored - everything is processed in-memory and discarded at the end of your session.

## Architecture

```
User Browser
    │
    │  Upload CV + Job Description (PDF/DOCX/TXT)
    ▼
AWS Amplify (React Frontend)
    │
    │  REST API calls (HTTPS)
    ▼
Amazon API Gateway
    │
    │  Proxy
    ▼
AWS Lambda (FastAPI via Mangum)
    │
    ├──► Amazon Bedrock (Nova Lite) ── generates interview questions & feedback
    └──► AWS Polly (optional)       ── text-to-speech for questions
```

### How it works

1. User uploads their CV and a job description via the browser
2. The frontend sends both files to API Gateway as a multipart form POST
3. Lambda receives the files, extracts text (supports PDF, DOCX, TXT) and stores it in-memory for the session
4. For each question, Lambda calls Amazon Bedrock (Nova Lite model) with the CV, job description, and all previously asked questions - so Nova never repeats itself
5. The browser reads the question aloud using the Web Speech API and records the user's spoken answer via speech-to-text
6. At the end, Lambda sends the full interview transcript to Nova to generate personalised feedback
7. When the Lambda container is recycled, all session data is gone - nothing is persisted

### Privacy

- CV and job description files are never written to disk or any storage service
- Session data (extracted text, questions, answers) lives only in Lambda memory
- No database, no S3, no logging of user content
- Data exists only for the duration of a single interview session

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | React, Web Speech API, Axios |
| Hosting | AWS Amplify |
| API | Amazon API Gateway (HTTP) |
| Backend | Python, FastAPI, Mangum |
| Compute | AWS Lambda (Python 3.11) |
| AI | Amazon Bedrock - Nova Lite (`amazon.nova-lite-v1:0`) |
| File parsing | PyPDF2, python-docx |

## Features

- Upload CV and job description (PDF, DOCX or TXT)
- AI-generated interview questions tailored to your CV and the role
- No repeated questions - Nova tracks what's been asked each session
- Voice question delivery via browser speech synthesis
- Voice answer capture via browser speech recognition
- Re-record button to redo an answer before submitting
- Personalised feedback at the end of the interview
- Say "end the interview" at any time to finish and get feedback

## Local Development

### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload
```

### Frontend

```bash
cd frontend
npm install
```

Create `frontend/.env`:
```
REACT_APP_API_URL=http://localhost:8000
```

Then run:
```bash
npm start
```

## Deployment

### Backend (Lambda)

1. Build a Linux-compatible layer:
```powershell
cd backend
.\build-layer-linux.ps1
```

2. Publish the layer:
```bash
aws lambda publish-layer-version \
  --layer-name interview-edge-dependencies \
  --zip-file fileb://layer.zip \
  --compatible-runtimes python3.11 \
  --region eu-west-2
```

3. Deploy function code:
```bash
zip function.zip main.py
aws lambda update-function-code \
  --function-name InterviewEdge-API \
  --zip-file fileb://function.zip \
  --region eu-west-2
```

### Frontend (Amplify)

Push to the connected Git branch - Amplify rebuilds automatically.

Set the following environment variable in Amplify Console (App Settings > Environment variables):
- `REACT_APP_API_URL` - your API Gateway URL

## IAM Permissions

The Lambda execution role needs:

```json
{
  "Effect": "Allow",
  "Action": [
    "bedrock:InvokeModel",
    "polly:SynthesizeSpeech"
  ],
  "Resource": "*"
}
```

## Usage

1. Open the app URL
2. Upload your CV (PDF, DOCX or TXT)
3. For the job description, open the job posting in your browser, press `Ctrl+P` → Save as PDF
4. Click "Start Interview"
5. Listen to each question, then click "Start Recording Answer"
6. Use "Re-record" if you want to redo your answer
7. Say "end the interview" or finish answering to get your feedback

## Browser Support

- Chrome / Edge - full support (recommended)
- Firefox / Safari - limited speech recognition support

## Project Structure

```
.
├── backend/
│   ├── main.py              # FastAPI app - session, question generation, feedback
│   ├── requirements.txt     # Python dependencies
│   └── build-layer-linux.ps1 # Builds Lambda layer for Linux x86_64
├── frontend/
│   └── src/
│       ├── App.js           # Main React component
│       └── App.css          # Styles
└── amplify.yml              # Amplify build config
```
