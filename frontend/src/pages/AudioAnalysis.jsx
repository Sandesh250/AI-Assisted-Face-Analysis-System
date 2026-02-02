import { useState, useCallback, useRef } from 'react';
import { useDropzone } from 'react-dropzone';
import { FaMicrophone, FaUpload, FaPlay, FaSpinner, FaUser, FaSearch, FaStop, FaCircle } from 'react-icons/fa';
import { analyzeFromAudio, analyzeFromText } from '../services/api';

function AudioAnalysis() {
    const [inputMode, setInputMode] = useState('audio'); // 'audio' or 'text'
    const [textDescription, setTextDescription] = useState('');
    const [file, setFile] = useState(null);
    const [loading, setLoading] = useState(false);
    const [step, setStep] = useState('');
    const [results, setResults] = useState(null);
    const [error, setError] = useState(null);
    const [generateSketch, setGenerateSketch] = useState(true); // Default ON for sketch generation

    // Recording state
    const [isRecording, setIsRecording] = useState(false);
    const [recordingTime, setRecordingTime] = useState(0);
    const [audioURL, setAudioURL] = useState(null);
    const mediaRecorderRef = useRef(null);
    const audioChunksRef = useRef([]);
    const timerRef = useRef(null);

    const onDrop = useCallback((acceptedFiles) => {
        if (acceptedFiles.length > 0) {
            setFile(acceptedFiles[0]);
            setAudioURL(URL.createObjectURL(acceptedFiles[0]));
            setResults(null);
            setError(null);
        }
    }, []);

    const { getRootProps, getInputProps, isDragActive } = useDropzone({
        onDrop,
        accept: {
            'audio/*': ['.wav', '.mp3', '.m4a', '.flac', '.ogg']
        },
        maxFiles: 1,
        noClick: isRecording
    });

    // Start recording
    const startRecording = async () => {
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            mediaRecorderRef.current = new MediaRecorder(stream, { mimeType: 'audio/webm' });
            audioChunksRef.current = [];

            mediaRecorderRef.current.ondataavailable = (event) => {
                audioChunksRef.current.push(event.data);
            };

            mediaRecorderRef.current.onstop = () => {
                const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/webm' });
                const audioFile = new File([audioBlob], 'recording.webm', { type: 'audio/webm' });
                setFile(audioFile);
                setAudioURL(URL.createObjectURL(audioBlob));

                // Stop all tracks
                stream.getTracks().forEach(track => track.stop());
            };

            mediaRecorderRef.current.start(100);
            setIsRecording(true);
            setRecordingTime(0);
            setResults(null);
            setError(null);

            // Start timer
            timerRef.current = setInterval(() => {
                setRecordingTime(prev => prev + 1);
            }, 1000);

        } catch (err) {
            setError('Failed to access microphone. Please allow microphone access.');
            console.error('Recording error:', err);
        }
    };

    // Stop recording
    const stopRecording = () => {
        if (mediaRecorderRef.current && isRecording) {
            mediaRecorderRef.current.stop();
            setIsRecording(false);
            clearInterval(timerRef.current);
        }
    };

    // Format time as MM:SS
    const formatTime = (seconds) => {
        const mins = Math.floor(seconds / 60);
        const secs = seconds % 60;
        return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
    };

    const runAnalysis = async () => {
        if (inputMode === 'audio' && !file) {
            setError('Please record or upload an audio file');
            return;
        }
        if (inputMode === 'text' && !textDescription.trim()) {
            setError('Please enter a description');
            return;
        }

        setLoading(true);
        setError(null);

        try {
            if (inputMode === 'audio') {
                setStep(generateSketch ? 'Transcribing & generating sketch (may take several minutes first time)...' : 'Transcribing audio...');
                const result = await analyzeFromAudio(file, generateSketch, 5);
                setResults(result);
            } else {
                setStep(generateSketch ? 'Generating sketch from description...' : 'Processing description...');
                const result = await analyzeFromText(textDescription, generateSketch, 5);
                setResults(result);
            }
            setStep('');
        } catch (err) {
            setError(err.response?.data?.detail || err.message || 'Analysis failed');
        } finally {
            setLoading(false);
        }
    };


    return (
        <div className="audio-analysis animate-fade-in">
            <div className="page-header">
                <h1><FaMicrophone /> Audio Description Analysis</h1>
                <p>
                    Record or upload a voice description of a person. The AI will transcribe it,
                    extract facial attributes, and generate a composite sketch.
                </p>
            </div>

            <div className="disclaimer-banner">
                <p>⚠️ Generated sketches are AI interpretations, not accurate representations. For educational purposes only.</p>
            </div>

            <div className="analysis-layout">
                {/* Upload Panel */}
                <div className="analysis-panel">
                    <div className="panel-header">
                        <div className="panel-icon"><FaMicrophone /></div>
                        <h3 className="panel-title">Input Description</h3>
                    </div>

                    {/* Input Mode Toggle */}
                    <div style={{ marginBottom: '1.5rem', display: 'flex', gap: '1rem', justifyContent: 'center' }}>
                        <button
                            className={`btn ${inputMode === 'audio' ? 'btn-primary' : ''}`}
                            onClick={() => { setInputMode('audio'); setTextDescription(''); setResults(null); }}
                            disabled={loading || isRecording}
                            style={{
                                padding: '0.75rem 1.5rem',
                                borderRadius: '8px',
                                background: inputMode === 'audio' ? 'linear-gradient(135deg, #8b5cf6, #7c3aed)' : 'var(--gray-700)',
                                color: 'white',
                                border: 'none',
                                cursor: 'pointer',
                                fontSize: '1rem',
                                display: 'flex',
                                alignItems: 'center',
                                gap: '0.5rem'
                            }}
                        >
                            <FaMicrophone /> Audio Input
                        </button>
                        <button
                            className={`btn ${inputMode === 'text' ? 'btn-primary' : ''}`}
                            onClick={() => { setInputMode('text'); setFile(null); setAudioURL(null); setResults(null); }}
                            disabled={loading || isRecording}
                            style={{
                                padding: '0.75rem 1.5rem',
                                borderRadius: '8px',
                                background: inputMode === 'text' ? 'linear-gradient(135deg, #8b5cf6, #7c3aed)' : 'var(--gray-700)',
                                color: 'white',
                                border: 'none',
                                cursor: 'pointer',
                                fontSize: '1rem',
                                display: 'flex',
                                alignItems: 'center',
                                gap: '0.5rem'
                            }}
                        >
                            <FaUser /> Text Input
                        </button>
                    </div>

                    {inputMode === 'text' ? (
                        <div style={{ marginBottom: '1.5rem' }}>
                            <textarea
                                value={textDescription}
                                onChange={(e) => setTextDescription(e.target.value)}
                                placeholder="Describe the person's appearance... (e.g., 'Male, 30-35 years old, short black hair, beard, brown eyes, oval face')"
                                disabled={loading}
                                style={{
                                    width: '100%',
                                    minHeight: '150px',
                                    padding: '1rem',
                                    borderRadius: '8px',
                                    background: 'var(--gray-800)',
                                    border: '2px solid var(--gray-700)',
                                    color: 'var(--gray-100)',
                                    fontSize: '1rem',
                                    resize: 'vertical',
                                    fontFamily: 'inherit'
                                }}
                            />
                            <div style={{ marginTop: '0.5rem', color: 'var(--gray-500)', fontSize: '0.875rem' }}>
                                💡 Tip: Include details like age, gender, hair color/style, facial features, etc.
                            </div>
                        </div>
                    ) : (
                        <>

                            {/* Recording Button */}
                            <div style={{ marginBottom: '1.5rem', textAlign: 'center' }}>
                                {!isRecording ? (
                                    <button
                                        className="btn btn-lg"
                                        onClick={startRecording}
                                        disabled={loading}
                                        style={{
                                            background: 'linear-gradient(135deg, #ef4444, #dc2626)',
                                            color: 'white',
                                            padding: '1rem 2rem',
                                            borderRadius: '50px',
                                            display: 'inline-flex',
                                            alignItems: 'center',
                                            gap: '0.75rem',
                                            fontSize: '1.1rem',
                                            border: 'none',
                                            cursor: 'pointer',
                                            boxShadow: '0 4px 15px rgba(239, 68, 68, 0.4)'
                                        }}
                                    >
                                        <FaCircle style={{ fontSize: '0.8rem' }} /> Start Recording
                                    </button>
                                ) : (
                                    <div>
                                        <button
                                            className="btn btn-lg"
                                            onClick={stopRecording}
                                            style={{
                                                background: 'linear-gradient(135deg, #6b7280, #4b5563)',
                                                color: 'white',
                                                padding: '1rem 2rem',
                                                borderRadius: '50px',
                                                display: 'inline-flex',
                                                alignItems: 'center',
                                                gap: '0.75rem',
                                                fontSize: '1.1rem',
                                                border: 'none',
                                                cursor: 'pointer'
                                            }}
                                        >
                                            <FaStop /> Stop Recording
                                        </button>
                                        <div style={{
                                            marginTop: '1rem',
                                            color: '#ef4444',
                                            fontSize: '1.5rem',
                                            fontFamily: 'monospace',
                                            display: 'flex',
                                            alignItems: 'center',
                                            justifyContent: 'center',
                                            gap: '0.5rem'
                                        }}>
                                            <FaCircle className="animate-pulse" style={{ fontSize: '0.75rem' }} />
                                            {formatTime(recordingTime)}
                                        </div>
                                    </div>
                                )}
                            </div>

                            <div style={{ textAlign: 'center', color: 'var(--gray-500)', marginBottom: '1rem' }}>
                                — OR —
                            </div>

                            {/* File Upload Dropzone */}
                            <div
                                {...getRootProps()}
                                className={`dropzone ${isDragActive ? 'active' : ''}`}
                                style={{ minHeight: '120px' }}
                            >
                                <input {...getInputProps()} />
                                <div className="dropzone-icon" style={{ fontSize: '1.5rem' }}>📁</div>
                                {file ? (
                                    <div className="dropzone-text">
                                        <strong>{file.name}</strong>
                                        <p>{(file.size / 1024 / 1024).toFixed(2)} MB</p>
                                    </div>
                                ) : (
                                    <div className="dropzone-text">
                                        <strong>Drop audio file here</strong>
                                        <p>or click to browse</p>
                                    </div>
                                )}
                            </div>

                            {/* Audio Preview */}
                            {audioURL && (
                                <div style={{ marginTop: '1rem' }}>
                                    <audio controls src={audioURL} style={{ width: '100%' }} />
                                </div>
                            )}
                        </>

                    )}




                    {/* Options */}
                    <div style={{ marginTop: '1rem', padding: '1rem', background: 'rgba(0,0,0,0.2)', borderRadius: '8px' }}>
                        <label style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', cursor: 'pointer' }}>
                            <input
                                type="checkbox"
                                checked={generateSketch}
                                onChange={(e) => setGenerateSketch(e.target.checked)}
                                style={{ width: '18px', height: '18px' }}
                            />
                            <span>Generate AI Face Sketch</span>
                        </label>
                        <p style={{ fontSize: '0.75rem', color: 'var(--gray-500)', marginTop: '0.5rem', marginLeft: '26px' }}>
                            {generateSketch
                                ? '⚠️ First run downloads ~4GB model. May take 5-10 minutes.'
                                : '✅ Quick mode: transcription + NLP only (faster)'
                            }
                        </p>
                    </div>

                    <button
                        className="btn btn-primary btn-lg w-full mt-lg"
                        onClick={runAnalysis}
                        disabled={(inputMode === 'audio' && !file) || (inputMode === 'text' && !textDescription.trim()) || loading || isRecording}
                    >
                        {loading ? (
                            <>
                                <FaSpinner className="animate-pulse" /> {step || 'Processing...'}
                            </>
                        ) : (
                            <>
                                <FaPlay /> Run Full Analysis
                            </>
                        )}
                    </button>

                    {error && (
                        <div className="error-message" style={{ marginTop: '1rem', color: 'var(--danger)' }}>
                            {error}
                        </div>
                    )}
                </div>

                {/* Results Panel */}
                <div className="analysis-panel">
                    <div className="panel-header">
                        <div className="panel-icon"><FaUser /></div>
                        <h3 className="panel-title">Analysis Results</h3>
                    </div>

                    {loading && (
                        <div className="loading-container">
                            <div className="spinner"></div>
                            <p className="loading-text">{step}</p>
                        </div>
                    )}

                    {!loading && !results && (
                        <div className="empty-state">
                            <div className="empty-state-icon">📝</div>
                            <p>Record or upload audio to see analysis results</p>
                        </div>
                    )}

                    {results && (
                        <div className="results-content">
                            {/* Transcription */}
                            {results.transcription && (
                                <div className="transcription-box">
                                    <div className="transcription-label">Transcription</div>
                                    <p className="transcription-text">{results.transcription.text}</p>
                                </div>
                            )}

                            {/* Extracted Attributes */}
                            {results.attributes && (
                                <>
                                    <h4 style={{ marginBottom: '1rem' }}>Extracted Attributes</h4>
                                    <div className="attributes-grid">
                                        {results.attributes.gender && (
                                            <div className="attribute-item">
                                                <div className="attribute-label">Gender</div>
                                                <div className="attribute-value">{results.attributes.gender}</div>
                                            </div>
                                        )}
                                        {results.attributes.age_range && (
                                            <div className="attribute-item">
                                                <div className="attribute-label">Age Range</div>
                                                <div className="attribute-value">{results.attributes.age_range}</div>
                                            </div>
                                        )}
                                        {results.attributes.hair_color && (
                                            <div className="attribute-item">
                                                <div className="attribute-label">Hair Color</div>
                                                <div className="attribute-value">{results.attributes.hair_color}</div>
                                            </div>
                                        )}
                                        {results.attributes.facial_hair && (
                                            <div className="attribute-item">
                                                <div className="attribute-label">Facial Hair</div>
                                                <div className="attribute-value">{results.attributes.facial_hair}</div>
                                            </div>
                                        )}
                                        {results.attributes.face_shape && (
                                            <div className="attribute-item">
                                                <div className="attribute-label">Face Shape</div>
                                                <div className="attribute-value">{results.attributes.face_shape}</div>
                                            </div>
                                        )}
                                        {results.attributes.glasses !== null && (
                                            <div className="attribute-item">
                                                <div className="attribute-label">Glasses</div>
                                                <div className="attribute-value">{results.attributes.glasses ? 'Yes' : 'No'}</div>
                                            </div>
                                        )}
                                    </div>
                                </>
                            )}

                            {/* Generated Sketch */}
                            {results.generated_sketch && (
                                <div style={{ marginTop: '1.5rem' }}>
                                    <h4 style={{ marginBottom: '1rem' }}>Generated Sketch</h4>
                                    <div className="generated-image-container">
                                        <img
                                            src={`data:image/png;base64,${results.generated_sketch.image_base64}`}
                                            alt="Generated face sketch"
                                            className="generated-image"
                                        />
                                        <p style={{ marginTop: '1rem', fontSize: '0.8rem', color: 'var(--gray-500)' }}>
                                            Generated in {results.generated_sketch.generation_time_seconds.toFixed(2)}s
                                        </p>
                                    </div>
                                </div>
                            )}

                            {/* Face Matches */}
                            {results.face_matches && results.face_matches.matches.length > 0 && (
                                <div style={{ marginTop: '1.5rem' }}>
                                    <h4 style={{ marginBottom: '1rem' }}>
                                        <FaSearch style={{ marginRight: '0.5rem' }} />
                                        Similar Faces ({results.face_matches.matches.length})
                                    </h4>
                                    {results.face_matches.matches.map((match, index) => {
                                        const filename = match.image_path.split(/[/\\]/).pop();
                                        const imageUrl = `/faces/${filename}`;

                                        return (
                                            <div key={index} style={{
                                                display: 'flex',
                                                alignItems: 'center',
                                                gap: '1rem',
                                                padding: '0.75rem',
                                                background: 'var(--glass-bg)',
                                                borderRadius: '8px',
                                                marginBottom: '0.5rem'
                                            }}>
                                                <img
                                                    src={imageUrl}
                                                    alt={match.name}
                                                    style={{
                                                        width: '50px',
                                                        height: '50px',
                                                        borderRadius: '8px',
                                                        objectFit: 'cover'
                                                    }}
                                                    onError={(e) => { e.target.style.display = 'none'; }}
                                                />
                                                <div style={{ flex: 1 }}>
                                                    <div style={{ fontWeight: '600' }}>{match.name}</div>
                                                    <div style={{ fontSize: '0.8rem', color: 'var(--gray-500)' }}>
                                                        {match.similarity_percentage.toFixed(1)}% match
                                                    </div>
                                                </div>
                                            </div>
                                        );
                                    })}
                                    <p style={{ fontSize: '0.8rem', color: 'var(--gray-500)', marginTop: '1rem' }}>
                                        ⚠️ Similarity scores are AI estimates, not identity confirmation
                                    </p>
                                </div>
                            )}

                            {/* Processing Time */}
                            <div style={{ marginTop: '1.5rem', textAlign: 'center', color: 'var(--gray-500)', fontSize: '0.85rem' }}>
                                Total processing time: {results.processing_time_seconds.toFixed(2)}s
                            </div>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
}

export default AudioAnalysis;
