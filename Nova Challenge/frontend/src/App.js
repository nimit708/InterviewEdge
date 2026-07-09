import React, { useState, useRef } from 'react';
import axios from 'axios';
import './App.css';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

function App() {
  const [sessionId, setSessionId] = useState(null);
  const [currentQuestion, setCurrentQuestion] = useState(null);
  const [isRecording, setIsRecording] = useState(false);
  const [transcript, setTranscript] = useState('');
  const [feedback, setFeedback] = useState(null);
  const [status, setStatus] = useState('idle');
  const [errorMessage, setErrorMessage] = useState('');
  
  const cvFileRef = useRef(null);
  const jobFileRef = useRef(null);
  const recognitionRef = useRef(null);

  const startSession = async () => {
    const cvFile = cvFileRef.current.files[0];
    const jobFile = jobFileRef.current.files[0];
    
    if (!cvFile || !jobFile) {
      alert('Please upload both CV and Job Description');
      return;
    }

    const formData = new FormData();
    formData.append('cv', cvFile);
    formData.append('job_desc', jobFile);

    try {
      setStatus('starting');
      const response = await axios.post(`${API_URL}/api/session/start`, formData);
      setSessionId(response.data.session_id);
      setStatus('ready');
      await getNextQuestion(response.data.session_id);
    } catch (error) {
      console.error('Failed to start session:', error);
      alert('Failed to start session');
      setStatus('idle');
    }
  };

  const getNextQuestion = async (sid) => {
    try {
      setStatus('generating');
      const response = await axios.post(`${API_URL}/api/question/generate/${sid || sessionId}`);
      setCurrentQuestion(response.data.question);
      setStatus('question_ready');
      speakQuestion(response.data.question.text);
    } catch (error) {
      console.error('Failed to generate question:', error);
      alert('Failed to generate question');
    }
  };

  const speakQuestion = (text) => {
    if ('speechSynthesis' in window) {
      const utterance = new SpeechSynthesisUtterance(text);
      utterance.onend = () => {
        setStatus('listening');
      };
      window.speechSynthesis.speak(utterance);
    } else {
      setStatus('listening');
    }
  };

  const startRecording = () => {
    if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
      alert('Speech recognition not supported in this browser');
      return;
    }

    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    const recognition = new SpeechRecognition();
    
    recognition.continuous = true;
    recognition.interimResults = true;
    recognition.lang = 'en-US';

    recognition.onresult = (event) => {
      let interimTranscript = '';
      let finalTranscript = '';

      for (let i = event.resultIndex; i < event.results.length; i++) {
        const transcript = event.results[i][0].transcript;
        if (event.results[i].isFinal) {
          finalTranscript += transcript + ' ';
        } else {
          interimTranscript += transcript;
        }
      }

      setTranscript(finalTranscript || interimTranscript);
    };

    recognition.onerror = (event) => {
      console.error('Speech recognition error:', event.error);
    };

    recognition.start();
    recognitionRef.current = recognition;
    setIsRecording(true);
    setStatus('recording');
  };

  const stopRecording = async () => {
    if (recognitionRef.current) {
      recognitionRef.current.stop();
      setIsRecording(false);
      setErrorMessage('');

      if (transcript && transcript.trim()) {
        setStatus('processing');
        if (transcript.toLowerCase().includes('end the interview')) {
          await endInterview();
        } else {
          await submitAnswer();
        }
      } else {
        setErrorMessage('No speech was detected. Please try recording again.');
        setStatus('submit_failed');
      }
    }
  };

  const reRecord = () => {
    if (recognitionRef.current) {
      recognitionRef.current.stop();
    }
    setIsRecording(false);
    setTranscript('');
    setErrorMessage('');
    setStatus('listening');
  };

  const submitAnswer = async () => {
    if (!transcript || !transcript.trim()) {
      setErrorMessage('No answer was recorded. Please try recording again.');
      setStatus('submit_failed');
      return;
    }

    try {
      setStatus('processing');
      await axios.post(`${API_URL}/api/answer/submit/${sessionId}`, null, {
        params: {
          question_id: currentQuestion.question_id,
          answer_text: transcript.trim()
        }
      });
      setTranscript('');
      setErrorMessage('');
      await getNextQuestion();
    } catch (error) {
      console.error('Failed to submit answer:', error);
      if (error.response && error.response.status === 400) {
        setErrorMessage('Answer cannot be blank. Please re-record your answer.');
      } else {
        setErrorMessage('Failed to submit answer. Please try again.');
      }
      setStatus('submit_failed');
    }
  };

  const endInterview = async () => {
    try {
      setStatus('ending');
      const response = await axios.post(`${API_URL}/api/session/end/${sessionId}`);
      setFeedback(response.data.feedback);
      setStatus('completed');
    } catch (error) {
      console.error('Failed to end interview:', error);
      alert('Failed to end interview');
    }
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>AI Mock Interview</h1>
      </header>

      <main className="App-main">
        {status === 'idle' && (
          <div className="upload-section">
            <h2>Start Your Interview</h2>

            <div className="privacy-notice">
              🔒 Your data is never stored. Files and answers exist only for the duration of your session and are discarded immediately after.
            </div>

            <div className="file-input">
              <label>Upload CV (PDF, DOCX or TXT):</label>
              <input type="file" ref={cvFileRef} accept=".txt,.pdf,.docx" />
            </div>
            <div className="file-input">
              <label>Upload Job Description (PDF, DOCX or TXT):</label>
              <input type="file" ref={jobFileRef} accept=".txt,.pdf,.docx" />
              <p className="file-hint">
                💡 Tip: Open the job posting in your browser, press <strong>Ctrl+P</strong> (or <strong>Cmd+P</strong> on Mac) and choose <strong>"Save as PDF"</strong> to download it.
              </p>
            </div>
            <button onClick={startSession} className="btn-primary">
              Start Interview
            </button>
          </div>
        )}

        {status === 'starting' && <div className="status">Initializing interview...</div>}
        {status === 'generating' && <div className="status">Generating question...</div>}

        {currentQuestion && status !== 'completed' && (
          <div className="interview-section">
            <div className="question-box">
              <h3>Question:</h3>
              <p>{currentQuestion.text}</p>
            </div>

            {status === 'listening' && !isRecording && (
              <div className="action-buttons">
                <button onClick={startRecording} className="btn-record">
                  Start Recording Answer
                </button>
                <button onClick={endInterview} className="btn-end">
                  End Interview &amp; Get Feedback
                </button>
              </div>
            )}

            {isRecording && (
              <div className="recording-section">
                <div className="recording-indicator">🔴 Recording...</div>
                <p className="transcript">{transcript}</p>
                <button onClick={stopRecording} className="btn-stop">
                  Stop &amp; Submit Answer
                </button>
                <button onClick={reRecord} className="btn-rerecord">
                  🔄 Re-record
                </button>

              </div>
            )}

            {status === 'processing' && <div className="status">Processing your answer...</div>}

            {status === 'submit_failed' && (
              <div className="error-section">
                <div className="error-message">⚠️ {errorMessage}</div>
                <div className="action-buttons">
                  <button onClick={reRecord} className="btn-record">
                    🎙️ Re-record Answer
                  </button>
                  <button onClick={endInterview} className="btn-end">
                    End Interview &amp; Get Feedback
                  </button>
                </div>
              </div>
            )}
          </div>
        )}

        {status === 'completed' && feedback && (
          <div className="feedback-section">
            <h2>Interview Feedback</h2>
            <div className="feedback-content">
              <pre>{feedback}</pre>
            </div>
            <button onClick={() => window.location.reload()} className="btn-primary">
              Start New Interview
            </button>
          </div>
        )}
      </main>
    </div>
  );
}

export default App;
