import { useState, useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import { FaSearch, FaUpload, FaSpinner, FaDatabase } from 'react-icons/fa';
import { matchFaces, getDatabaseStats } from '../services/api';
import { useEffect } from 'react';

function FaceSearch() {
    const [file, setFile] = useState(null);
    const [preview, setPreview] = useState(null);
    const [loading, setLoading] = useState(false);
    const [results, setResults] = useState(null);
    const [error, setError] = useState(null);
    const [dbStats, setDbStats] = useState(null);
    const [topK, setTopK] = useState(5);

    useEffect(() => {
        const loadStats = async () => {
            try {
                const stats = await getDatabaseStats();
                setDbStats(stats);
            } catch (err) {
                console.error('Failed to load stats:', err);
            }
        };
        loadStats();
    }, []);

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

    const runSearch = async () => {
        if (!file) return;

        setLoading(true);
        setError(null);

        try {
            const result = await matchFaces(file, topK);
            setResults(result);
        } catch (err) {
            setError(err.response?.data?.detail || err.message || 'Search failed');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="face-search animate-fade-in">
            <div className="page-header">
                <h1><FaSearch /> Face Similarity Search</h1>
                <p>
                    Upload a face image to find similar faces in the database using
                    AI-powered embedding comparison (ArcFace + FAISS).
                </p>
            </div>

            <div className="disclaimer-banner">
                <p>⚠️ Face matching provides AI suggestions only, not identity confirmation. For educational purposes only.</p>
            </div>

            {/* Database Stats */}
            {dbStats && (
                <div className="stats-grid" style={{ marginBottom: '2rem' }}>
                    <div className="stat-card">
                        <div className="stat-value">{dbStats.total_faces}</div>
                        <div className="stat-label">Faces in Database</div>
                    </div>
                    <div className="stat-card">
                        <div className="stat-value">{dbStats.embedding_dimension}</div>
                        <div className="stat-label">Embedding Dimension</div>
                    </div>
                    <div className="stat-card">
                        <div className="stat-value">FAISS</div>
                        <div className="stat-label">Vector Index</div>
                    </div>
                    <div className="stat-card">
                        <div className="stat-value">Cosine</div>
                        <div className="stat-label">Similarity Metric</div>
                    </div>
                </div>
            )}

            <div className="analysis-layout">
                {/* Upload Panel */}
                <div className="analysis-panel">
                    <div className="panel-header">
                        <div className="panel-icon"><FaUpload /></div>
                        <h3 className="panel-title">Query Image</h3>
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
                                <div className="dropzone-icon">👤</div>
                                <div className="dropzone-text">
                                    <strong>Drop face image here</strong>
                                    <p>or click to browse</p>
                                </div>
                            </>
                        )}
                    </div>

                    {/* Options */}
                    <div style={{ marginTop: '1.5rem' }}>
                        <label>Number of Results</label>
                        <select
                            value={topK}
                            onChange={(e) => setTopK(Number(e.target.value))}
                            style={{ marginTop: '0.5rem' }}
                        >
                            <option value={3}>Top 3</option>
                            <option value={5}>Top 5</option>
                            <option value={10}>Top 10</option>
                            <option value={20}>Top 20</option>
                        </select>
                    </div>

                    <button
                        className="btn btn-primary btn-lg w-full mt-lg"
                        onClick={runSearch}
                        disabled={!file || loading}
                    >
                        {loading ? (
                            <>
                                <FaSpinner className="animate-pulse" /> Searching...
                            </>
                        ) : (
                            <>
                                <FaSearch /> Find Similar Faces
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
                        <div className="panel-icon"><FaDatabase /></div>
                        <h3 className="panel-title">Search Results</h3>
                    </div>

                    {loading && (
                        <div className="loading-container">
                            <div className="spinner"></div>
                            <p className="loading-text">Generating embedding and searching...</p>
                        </div>
                    )}

                    {!loading && !results && (
                        <div className="empty-state">
                            <div className="empty-state-icon">🔍</div>
                            <p>Upload a face image to search the database</p>
                        </div>
                    )}

                    {results && (
                        <div className="results-content">
                            {results.matches.length > 0 ? (
                                <>
                                    <p style={{ marginBottom: '1rem', color: 'var(--gray-400)' }}>
                                        Found {results.matches.length} matches in {results.search_time_seconds.toFixed(3)}s
                                    </p>

                                    {results.matches.map((match, index) => {
                                        // Extract filename from the full path
                                        const filename = match.image_path.split(/[/\\]/).pop();
                                        const imageUrl = `/faces/${filename}`;

                                        return (
                                            <div key={index} className="match-card" style={{
                                                display: 'flex',
                                                alignItems: 'center',
                                                gap: '1rem',
                                                padding: '1rem',
                                                background: 'var(--glass-bg)',
                                                borderRadius: '12px',
                                                marginBottom: '0.75rem'
                                            }}>
                                                {/* Rank Badge */}
                                                <div style={{
                                                    width: '32px',
                                                    height: '32px',
                                                    background: index === 0 ? 'var(--gradient-primary)' : 'var(--gray-700)',
                                                    borderRadius: '50%',
                                                    display: 'flex',
                                                    alignItems: 'center',
                                                    justifyContent: 'center',
                                                    fontWeight: 'bold',
                                                    fontSize: '0.9rem',
                                                    flexShrink: 0
                                                }}>
                                                    {index + 1}
                                                </div>

                                                {/* Face Image */}
                                                <div style={{
                                                    width: '80px',
                                                    height: '80px',
                                                    borderRadius: '8px',
                                                    overflow: 'hidden',
                                                    flexShrink: 0,
                                                    border: '2px solid var(--primary)'
                                                }}>
                                                    <img
                                                        src={imageUrl}
                                                        alt={match.name}
                                                        style={{
                                                            width: '100%',
                                                            height: '100%',
                                                            objectFit: 'cover'
                                                        }}
                                                        onError={(e) => {
                                                            e.target.style.display = 'none';
                                                        }}
                                                    />
                                                </div>

                                                {/* Match Info */}
                                                <div style={{ flex: 1 }}>
                                                    <div style={{ fontWeight: '600', marginBottom: '0.25rem' }}>
                                                        {match.name}
                                                    </div>
                                                    <div style={{ fontSize: '0.75rem', color: 'var(--gray-500)', marginBottom: '0.5rem' }}>
                                                        ID: {match.id}
                                                    </div>
                                                    <div className="match-score">
                                                        <div className="score-bar" style={{ height: '6px' }}>
                                                            <div
                                                                className="score-fill"
                                                                style={{
                                                                    width: `${match.similarity_percentage}%`,
                                                                    background: match.similarity_percentage > 80
                                                                        ? 'var(--success)'
                                                                        : match.similarity_percentage > 60
                                                                            ? 'var(--warning)'
                                                                            : 'var(--gradient-primary)'
                                                                }}
                                                            ></div>
                                                        </div>
                                                        <span className="score-value" style={{ fontSize: '0.85rem' }}>
                                                            {match.similarity_percentage.toFixed(1)}%
                                                        </span>
                                                    </div>
                                                </div>
                                            </div>
                                        );
                                    })}

                                    {/* Similarity Explanation */}
                                    <div style={{ marginTop: '1.5rem', padding: '1rem', background: 'rgba(0, 0, 0, 0.2)', borderRadius: '8px' }}>
                                        <h4 style={{ marginBottom: '0.5rem', fontSize: '0.9rem' }}>📊 How Similarity Works</h4>
                                        <p style={{ fontSize: '0.85rem', color: 'var(--gray-400)' }}>
                                            Faces are converted to 512-dimensional vectors using ArcFace.
                                            Similarity is calculated using cosine similarity:
                                            <code style={{ background: 'rgba(139, 92, 246, 0.2)', padding: '0.2rem 0.4rem', borderRadius: '4px', marginLeft: '0.25rem' }}>
                                                cos(θ) = (A · B) / (||A|| × ||B||)
                                            </code>
                                        </p>
                                    </div>
                                </>
                            ) : (
                                <div className="empty-state">
                                    <div className="empty-state-icon">😕</div>
                                    <p>No similar faces found in database</p>
                                    <p style={{ fontSize: '0.85rem', marginTop: '0.5rem' }}>
                                        Database contains {results.total_database_faces} faces
                                    </p>
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

export default FaceSearch;
