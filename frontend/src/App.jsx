import React, { useState } from 'react';
import axios from 'axios';
import './App.css'; // We'll define styles in App.css

// --- Configuration ---
// Change this from localhost to your Render URL
const API_URL = 'https://eco-sort-wmvk.onrender.com/api/predict';
const INITIAL_RESULT_STATE = {
    class: null,
    confidence: null,
    instruction: null,
    tip: null,
    error: null,
};

function App() {
    // State for the uploaded file object
    const [selectedFile, setSelectedFile] = useState(null);
    // State for the image preview URL
    const [previewUrl, setPreviewUrl] = useState(null);
    // State to store the prediction results
    const [result, setResult] = useState(INITIAL_RESULT_STATE);
    // State for showing loading/processing status
    const [isLoading, setIsLoading] = useState(false);

    // 1. Handle file selection from the input
    const handleFileChange = (event) => {
        const file = event.target.files[0];
        if (file) {
            setSelectedFile(file);
            setResult(INITIAL_RESULT_STATE); // Clear previous results
            // Create a local URL for image preview
            setPreviewUrl(URL.createObjectURL(file)); 
        }
    };

    // 2. Handle the prediction submission
    const handleUpload = async () => {
        if (!selectedFile) {
            setResult({ ...INITIAL_RESULT_STATE, error: 'Please select an image file first.' });
            return;
        }

        setIsLoading(true);
        setResult(INITIAL_RESULT_STATE); // Clear previous errors/results

        // Create form data to send the file to the Flask API
        const formData = new FormData();
        formData.append('file', selectedFile);

        try {
            const response = await axios.post(API_URL, formData, {
                headers: { 'Content-Type': 'multipart/form-data' },
            });

            // Handle successful response from Flask
            if (response.data.error) {
                 setResult({ ...INITIAL_RESULT_STATE, error: response.data.error });
            } else {
                setResult({
                    class: response.data.class,
                    confidence: response.data.confidence,
                    instruction: response.data.instruction,
                    tip: response.data.tip,
                    error: null,
                });
            }
        } catch (error) {
            // Handle network or server errors
            console.error('API Call Error:', error);
            setResult({ 
                ...INITIAL_RESULT_STATE, 
                error: `Failed to connect to the backend API. Is the Flask server running on ${API_URL}?` 
            });
        } finally {
            setIsLoading(false);
        }
    };

    // 3. Render the Component
    return (
        <div className="app-container">
            <header className="app-header">
                <h1>♻️ Smart Waste Classifier</h1>
                <p>Upload an image to get instant classification and disposal instructions.</p>
            </header>

            <div className="content-area">
                
                {/* Image Upload Area */}
                <div className="upload-section">
                    <input 
                        type="file" 
                        accept="image/*" 
                        onChange={handleFileChange} 
                        disabled={isLoading}
                    />
                    <button 
                        onClick={handleUpload} 
                        disabled={!selectedFile || isLoading}
                    >
                        {isLoading ? 'Processing...' : 'Classify Waste'}
                    </button>
                </div>

                {/* Preview and Results */}
                <div className="results-section">
                    <div className="image-preview">
                        {previewUrl ? (
                            <img src={previewUrl} alt="Waste preview" />
                        ) : (
                            <div className="placeholder">Image Preview</div>
                        )}
                    </div>
                    
                    <div className="prediction-output">
                        {isLoading && (
                            <div className="loading-message">
                                Analyzing image... please wait.
                            </div>
                        )}
                        
                        {result.error && (
                            <div className="error-message">
                                <h3>Error:</h3>
                                <p>{result.error}</p>
                            </div>
                        )}

                        {result.class && (
                            <div className="success-output">
                                <h2>Predicted Class: <span className={`class-label ${result.class}`}>{result.class.toUpperCase()}</span></h2>
                                <p className="confidence">Confidence: {Math.round(result.confidence * 10000) / 100}%</p>
                                
                                <div className="instructions-box">
                                    <h3>Disposal Instruction:</h3>
                                    <p>{result.instruction}</p>
                                    <h3>Recycling Tip:</h3>
                                    <p>{result.tip}</p>
                                </div>
                            </div>
                        )}
                    </div>
                </div>

            </div>
        </div>
    );
}

export default App;