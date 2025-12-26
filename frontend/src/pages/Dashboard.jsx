import { Link } from 'react-router-dom';
import { FaMicrophone, FaImage, FaSearch, FaShieldAlt, FaBrain, FaDatabase } from 'react-icons/fa';
import { useEffect, useState } from 'react';
import { getSystemStatus, getDatabaseStats } from '../services/api';

function Dashboard() {
    const [stats, setStats] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const loadStats = async () => {
            try {
                const status = await getSystemStatus();
                const dbStats = await getDatabaseStats();
                setStats({ ...status, database: dbStats });
            } catch (error) {
                console.error('Failed to load stats:', error);
            } finally {
                setLoading(false);
            }
        };

        loadStats();
    }, []);

    const features = [
        {
            icon: <FaMicrophone />,
            title: 'Audio Analysis',
            description: 'Upload audio descriptions and let AI transcribe, extract attributes, and generate face sketches.',
            link: '/audio',
            color: '#8b5cf6'
        },
        {
            icon: <FaImage />,
            title: 'Image Analysis',
            description: 'Upload images for deepfake detection and authenticity verification using neural networks.',
            link: '/image',
            color: '#06b6d4'
        },
        {
            icon: <FaSearch />,
            title: 'Face Search',
            description: 'Search for similar faces in the database using AI-powered embedding matching.',
            link: '/search',
            color: '#10b981'
        },
        {
            icon: <FaShieldAlt />,
            title: 'Deepfake Detection',
            description: 'Verify if uploaded images are authentic or potentially manipulated using EfficientNet.',
            link: '/image',
            color: '#f59e0b'
        }
    ];

    return (
        <div className="dashboard animate-fade-in">
            {/* Page Header */}
            <div className="page-header">
                <h1>🔍 Multimodal AI Identity Analysis</h1>
                <p>
                    An educational system demonstrating AI-powered identity analysis combining
                    speech recognition, NLP, generative AI, and computer vision.
                </p>
            </div>

            {/* Stats Grid */}
            <div className="stats-grid">
                <div className="stat-card">
                    <div className="stat-value">5</div>
                    <div className="stat-label">AI Models</div>
                </div>
                <div className="stat-card">
                    <div className="stat-value">{stats?.database?.total_faces || '0'}</div>
                    <div className="stat-label">Faces in DB</div>
                </div>
                <div className="stat-card">
                    <div className="stat-value">512</div>
                    <div className="stat-label">Embedding Dim</div>
                </div>
                <div className="stat-card">
                    <div className="stat-value">GPU</div>
                    <div className="stat-label">Accelerated</div>
                </div>
            </div>

            {/* Feature Cards */}
            <div className="feature-grid">
                {features.map((feature, index) => (
                    <Link to={feature.link} key={index} className="feature-card">
                        <div className="feature-icon" style={{ background: `linear-gradient(135deg, ${feature.color}, ${feature.color}80)` }}>
                            {feature.icon}
                        </div>
                        <h3>{feature.title}</h3>
                        <p>{feature.description}</p>
                    </Link>
                ))}
            </div>

            {/* Technology Stack */}
            <div className="tech-stack" style={{ marginTop: 'var(--spacing-2xl)' }}>
                <h2 style={{ textAlign: 'center', marginBottom: 'var(--spacing-xl)' }}>
                    <FaBrain style={{ marginRight: 'var(--spacing-sm)' }} />
                    Technology Stack
                </h2>

                <div className="feature-grid">
                    <div className="card">
                        <h4>🎤 Speech Recognition</h4>
                        <p>OpenAI Whisper (base) - Robust ASR supporting multiple languages</p>
                    </div>
                    <div className="card">
                        <h4>🧠 NLP Processing</h4>
                        <p>spaCy - Named entity recognition and attribute extraction</p>
                    </div>
                    <div className="card">
                        <h4>🎨 Face Generation</h4>
                        <p>Stable Diffusion v1.5 - High-quality portrait generation</p>
                    </div>
                    <div className="card">
                        <h4>🔍 Deepfake Detection</h4>
                        <p>EfficientNet-B0 - CNN-based manipulation detection</p>
                    </div>
                    <div className="card">
                        <h4>👤 Face Embeddings</h4>
                        <p>InsightFace/ArcFace - 512-dimensional face vectors</p>
                    </div>
                    <div className="card">
                        <h4>📊 Vector Search</h4>
                        <p>FAISS - Fast similarity search at scale</p>
                    </div>
                </div>
            </div>

            {/* Ethics Notice */}
            <div className="ethics-notice" style={{ marginTop: 'var(--spacing-2xl)' }}>
                <div className="card" style={{ borderColor: 'rgba(245, 158, 11, 0.3)' }}>
                    <h3>⚠️ Ethical Considerations</h3>
                    <ul style={{ marginTop: 'var(--spacing-md)', paddingLeft: 'var(--spacing-xl)', color: 'var(--gray-300)' }}>
                        <li>This system is for <strong>educational purposes only</strong></li>
                        <li>Uses only synthetic/public datasets (LFW)</li>
                        <li>AI results are probabilistic, not definitive</li>
                        <li>No demographic predictions are made</li>
                        <li>Not intended for real-world law enforcement</li>
                    </ul>
                </div>
            </div>
        </div>
    );
}

export default Dashboard;
