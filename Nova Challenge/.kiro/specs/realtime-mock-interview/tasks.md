# Implementation Plan: Realtime Mock Interview Application

## Overview

This implementation plan breaks down the realtime mock interview application into discrete coding tasks. The application will be built in Python, leveraging AWS services (Transcribe, Polly, Bedrock for Nova models) and following a modular architecture. Each task builds incrementally, with testing integrated throughout to validate functionality early.

## Tasks

- [ ] 1. Set up project structure and core dependencies
  - Create Python project structure with appropriate directories (src, tests, config)
  - Set up virtual environment and requirements.txt with dependencies: boto3, python-docx, PyPDF2, pytest, hypothesis
  - Create configuration module for AWS credentials and service endpoints
  - Define core data models as Python dataclasses (CVContext, JobContext, InterviewContext, Question, QAPair, SessionState, etc.)
  - _Requirements: All requirements (foundational)_

- [ ] 2. Implement Document Processor
  - [ ] 2.1 Create document parsing functions
    - Implement PDF parsing using PyPDF2
    - Implement DOCX parsing using python-docx
    - Implement plain text parsing
    - Create unified interface that accepts file path and returns raw text
    - _Requirements: 1.1, 1.2, 1.5_
  
  - [ ] 2.2 Implement information extraction
    - Create CV parser that extracts skills, experience, education, certifications using pattern matching and NLP
    - Create job description parser that extracts required skills, responsibilities, qualifications
    - Build InterviewContext by combining CV and job contexts, identifying skill matches and gaps
    - _Requirements: 1.3_
  
  - [ ]* 2.3 Write property test for document extraction
    - **Property 1: Document Extraction Completeness**
    - **Validates: Requirements 1.3**
  
  - [ ] 2.4 Implement error handling for invalid documents
    - Add try-catch blocks for parsing errors
    - Return descriptive error messages for corrupted, unreadable, or invalid format files
    - _Requirements: 1.4_
  
  - [ ]* 2.5 Write property test for invalid document handling
    - **Property 2: Invalid Document Error Handling**
    - **Validates: Requirements 1.4**
  
  - [ ]* 2.6 Write unit tests for document processor
    - Test each document format (PDF, DOCX, TXT) with sample files
    - Test edge cases: empty documents, malformed documents, special characters
    - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5_

- [ ] 3. Implement Speech Interface foundation
  - [ ] 3.1 Create AWS Polly integration for text-to-speech
    - Implement speakText() function using boto3 Polly client
    - Configure voice parameters (voice ID, engine, output format)
    - Handle audio streaming and playback
    - _Requirements: 2.1_
  
  - [ ]* 3.2 Write property test for question-to-speech conversion
    - **Property 3: Question-to-Speech Conversion**
    - **Validates: Requirements 2.1**
  
  - [ ] 3.3 Create AWS Transcribe integration for speech-to-text
    - Implement startListening() and stopListening() functions
    - Integrate with AWS Transcribe streaming API using boto3
    - Implement transcribeSpeech() that returns transcribed text
    - Add voice activity detection to determine when candidate stops speaking
    - _Requirements: 3.1, 3.2, 3.3_
  
  - [ ] 3.4 Implement termination command detection
    - Create detectTerminationCommand() function
    - Match against termination phrases: "end the interview", "stop interview", "finish interview"
    - Use fuzzy matching to handle variations
    - _Requirements: 6.1, 6.4_
  
  - [ ]* 3.5 Write property test for termination detection
    - **Property 17: Termination Command Detection**
    - **Validates: Requirements 6.1, 6.4**
  
  - [ ]* 3.6 Write unit tests for speech interface
    - Test Polly integration with mock AWS responses
    - Test Transcribe integration with mock audio streams
    - Test termination command detection with various phrasings
    - _Requirements: 2.1, 3.1, 3.2, 3.3, 6.1, 6.4_

