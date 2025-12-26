import { useState } from 'react'
import { BrowserRouter as Router, Routes, Route, NavLink } from 'react-router-dom'
import { FaHome, FaMicrophone, FaImage, FaSearch, FaShieldAlt, FaInfoCircle } from 'react-icons/fa'
import Dashboard from './pages/Dashboard'
import AudioAnalysis from './pages/AudioAnalysis'
import ImageAnalysis from './pages/ImageAnalysis'
import FaceSearch from './pages/FaceSearch'
import About from './pages/About'
import './App.css'

function App() {
    return (
        <Router>
            <div className="app">
                {/* Disclaimer Banner */}
                <div className="disclaimer-banner">
                    <p>
                        ⚠️ <strong>EDUCATIONAL PROJECT</strong> - This system is for learning and research purposes only.
                        Not for real-world surveillance or law enforcement use. AI results are probabilistic, not definitive.
                    </p>
                </div>

                {/* Navigation */}
                <nav className="navbar">
                    <div className="nav-brand">
                        <div className="brand-icon">🔍</div>
                        <div className="brand-text">
                            <span className="brand-title">AI Identity Analysis</span>
                            <span className="brand-subtitle">Educational System</span>
                        </div>
                    </div>

                    <div className="nav-links">
                        <NavLink to="/" className={({ isActive }) => isActive ? 'nav-link active' : 'nav-link'}>
                            <FaHome /> <span>Dashboard</span>
                        </NavLink>
                        <NavLink to="/audio" className={({ isActive }) => isActive ? 'nav-link active' : 'nav-link'}>
                            <FaMicrophone /> <span>Audio Analysis</span>
                        </NavLink>
                        <NavLink to="/image" className={({ isActive }) => isActive ? 'nav-link active' : 'nav-link'}>
                            <FaImage /> <span>Image Analysis</span>
                        </NavLink>
                        <NavLink to="/search" className={({ isActive }) => isActive ? 'nav-link active' : 'nav-link'}>
                            <FaSearch /> <span>Face Search</span>
                        </NavLink>
                        <NavLink to="/about" className={({ isActive }) => isActive ? 'nav-link active' : 'nav-link'}>
                            <FaInfoCircle /> <span>About</span>
                        </NavLink>
                    </div>
                </nav>

                {/* Main Content */}
                <main className="main-content">
                    <Routes>
                        <Route path="/" element={<Dashboard />} />
                        <Route path="/audio" element={<AudioAnalysis />} />
                        <Route path="/image" element={<ImageAnalysis />} />
                        <Route path="/search" element={<FaceSearch />} />
                        <Route path="/about" element={<About />} />
                    </Routes>
                </main>

                {/* Footer */}
                <footer className="footer">
                    <p>
                        <FaShieldAlt /> Educational Project | AI-Assisted Analysis |
                        <a href="#ethics"> View Ethical Guidelines</a>
                    </p>
                </footer>
            </div>
        </Router>
    )
}

export default App
