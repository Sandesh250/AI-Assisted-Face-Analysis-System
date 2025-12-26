import { useState, useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import { FaImage, FaUpload, FaSearch, FaSpinner, FaShieldAlt, FaCheckCircle, FaExclamationTriangle } from 'react-icons/fa';
import { analyzeFromImage } from '../services/api';

function ImageAnalysis() {
    const [file, setFile] = useState(null);
    const [preview, setPreview] = useState(null);
    const [loading, setLoading] = useState(false);
    const [results, setResults] = useState(null);
    const [error, setError] = useState(null);

    const onDrop = useCallback((acceptedFiles) => {
        if (acceptedFiles.length > 0) {
            const selectedFile = acceptedFiles[0];
            setFile(selectedFile);
            setPreview(URL.createObjectURL(selectedFile));
            setResults(null);
            setError(null);
        }
    }, []);

    const { getRootProps, getInputProps, isDragActive } = useDropzone({
        onDrop,
        accept: {
            'image/*': ['.jpg', '.jpeg', '.png', '.webp']
        },
        maxFiles: 1
    });

    const runAnalysis = async () => {
        if (!file) return;

        setLoading(true);
        setError(null);

        try {
            const result = await analyzeFromImage(file, 5);
            setResults(result);
        } catch (err) {
            setError(err.response?.data?.detail || err.message || 'Analysis failed');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="image-analysis animate-fade-in">
            <div className="page-header">
                <h1><FaImage /> Image Analysis</h1>
                <p>
                    Upload an image to verify its authenticity using deepfake detection
                    and find similar faces in the database.
                </p>
            </div>

            <div className="disclaimer-banner">
                <p>⚠️ AI detection is probabilistic. Results should be verified by experts. For educational purposes only.</p>
            </div>

            <div className="analysis-layout">
                {/* Upload Panel */}
                <div className="analysis-panel">
                    <div className="panel-header">
                        <div className="panel-icon"><FaUpload /></div>
                        <h3 className="panel-title">Upload Image</h3>
                    </div>

                    <div
                        {...getRootProps()}
                        className={`dropzone ${isDragActive ? 'active' : ''}`}
                    >
                        <input {...getInputProps()} />
                        {preview ? (
                            <img
                                src={preview}
                                alt="Preview"
                                style={{ maxWidth: '100%', maxHeight: '200px', borderRadius: '8px' }}
                            />
                        ) : (
                            <>
                                <div className="dropzone-icon">🖼️</div>
                                <div className="dropzone-text">
                                    <strong>Drop image here</strong>
                                    <p>or click to browse</p>
                                    <p style={{ fontSize: '0.8rem', marginTop: '0.5rem' }}>
                                        Supports: JPG, PNG, WebP
                                    </p>
                                </div>
                            </>
                        )}
                    </div>

                    {file && (
                        <p style={{ marginTop: '1rem', fontSize: '0.9rem', color: 'var(--gray-400)' }}>
                            {file.name} ({(file.size / 1024 / 1024).toFixed(2)} MB)
                        </p>
                    )}

                    <button
                        className="btn btn-primary btn-lg w-full mt-lg"
                        onClick={runAnalysis}
                        disabled={!file || loading}
                    >
                        {loading ? (
                            <>
                                <FaSpinner className="animate-pulse" /> Analyzing...
                            </>
                        ) : (
                            <>
                                <FaSearch /> Analyze Image
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
                        <div className="panel-icon"><FaShieldAlt /></div>
                        <h3 className="panel-title">Analysis Results</h3>
                    </div>

                    {loading && (
                        <div className="loading-container">
                            <div className="spinner"></div>
                            <p className="loading-text">Analyzing image authenticity...</p>
                        </div>
                    )}

                    {!loading && !results && (
                        <div className="empty-state">
                            <div className="empty-state-icon">🔍</div>
                            <p>Upload an image to see analysis results</p>
                        </div>
                    )}

                    {results && (
                        <div className="results-content">
                            {/* Deepfake Verification */}
                            {results.deepfake_verification && (
                                <div className="verification-result">
                                    <div className={`verification-icon ${results.deepfake_verification.is_real ? 'real' : 'fake'}`}>
                                        {results.deepfake_verification.is_real ? <FaCheckCircle /> : <FaExclamationTriangle />}
                                    </div>
                                    <h3 className="verification-verdict">
                                        {results.deepfake_verification.verdict}
                                    </h3>
                                    <p className="verification-confidence">
                                        Confidence: {(results.deepfake_verification.confidence * 100).toFixed(1)}%
                                    </p>

                                    <div className={`badge ${results.deepfake_verification.is_real ? 'badge-success' : 'badge-danger'}`} style={{ fontSize: '1rem', padding: '0.5rem 1rem' }}>
                                        {results.deepfake_verification.is_real ? 'Likely Authentic' : 'Potentially Manipulated'}
                                    </div>

                                    {/* Detection Details */}
                                    {results.deepfake_verification.details && (
                                        <div style={{ marginTop: '1.5rem', textAlign: 'left' }}>
                                            <h4 style={{ marginBottom: '0.5rem' }}>Detection Details</h4>
                                            <div className="attributes-grid">
                                                <div className="attribute-item">
                                                    <div className="attribute-label">Real Probability</div>
                                                    <div className="attribute-value">
                                                        {(results.deepfake_verification.details.real_probability * 100).toFixed(1)}%
                                                    </div>
                                                </div>
                                                <div className="attribute-item">
                                                    <div className="attribute-label">Fake Probability</div>
                                                    <div className="attribute-value">
                                                        {(results.deepfake_verification.details.fake_probability * 100).toFixed(1)}%
                                                    </div>
                                                </div>
                                                <div className="attribute-item">
                                                    <div className="attribute-label">Model</div>
                                                    <div className="attribute-value">{results.deepfake_verification.details.model_used}</div>
                                                </div>
                                                <div className="attribute-item">
                                                    <div className="attribute-label">Processing Time</div>
                                                    <div className="attribute-value">
                                                        {results.deepfake_verification.details.processing_time_seconds}s
                                                    </div>
                                                </div>
                                            </div>
                                        </div>
                                    )}
                                </div>
                            )}

                            {/* Face Matches */}
                            {results.face_matches && results.face_matches.matches.length > 0 && (
                                <div style={{ marginTop: '1.5rem' }}>
                                    <h4 style={{ marginBottom: '1rem' }}>
                                        <FaSearch style={{ marginRight: '0.5rem' }} />
                                        Similar Faces ({results.face_matches.matches.length})
                                    </h4>
                                    {results.face_matches.matches.map((match, index) => (
                                        <div key={index} className="match-card">
                                            <div className="match-info">
                                                <div className="match-name">{match.name}</div>
                                                <div className="match-score">
                                                    <div className="score-bar">
                                                        <div className="score-fill" style={{ width: `${match.similarity_percentage}%` }}></div>
                                                    </div>
                                                    <span className="score-value">{match.similarity_percentage.toFixed(1)}%</span>
                                                </div>
                                            </div>
                                        </div>
                                    ))}
                                </div>
                            )}

                            {results.face_matches && results.face_matches.matches.length === 0 && (
                                <div style={{ marginTop: '1.5rem', textAlign: 'center', color: 'var(--gray-500)' }}>
                                    No similar faces found in database ({results.face_matches.total_database_faces} faces indexed)
                                </div>
                            )}

                            {/* Disclaimer */}
                            <div style={{ marginTop: '1.5rem', padding: '1rem', background: 'rgba(245, 158, 11, 0.1)', borderRadius: '8px' }}>
                                <p style={{ fontSize: '0.85rem', color: 'var(--warning)' }}>
                                    ⚠️ {results.disclaimer}
                                </p>
                            </div>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
}

export default ImageAnalysis;