- [ ] 4. Checkpoint - Ensure document processing and speech interface work
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 5. Implement Session Manager
  - [ ] 5.1 Create session state management
    - Implement initializeSession() that creates SessionState with unique ID
    - Implement getSessionState() for retrieving current state
    - Implement session storage using in-memory dict (can be replaced with Redis/DynamoDB later)
    - Add session TTL handling (24 hours)
    - _Requirements: 5.1, 5.5_
  
  - [ ] 5.2 Implement conversation history tracking
    - Implement recordAnswer() that stores QAPair in session history
    - Ensure conversation history preserves order and completeness
    - Track metadata: question count, duration, topics covered
    - _Requirements: 5.2, 5.3, 5.4_
  
  - [ ]* 5.3 Write property test for session initialization
    - **Property 13: Session Initialization Completeness**
    - **Validates: Requirements 5.1**
  
  - [ ]* 5.4 Write property test for conversation history
    - **Property 14: Conversation History Preservation**
    - **Validates: Requirements 5.3**
  
  - [ ]* 5.5 Write property test for session metadata
    - **Property 15: Session Metadata Tracking**
    - **Validates: Requirements 5.4**
  
  - [ ]* 5.6 Write property test for session state consistency
    - **Property 16: Session State Consistency**
    - **Validates: Requirements 5.5**
  
  - [ ] 5.7 Implement session finalization
    - Implement finalizeSession() that changes status to COMPLETED
    - Generate InterviewTranscript from session state
    - Persist transcript to storage
    - _Requirements: 6.2, 9.3_
  
  - [ ]* 5.8 Write property test for session finalization
    - **Property 18: Session Finalization on Termination**
    - **Validates: Requirements 6.2**
  
  - [ ]* 5.9 Write unit tests for session manager
    - Test session lifecycle: initialization, updates, finalization
    - Test concurrent session handling
    - Test session expiration
    - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5, 6.2_

- [ ] 6. Implement Question Generator with Nova integration
  - [ ] 6.1 Create Amazon Nova API client
    - Set up boto3 Bedrock Runtime client for Nova models
    - Implement callNovaForQuestion() that sends prompts to Nova 2 Sonic
    - Configure model parameters (temperature, max tokens, etc.)
    - Add error handling and retry logic for API calls
    - _Requirements: 8.1, 8.4_
  
  - [ ]* 6.2 Write property test for Nova error handling
    - **Property 22: Nova API Error Handling**
    - **Validates: Requirements 8.4**
  
  - [ ] 6.3 Implement prompt building for question generation
    - Create buildQuestionPrompt() for initial questions using CV and job description
    - Create buildFollowUpPrompt() using conversation history and last answer
    - Create buildNewTopicPrompt() using topics already covered
    - Structure prompts to elicit clear, professional interview questions
    - _Requirements: 4.1, 4.2, 4.3_
  
  - [ ] 6.4 Implement question generation functions
    - Implement generateInitialQuestions() that returns 3-5 starter questions
    - Implement generateFollowUpQuestion() that probes deeper into candidate's last answer
    - Implement generateNextTopicQuestion() that moves to uncovered topics
    - Parse Nova responses into Question objects with proper metadata
    - _Requirements: 4.1, 4.2, 4.3, 4.4_
  
  - [ ]* 6.5 Write property test for Nova context inclusion
    - **Property 10: Nova Context Inclusion for Questions**
    - **Validates: Requirements 4.1, 4.2**
  
  - [ ]* 6.6 Write property test for follow-up relevance
    - **Property 11: Follow-Up Topic Relevance**
    - **Validates: Requirements 4.3**
  
  - [ ]* 6.7 Write property test for question diversity
    - **Property 12: Question Type Diversity**
    - **Validates: Requirements 4.4**
  
  - [ ]* 6.8 Write unit tests for question generator
    - Test prompt construction with various CV and job description inputs
    - Test Nova API integration with mocked responses
    - Test question parsing and metadata assignment
    - _Requirements: 4.1, 4.2, 4.3, 4.4, 8.1, 8.4_

