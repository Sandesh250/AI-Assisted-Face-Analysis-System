import axios from 'axios';

const API_BASE_URL = '/api/v1';

const api = axios.create({
    baseURL: API_BASE_URL,
    timeout: 600000, // 10 minutes for AI processing (Stable Diffusion needs time)
});

// Speech-to-Text
export const transcribeAudio = async (audioFile) => {
    const formData = new FormData();
    formData.append('file', audioFile);

    const response = await api.post('/speech-to-text', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
    });
    return response.data;
};

// NLP Processing
export const processDescription = async (text) => {
    const response = await api.post('/process-description', { text });
    return response.data;
};

// Face Generation
export const generateSketch = async (description, style = 'portrait') => {
    const response = await api.post('/generate-sketch', { description, style });
    return response.data;
};

// Deepfake Detection
export const verifyImage = async (imageFile) => {
    const formData = new FormData();
    formData.append('file', imageFile);

    const response = await api.post('/deepfake/verify', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
    });
    return response.data;
};

// Face Matching
export const matchFaces = async (imageFile, topK = 5) => {
    const formData = new FormData();
    formData.append('file', imageFile);
    formData.append('top_k', topK);

    const response = await api.post('/match-faces', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
    });
    return response.data;
};

// Full Analysis - Audio
export const analyzeFromAudio = async (audioFile, generateSketch = true, topK = 5) => {
    const formData = new FormData();
    formData.append('audio_file', audioFile);
    formData.append('generate_sketch', generateSketch);
    formData.append('top_k', topK);

    const response = await api.post('/analyze/audio', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
    });
    return response.data;
};

// Full Analysis - Image
export const analyzeFromImage = async (imageFile, topK = 5) => {
    const formData = new FormData();
    formData.append('image_file', imageFile);
    formData.append('top_k', topK);

    const response = await api.post('/analyze/image', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
    });
    return response.data;
};

// Health Check
export const checkHealth = async () => {
    const response = await api.get('/health');
    return response.data;
};

// Get System Status
export const getSystemStatus = async () => {
    const response = await api.get('/analyze/status');
    return response.data;
};

// Database Stats
export const getDatabaseStats = async () => {
    const response = await api.get('/database-stats');
    return response.data;
};

export default api;
