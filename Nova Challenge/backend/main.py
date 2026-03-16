from fastapi import FastAPI, WebSocket, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from mangum import Mangum
import json
import uuid
from datetime import datetime
from typing import Dict, List
import boto3
from dataclasses import dataclass, asdict
import os
import io

app = FastAPI()

# CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# AWS clients
bedrock = boto3.client('bedrock-runtime', region_name=os.getenv('AWS_REGION', 'eu-west-2'))
polly = boto3.client('polly', region_name=os.getenv('AWS_REGION', 'eu-west-2'))
transcribe = boto3.client('transcribe', region_name=os.getenv('AWS_REGION', 'eu-west-2'))

# In-memory session storage (use DynamoDB for production)
sessions: Dict[str, dict] = {}

@dataclass
class Question:
    question_id: str
    text: str
    type: str
    timestamp: str

@dataclass
class Answer:
    answer_id: str
    question_id: str
    text: str
    timestamp: str

@app.get("/")
async def root():
    return {"message": "Mock Interview API", "status": "running"}

def extract_text(content: bytes, filename: str) -> str:
    """Extract text from txt, pdf, or docx files"""
    ext = filename.lower().rsplit('.', 1)[-1] if '.' in filename else ''

    if ext == 'pdf':
        try:
            import PyPDF2
            reader = PyPDF2.PdfReader(io.BytesIO(content))
            return "\n".join(page.extract_text() or '' for page in reader.pages).strip()
        except Exception as e:
            return f"[PDF parse error: {str(e)}]"

    elif ext == 'docx':
        try:
            import docx
            doc = docx.Document(io.BytesIO(content))
            return "\n".join(p.text for p in doc.paragraphs if p.text.strip())
        except Exception as e:
            return f"[DOCX parse error: {str(e)}]"

    else:
        try:
            return content.decode('utf-8')
        except UnicodeDecodeError:
            return content.decode('latin-1', errors='replace')

@app.post("/api/session/start")
async def start_session(cv: UploadFile = File(...), job_desc: UploadFile = File(...)):
    """Initialize interview session with CV and job description"""
    try:
        session_id = str(uuid.uuid4())
        
        # Read and parse file content
        cv_content = await cv.read()
        job_content = await job_desc.read()

        cv_text = extract_text(cv_content, cv.filename or 'cv.txt')
        job_text = extract_text(job_content, job_desc.filename or 'job.txt')
        
        sessions[session_id] = {
            "session_id": session_id,
            "cv_context": cv_text,
            "job_context": job_text,
            "questions": [],
            "answers": [],
            "status": "ACTIVE",
            "start_time": datetime.now().isoformat()
        }
        
        return {"session_id": session_id, "status": "initialized"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/session/{session_id}")
async def get_session(session_id: str):
    """Get session state"""
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    return sessions[session_id]

@app.post("/api/question/generate/{session_id}")
async def generate_question(session_id: str):
    """Generate next interview question using Nova"""
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session = sessions[session_id]
    
    # Build prompt for Nova
    previous_qs = "\n".join(f"- {q['text']}" for q in session['questions']) if session['questions'] else "None yet"
    prompt = f"""You are conducting a job interview.
CV Summary: {session['cv_context'][:500]}
Job Description: {session['job_context'][:500]}

Questions already asked (do NOT repeat or ask anything similar to these):
{previous_qs}

Generate ONE new interview question that is different from all the above. Cover a different topic or skill each time. Return only the question text, nothing else."""
    
    try:
        response = bedrock.invoke_model(
            modelId='amazon.nova-lite-v1:0',
            body=json.dumps({
                "messages": [{"role": "user", "content": [{"text": prompt}]}],
                "inferenceConfig": {"temperature": 0.7, "maxTokens": 200}
            })
        )
        
        result = json.loads(response['body'].read())
        question_text = result['output']['message']['content'][0]['text'].strip()
        
        question = Question(
            question_id=str(uuid.uuid4()),
            text=question_text,
            type="TECHNICAL",
            timestamp=datetime.now().isoformat()
        )
        
        session['questions'].append(asdict(question))
        
        return {"question": asdict(question)}
    except Exception as e:
        import traceback
        error_detail = f"Question generation failed: {str(e)}\nTraceback: {traceback.format_exc()}"
        print(error_detail)  # This will appear in CloudWatch logs
        raise HTTPException(status_code=500, detail=error_detail)

@app.post("/api/answer/submit/{session_id}")
async def submit_answer(session_id: str, question_id: str, answer_text: str):
    """Submit answer for a question"""
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session = sessions[session_id]
    
    answer = Answer(
        answer_id=str(uuid.uuid4()),
        question_id=question_id,
        text=answer_text,
        timestamp=datetime.now().isoformat()
    )
    
    session['answers'].append(asdict(answer))
    
    return {"answer": asdict(answer), "status": "recorded"}

@app.post("/api/session/end/{session_id}")
async def end_session(session_id: str):
    """End interview and generate feedback"""
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session = sessions[session_id]
    session['status'] = "COMPLETED"
    session['end_time'] = datetime.now().isoformat()
    
    # Only include questions that were actually answered
    answered_questions = [
        q for q in session['questions']
        if any(a['question_id'] == q['question_id'] for a in session['answers'])
    ]

    if not answered_questions:
        return {"feedback": "No answers were recorded in this session. Please complete at least one question to receive feedback.", "transcript": ""}

    # Generate feedback using Nova
    transcript = "\n".join([
        f"Q: {q['text']}\nA: {next(a['text'] for a in session['answers'] if a['question_id'] == q['question_id'])}"
        for q in answered_questions
    ])
    
    prompt = f"""You are evaluating a mock job interview for the following role:

Job Description: {session['job_context'][:400]}

Interview transcript:
{transcript}

Important: The answers were captured via speech-to-text so they may lack punctuation or have minor transcription errors. Judge the substance and relevance of what was said, not the formatting or grammar.

The candidate answered {len(answered_questions)} question(s). Only evaluate the answers provided above.

Provide constructive feedback with:
1. Overall assessment
2. Strengths (2-3 points)
3. Areas for improvement (2-3 points)
4. Overall score (0-100)"""
    
    try:
        response = bedrock.invoke_model(
            modelId='amazon.nova-lite-v1:0',
            body=json.dumps({
                "messages": [{"role": "user", "content": [{"text": prompt}]}],
                "inferenceConfig": {"temperature": 0.7, "maxTokens": 500}
            })
        )
        
        result = json.loads(response['body'].read())
        feedback_text = result['output']['message']['content'][0]['text']
        
        session['feedback'] = feedback_text
        
        return {"feedback": feedback_text, "transcript": transcript}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Feedback generation failed: {str(e)}")

@app.post("/api/speech/synthesize")
async def synthesize_speech(text: str):
    """Convert text to speech using AWS Polly"""
    try:
        response = polly.synthesize_speech(
            Text=text,
            OutputFormat='mp3',
            VoiceId='Joanna',
            Engine='neural'
        )
        
        audio_stream = response['AudioStream'].read()
        return {"audio": audio_stream.hex(), "format": "mp3"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Speech synthesis failed: {str(e)}")

# Lambda handler for AWS Amplify
handler = Mangum(app)