- [ ] 7. Implement Answer Analyzer
  - [ ] 7.1 Create answer storage functions
    - Implement storeAnswer() that creates AnswerRecord with timestamp
    - Ensure answer-question association is maintained
    - Store answers in session-specific storage
    - _Requirements: 3.5, 9.1, 9.2_
  
  - [ ] 7.2 Implement answer analysis functions
    - Create extractKeyPoints() that identifies main topics in answer
    - Create analyzeAnswerQuality() that evaluates relevance and completeness
    - Use simple NLP techniques (keyword extraction, sentence analysis)
    - _Requirements: 4.3_
  
  - [ ]* 7.3 Write property test for answer storage round-trip
    - **Property 9: Answer Storage Round-Trip**
    - **Validates: Requirements 3.5, 9.1**
  
  - [ ]* 7.4 Write property test for answer-question association
    - **Property 23: Answer-Question Association Integrity**
    - **Validates: Requirements 9.2**
  
  - [ ]* 7.5 Write unit tests for answer analyzer
    - Test answer storage and retrieval
    - Test key point extraction with various answer texts
    - Test answer quality analysis
    - _Requirements: 3.5, 9.1, 9.2_

- [ ] 8. Checkpoint - Ensure core components work together
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 9. Implement Feedback Engine
  - [ ] 9.1 Create feedback generation with Nova
    - Implement callNovaForEvaluation() using appropriate Nova model
    - Build evaluation prompt that includes full transcript and job context
    - Parse Nova response into structured FeedbackReport
    - _Requirements: 7.1, 8.2, 8.3_
  
  - [ ] 9.2 Implement performance evaluation functions
    - Create evaluatePerformance() that scores across multiple dimensions
    - Create identifyStrengths() that extracts positive aspects with examples
    - Create identifyImprovements() that provides actionable recommendations
    - Create summarizePerformance() that generates overall summary
    - _Requirements: 7.2, 7.3, 7.4, 7.6_
  
  - [ ]* 9.3 Write property test for feedback generation trigger
    - **Property 19: Feedback Generation Trigger**
    - **Validates: Requirements 6.3, 7.1**
  
  - [ ]* 9.4 Write property test for feedback completeness
    - **Property 20: Feedback Structure Completeness**
    - **Validates: Requirements 7.2, 7.3, 7.4, 7.6**
  
  - [ ] 9.5 Implement dual-format feedback delivery
    - Create formatFeedbackAsText() that generates readable text report
    - Create formatFeedbackAsSpeech() that generates speech-friendly summary
    - Integrate with Speech Interface to deliver spoken feedback
    - _Requirements: 7.5_
  
  - [ ]* 9.6 Write property test for dual-format delivery
    - **Property 21: Dual-Format Feedback Delivery**
    - **Validates: Requirements 7.5**
  
  - [ ]* 9.7 Write unit tests for feedback engine
    - Test feedback generation with mock Nova responses
    - Test performance evaluation with various transcripts
    - Test strength and improvement identification
    - Test dual-format output
    - _Requirements: 7.1, 7.2, 7.3, 7.4, 7.5, 7.6, 8.2, 8.3_

- [ ] 10. Implement interview orchestration and state management
  - [ ] 10.1 Create interview flow controller
    - Implement main interview loop that coordinates all components
    - Handle state transitions: INIT -> ASKING -> LISTENING -> ANALYZING -> ASKING (loop) -> COMPLETED
    - Implement shouldAskFollowUp() decision logic based on answer analysis
    - Implement requestNextQuestion() that calls appropriate question generation function
    - _Requirements: 5.2, 2.4_
  
  - [ ] 10.2 Implement speech state blocking
    - Ensure system doesn't accept input while in ASKING state (speaking question)
    - Transition to LISTENING state only after speech completion
    - _Requirements: 2.3_
  
  - [ ]* 10.3 Write property test for speech state blocking
    - **Property 4: Speech State Blocking**
    - **Validates: Requirements 2.3**
  
  - [ ]* 10.4 Write property test for sequential delivery
    - **Property 5: Sequential Question Delivery**
    - **Validates: Requirements 2.4**
  
  - [ ]* 10.5 Write property test for listening state activation
    - **Property 6: Listening State Activation**
    - **Validates: Requirements 3.1**
  
  - [ ]* 10.6 Write property test for continuous capture
    - **Property 7: Continuous Audio Capture**
    - **Validates: Requirements 3.2**
  
  - [ ]* 10.7 Write unit tests for interview orchestration
    - Test state transitions
    - Test decision logic for follow-ups vs new topics
    - Test complete interview flow with mocked components
    - _Requirements: 2.3, 2.4, 3.1, 3.2, 5.2_

