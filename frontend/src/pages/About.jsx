import { FaGithub, FaBook, FaShieldAlt, FaBrain, FaBalanceScale } from 'react-icons/fa';

function About() {
    return (
        <div className="about-page animate-fade-in">
            <div className="page-header">
                <h1>📚 About This Project</h1>
                <p>
                    Multimodal AI System for Suspect Identification with Deepfake Verification
                </p>
            </div>

            <div className="feature-grid">
                {/* Project Overview */}
                <div className="card" style={{ gridColumn: 'span 2' }}>
                    <h2><FaBrain style={{ marginRight: '0.5rem' }} /> Project Overview</h2>
                    <p style={{ marginTop: '1rem' }}>
                        This is an <strong>educational</strong> AI system demonstrating how multiple AI
                        technologies can be combined for identity analysis. It showcases:
                    </p>
                    <ul style={{ marginTop: '1rem', paddingLeft: '1.5rem', color: 'var(--gray-300)' }}>
                        <li>Speech-to-Text using OpenAI Whisper</li>
                        <li>Natural Language Processing with spaCy</li>
                        <li>AI Image Generation with Stable Diffusion</li>
                        <li>Deepfake Detection using EfficientNet</li>
                        <li>Face Recognition with ArcFace embeddings</li>
                        <li>Vector Similarity Search with FAISS</li>
                    </ul>
                </div>

                {/* Ethical Considerations */}
                <div className="card" style={{ gridColumn: 'span 2', borderColor: 'rgba(245, 158, 11, 0.3)' }}>
                    <h2><FaBalanceScale style={{ marginRight: '0.5rem', color: 'var(--warning)' }} /> Ethical Considerations</h2>

                    <div style={{ marginTop: '1rem' }}>
                        <h4 style={{ color: 'var(--danger)' }}>⚠️ Important Disclaimers</h4>
                        <ul style={{ marginTop: '0.5rem', paddingLeft: '1.5rem', color: 'var(--gray-300)' }}>
                            <li><strong>Educational Only:</strong> This system is NOT for real-world law enforcement</li>
                            <li><strong>No Real Criminal Data:</strong> Uses only public/synthetic datasets (LFW)</li>
                            <li><strong>AI Limitations:</strong> All results are probabilistic, not definitive</li>
                            <li><strong>Bias Awareness:</strong> AI systems can have demographic biases</li>
                            <li><strong>Privacy:</strong> No personal data is stored or transmitted</li>
                        </ul>
                    </div>

                    <div style={{ marginTop: '1.5rem' }}>
                        <h4>🎯 Responsible AI Principles</h4>
                        <ul style={{ marginTop: '0.5rem', paddingLeft: '1.5rem', color: 'var(--gray-300)' }}>
                            <li><strong>Transparency:</strong> All AI decisions include confidence scores</li>
                            <li><strong>Explainability:</strong> Similarity calculations are documented</li>
                            <li><strong>No Demographics:</strong> System does not predict race, ethnicity, or religion</li>
                            <li><strong>Human Oversight:</strong> Results should always be verified by experts</li>
                        </ul>
                    </div>
                </div>

                {/* Technology Stack */}
                <div className="card">
                    <h3>🛠️ Technology Stack</h3>
                    <div style={{ marginTop: '1rem' }}>
                        <div style={{ marginBottom: '1rem' }}>
                            <strong style={{ color: 'var(--primary-400)' }}>Backend</strong>
                            <p style={{ fontSize: '0.9rem', color: 'var(--gray-400)' }}>
                                Python, FastAPI, PyTorch, FAISS
                            </p>
                        </div>
                        <div style={{ marginBottom: '1rem' }}>
                            <strong style={{ color: 'var(--primary-400)' }}>AI Models</strong>
                            <p style={{ fontSize: '0.9rem', color: 'var(--gray-400)' }}>
                                Whisper, Stable Diffusion, EfficientNet, ArcFace
                            </p>
                        </div>
                        <div>
                            <strong style={{ color: 'var(--primary-400)' }}>Frontend</strong>
                            <p style={{ fontSize: '0.9rem', color: 'var(--gray-400)' }}>
                                React 18, Vite, React Router
                            </p>
                        </div>
                    </div>
                </div>

                {/* AI Models */}
                <div className="card">
                    <h3>🤖 AI Models Used</h3>
                    <table style={{ width: '100%', marginTop: '1rem', fontSize: '0.9rem' }}>
                        <tbody>
                            <tr>
                                <td style={{ padding: '0.5rem 0', color: 'var(--gray-400)' }}>ASR</td>
                                <td style={{ padding: '0.5rem 0' }}>Whisper Base (74M)</td>
                            </tr>
                            <tr>
                                <td style={{ padding: '0.5rem 0', color: 'var(--gray-400)' }}>NLP</td>
                                <td style={{ padding: '0.5rem 0' }}>spaCy en_core_web_sm</td>
                            </tr>
                            <tr>
                                <td style={{ padding: '0.5rem 0', color: 'var(--gray-400)' }}>Image Gen</td>
                                <td style={{ padding: '0.5rem 0' }}>SD v1.5</td>
                            </tr>
                            <tr>
                                <td style={{ padding: '0.5rem 0', color: 'var(--gray-400)' }}>Deepfake</td>
                                <td style={{ padding: '0.5rem 0' }}>EfficientNet-B0</td>
                            </tr>
                            <tr>
                                <td style={{ padding: '0.5rem 0', color: 'var(--gray-400)' }}>Embeddings</td>
                                <td style={{ padding: '0.5rem 0' }}>ArcFace (512-dim)</td>
                            </tr>
                        </tbody>
                    </table>
                </div>

                {/* Resume Points */}
                <div className="card" style={{ gridColumn: 'span 2' }}>
                    <h3><FaBook style={{ marginRight: '0.5rem' }} /> Resume-Ready Description</h3>
                    <div style={{ marginTop: '1rem', padding: '1rem', background: 'rgba(0, 0, 0, 0.2)', borderRadius: '8px' }}>
                        <p style={{ fontStyle: 'italic', color: 'var(--gray-300)', lineHeight: '1.8' }}>
                            "Developed a multimodal AI system for educational identity analysis, integrating
                            speech recognition (Whisper), NLP (spaCy), generative AI (Stable Diffusion),
                            deepfake detection (EfficientNet), and face recognition (ArcFace + FAISS).
                            Built with FastAPI backend and React frontend, featuring GPU-accelerated inference,
                            RESTful APIs, and emphasis on ethical AI principles with bias awareness and transparency."
                        </p>
                    </div>

                    <div style={{ marginTop: '1rem' }}>
                        <h4>Key Highlights:</h4>
                        <ul style={{ marginTop: '0.5rem', paddingLeft: '1.5rem', color: 'var(--gray-300)', lineHeight: '1.8' }}>
                            <li>Integrated 5+ AI models in a unified pipeline</li>
                            <li>CUDA-accelerated inference with PyTorch</li>
                            <li>Vector similarity search with FAISS (under 100ms query time)</li>
                            <li>Clean architecture with modular services</li>
                            <li>Comprehensive API documentation (OpenAPI/Swagger)</li>
                            <li>Ethical AI implementation with bias disclaimers</li>
                        </ul>
                    </div>
                </div>

                {/* Acknowledgments */}
                <div className="card" style={{ gridColumn: 'span 2' }}>
                    <h3>🙏 Acknowledgments</h3>
                    <p style={{ marginTop: '1rem', color: 'var(--gray-400)' }}>
                        This project uses the following open-source technologies and datasets:
                    </p>
                    <ul style={{ marginTop: '0.5rem', paddingLeft: '1.5rem', color: 'var(--gray-300)' }}>
                        <li>OpenAI Whisper for speech recognition</li>
                        <li>Stability AI for Stable Diffusion</li>
                        <li>InsightFace for face recognition</li>
                        <li>Facebook AI for FAISS</li>
                        <li>University of Massachusetts for LFW dataset</li>
                    </ul>
                </div>
            </div>
        </div>
    );
}

export default About;