- [ ] 11. Implement comprehensive error handling
  - [ ] 11.1 Add speech processing error handling
    - Handle STT failures with retry and user notification
    - Handle audio capture failures with clear error messages
    - Implement fallback to text input if speech fails repeatedly
    - _Requirements: 3.4, 10.1, 10.3_
  
  - [ ]* 11.2 Write property test for STT failure recovery
    - **Property 8: Speech-to-Text Failure Recovery**
    - **Validates: Requirements 3.4**
  
  - [ ] 11.3 Add Nova API error handling with retry
    - Implement exponential backoff retry logic (1s, 2s, 4s, max 3 attempts)
    - Handle rate limiting, timeouts, and service unavailability
    - Inform user and save state if errors persist
    - _Requirements: 8.4, 10.2_
  
  - [ ] 11.4 Implement critical error recovery
    - Save session state before critical operations
    - Implement checkpoint after each Q&A pair
    - Enable session resumption after critical errors
    - _Requirements: 10.4_
  
  - [ ]* 11.5 Write property test for error state preservation
    - **Property 25: Error Recovery with State Preservation**
    - **Validates: Requirements 10.4**
  
  - [ ]* 11.6 Write property test for error notification
    - **Property 26: Error Notification Consistency**
    - **Validates: Requirements 10.1, 10.2, 10.3**
  
  - [ ]* 11.7 Write unit tests for error handling
    - Test retry logic with various failure scenarios
    - Test state preservation on errors
    - Test graceful degradation (TTS fails -> text only, etc.)
    - Test error message clarity
    - _Requirements: 3.4, 8.4, 10.1, 10.2, 10.3, 10.4_

- [ ] 12. Implement transcript storage and retrieval
  - [ ] 12.1 Create transcript persistence
    - Implement transcript storage (file-based or database)
    - Store complete InterviewTranscript with all Q&A pairs
    - Ensure transcript preserves all data throughout session
    - _Requirements: 9.3, 9.4_
  
  - [ ]* 12.2 Write property test for transcript completeness
    - **Property 24: Complete Transcript Preservation**
    - **Validates: Requirements 9.3, 9.4**
  
  - [ ]* 12.3 Write unit tests for transcript storage
    - Test transcript save and load
    - Test transcript completeness
    - Test concurrent access handling
    - _Requirements: 9.3, 9.4_

- [ ] 13. Create main application entry point and CLI
  - [ ] 13.1 Build command-line interface
    - Create main.py with argument parsing for CV and job description file paths
    - Implement application initialization that sets up all components
    - Wire together all components: DocumentProcessor -> SessionManager -> QuestionGenerator -> SpeechInterface -> AnswerAnalyzer -> FeedbackEngine
    - Add logging configuration for debugging and monitoring
    - _Requirements: All requirements (integration)_
  
  - [ ] 13.2 Implement graceful shutdown
    - Handle keyboard interrupts (Ctrl+C)
    - Save session state on unexpected termination
    - Clean up resources (close audio streams, API connections)
    - _Requirements: 10.4_
  
  - [ ]* 13.3 Write integration tests
    - Test end-to-end flow from document input to feedback delivery
    - Test termination at various points in interview
    - Test session resumption after errors
    - Use recorded audio samples for reproducible tests
    - _Requirements: All requirements_

- [ ] 14. Final checkpoint - Complete system validation
  - Run all unit tests and property tests
  - Perform manual end-to-end testing with real CV and job description
  - Verify AWS service integrations work correctly
  - Ensure all tests pass, ask the user if questions arise.

## Notes

- Tasks marked with `*` are optional and can be skipped for faster MVP
- Each task references specific requirements for traceability
- Property tests validate universal correctness properties from the design document
- Unit tests validate specific examples, edge cases, and integration points
- AWS credentials must be configured before running (via environment variables or AWS CLI)
- Consider using moto library for mocking AWS services in tests
- The implementation uses Python with boto3 for AWS integration
- Consider adding a web interface later for better user experience
