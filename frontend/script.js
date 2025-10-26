// File upload functionality
class FileUploader {
    constructor() {
        this.selectedFiles = [];
        this.uploadArea = document.getElementById('uploadArea');
        this.fileInput = document.getElementById('fileInput');
        this.fileList = document.getElementById('fileList');
        this.uploadBtn = document.getElementById('uploadBtn');
        this.clearBtn = document.getElementById('clearBtn');
        this.uploadProgress = document.getElementById('uploadProgress');
        this.progressFill = document.getElementById('progressFill');
        this.progressText = document.getElementById('progressText');
        this.uploadStatus = document.getElementById('uploadStatus');

        this.initEventListeners();
    }

    initEventListeners() {
        // Click to select files - only on upload area background, not buttons
        this.uploadArea.addEventListener('click', (e) => {
            // Only trigger file input if clicking on the upload area background, not on buttons
            if (e.target === this.uploadArea || e.target.classList.contains('upload-content')) {
                this.fileInput.click();
            }
        });

        // File input change
        this.fileInput.addEventListener('change', (e) => {
            this.handleFiles(e.target.files);
        });

        // Drag and drop
        this.uploadArea.addEventListener('dragover', (e) => {
            e.preventDefault();
            this.uploadArea.classList.add('dragover');
        });

        this.uploadArea.addEventListener('dragleave', () => {
            this.uploadArea.classList.remove('dragover');
        });

        this.uploadArea.addEventListener('drop', (e) => {
            e.preventDefault();
            this.uploadArea.classList.remove('dragover');
            this.handleFiles(e.dataTransfer.files);
        });

        // Upload button
        this.uploadBtn.addEventListener('click', () => {
            this.uploadFiles();
        });

        // Clear button
        this.clearBtn.addEventListener('click', () => {
            this.clearFiles();
        });
    }

    handleFiles(files) {
        const newFiles = Array.from(files);
        this.selectedFiles = [...this.selectedFiles, ...newFiles];
        this.updateFileList();
        this.updateButtons();
    }

    updateFileList() {
        this.fileList.innerHTML = '';
        
        this.selectedFiles.forEach((file, index) => {
            const fileItem = document.createElement('div');
            fileItem.className = 'file-item';
            
            const fileIcon = this.getFileIcon(file.type);
            const fileSize = this.formatFileSize(file.size);
            
            fileItem.innerHTML = `
                <div class="file-info">
                    <span class="file-icon">${fileIcon}</span>
                    <div class="file-details">
                        <div class="file-name">${file.name}</div>
                        <div class="file-size">${fileSize}</div>
                    </div>
                </div>
                <button class="remove-file" onclick="fileUploader.removeFile(${index})">Remove</button>
            `;
            
            this.fileList.appendChild(fileItem);
        });
    }

    removeFile(index) {
        this.selectedFiles.splice(index, 1);
        this.updateFileList();
        this.updateButtons();
    }

    clearFiles() {
        this.selectedFiles = [];
        this.fileInput.value = '';
        this.updateFileList();
        this.updateButtons();
        this.hideStatus();
    }

    updateButtons() {
        const hasFiles = this.selectedFiles.length > 0;
        this.uploadBtn.disabled = !hasFiles;
        this.clearBtn.disabled = !hasFiles;
    }

    getFileIcon(fileType) {
        if (fileType.startsWith('image/')) return '🖼️';
        if (fileType.startsWith('video/')) return '🎥';
        if (fileType.startsWith('audio/')) return '🎵';
        if (fileType.includes('pdf')) return '📄';
        if (fileType.includes('word')) return '📝';
        if (fileType.includes('excel') || fileType.includes('spreadsheet')) return '📊';
        if (fileType.includes('zip') || fileType.includes('rar')) return '📦';
        return '📁';
    }

    formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }

    async uploadFiles() {
        if (this.selectedFiles.length === 0) return;

        this.showProgress();
        this.hideStatus();

        const formData = new FormData();
        this.selectedFiles.forEach(file => {
            formData.append('files', file);
        });

        try {
            const response = await fetch('/upload', {
                method: 'POST',
                body: formData
            });

            if (response.ok) {
                const result = await response.json();
                console.log('Upload result:', result); // Debug log
                this.showStatus('success', `Successfully uploaded ${result.uploadedCount} file(s)!`);
                this.displayArtworkResults(result.uploadedFiles);
                this.clearFiles();
            } else {
                const error = await response.json();
                this.showStatus('error', `Upload failed: ${error.message}`);
            }
        } catch (error) {
            this.showStatus('error', `Upload failed: ${error.message}`);
        } finally {
            this.hideProgress();
        }
    }

    showProgress() {
        this.uploadProgress.style.display = 'block';
        this.uploadBtn.disabled = true;
        
        // Simulate progress (in real app, you'd track actual upload progress)
        let progress = 0;
        const interval = setInterval(() => {
            progress += Math.random() * 15;
            if (progress >= 100) {
                progress = 100;
                clearInterval(interval);
            }
            this.updateProgress(progress);
        }, 200);
    }

    updateProgress(percent) {
        this.progressFill.style.width = percent + '%';
        this.progressText.textContent = Math.round(percent) + '%';
    }

    hideProgress() {
        this.uploadProgress.style.display = 'none';
        this.progressFill.style.width = '0%';
        this.progressText.textContent = '0%';
        this.updateButtons();
    }

    showStatus(type, message) {
        this.uploadStatus.className = `upload-status ${type}`;
        this.uploadStatus.textContent = message;
        this.uploadStatus.style.display = 'block';
        
        // Auto-hide success messages after 5 seconds
        if (type === 'success') {
            setTimeout(() => {
                this.hideStatus();
            }, 5000);
        }
    }

    hideStatus() {
        this.uploadStatus.style.display = 'none';
    }

    displayArtworkResults(files) {
        // Get the results container and elements
        const resultsContainer = document.getElementById('artworkResults');
        const uploadedImage = document.getElementById('uploadedImage');
        const artworkName = document.getElementById('artworkName');
        const artworkDescription = document.getElementById('artworkDescription');

        // Find the first file with artwork analysis
        const fileWithAnalysis = files.find(file => file.artwork_analysis);
        
        if (fileWithAnalysis && fileWithAnalysis.artwork_analysis) {
            const analysis = fileWithAnalysis.artwork_analysis;
            
            // Display the uploaded image
            if (fileWithAnalysis.original_name && uploadedImage) {
                // Create a temporary URL for the uploaded image
                const imageUrl = `/uploads/${fileWithAnalysis.saved_name}`;
                uploadedImage.src = imageUrl;
                uploadedImage.style.display = 'block';
            }
            
            // Display artwork information
            if (artworkName) {
                artworkName.textContent = analysis.artwork_name || '-';
            }
            if (artworkDescription) {
                artworkDescription.textContent = 'Loading AI analysis...';
            }
            
            // Automatically load AI analysis into description
            this.loadAIAnalysisIntoDescription(analysis.artwork_name);
            
            // Automatically load suggestions
            this.loadSuggestions(analysis.artwork_name);

            // Show results container
            if (resultsContainer) {
                resultsContainer.style.display = 'block';
                
                // Scroll to results
                resultsContainer.scrollIntoView({ behavior: 'smooth', block: 'start' });
                
                // Auto-hide after 60 seconds
                setTimeout(() => {
                    resultsContainer.style.display = 'none';
                }, 60000);
            }
        }
    }

    async analyzeWithLLM(artworkName) {
        const analyzeBtn = document.getElementById('analyzeBtn');
        const analysisContent = document.getElementById('analysisContent');
        
        // Show loading state
        analyzeBtn.disabled = true;
        analyzeBtn.textContent = 'Analyzing...';
        analysisContent.innerHTML = `
            <div class="analysis-loading">
                <div class="loading-spinner"></div>
                <span>AI is analyzing the artwork...</span>
            </div>
        `;
        
        try {
            // Call the backend LLM analysis endpoint
            const response = await fetch(`/get_themes/${encodeURIComponent(artworkName)}`);
            const data = await response.json();
            
            if (data.success) {
                // Display the analysis result
                analysisContent.innerHTML = `
                    <div class="analysis-result">
                        <h4>📋 Detailed Analysis</h4>
                        <div style="white-space: pre-wrap; line-height: 1.6;">${data.themes}</div>
                    </div>
                `;
            } else {
                // Show error
                analysisContent.innerHTML = `
                    <div class="analysis-error">
                        <h4>❌ Analysis Failed</h4>
                        <p>${data.themes}</p>
                    </div>
                `;
            }
        } catch (error) {
            // Show error
            analysisContent.innerHTML = `
                <div class="analysis-error">
                    <h4>❌ Connection Error</h4>
                    <p>Failed to connect to AI analysis service: ${error.message}</p>
                </div>
            `;
        } finally {
            // Reset button
            analyzeBtn.disabled = false;
            analyzeBtn.textContent = 'Analyze with AI';
        }
    }

    async getSuggestions(artworkName) {
        const suggestionsBtn = document.getElementById('suggestionsBtn');
        const suggestionsContent = document.getElementById('suggestionsContent');
        
        // Show loading state
        suggestionsBtn.disabled = true;
        suggestionsBtn.textContent = 'Finding Similar Artworks...';
        suggestionsContent.innerHTML = `
            <div class="suggestions-loading">
                <div class="loading-spinner"></div>
                <span>AI is finding similar artworks...</span>
            </div>
        `;
        
        try {
            // Call the backend suggestions endpoint
            const response = await fetch(`/get_suggestions/${encodeURIComponent(artworkName)}`);
            const data = await response.json();
            
            if (data.success && data.suggestions && data.suggestions.length > 0) {
                // Display the suggestions result as cards
                const suggestionsHtml = data.suggestions.map((suggestion, index) => `
                    <div class="suggestion-item">
                        <div class="suggestion-number">${index + 1}</div>
                        <div class="suggestion-details">
                            <div class="suggestion-title">${suggestion.Name}</div>
                            <div class="suggestion-artist">by ${suggestion.Artist}</div>
                            <div class="suggestion-year">${suggestion.Year}</div>
                            <div class="suggestion-location">📍 ${suggestion['Current Location']}</div>
                            ${suggestion.Wikipedia ? `<a href="${suggestion.Wikipedia}" target="_blank" class="suggestion-link">🔗 Learn More</a>` : ''}
                        </div>
                    </div>
                `).join('');
                
                suggestionsContent.innerHTML = suggestionsHtml;
            } else {
                // Show error or no results
                suggestionsContent.innerHTML = `
                    <div class="suggestions-error">
                        <h4>❌ No Similar Artworks Found</h4>
                        <p>Unable to find similar artworks for "${artworkName}". This might be because the artwork is not well-known or the AI couldn't identify it properly.</p>
                    </div>
                `;
            }
        } catch (error) {
            // Show error
            suggestionsContent.innerHTML = `
                <div class="suggestions-error">
                    <h4>❌ Connection Error</h4>
                    <p>Failed to connect to suggestions service: ${error.message}</p>
                </div>
            `;
        } finally {
            // Reset button
            suggestionsBtn.disabled = false;
            suggestionsBtn.textContent = 'Get Similar Artworks';
        }
    }

    async loadAIAnalysisIntoDescription(artworkName) {
        const artworkDescription = document.getElementById('artworkDescription');
        
        if (!artworkDescription) return;
        
        if (!artworkName || artworkName === 'Artwork could not be found') {
            artworkDescription.textContent = 'Unable to analyze this artwork';
            return;
        }
        
        try {
            // Call the backend LLM analysis endpoint
            const response = await fetch(`/get_themes/${encodeURIComponent(artworkName)}`);
            const data = await response.json();
            
            if (data.success) {
                // Process the text to make Wikipedia links clickable
                let processedText = data.themes;
                
                // Find Wikipedia URLs and make them clickable
                const wikipediaRegex = /(https?:\/\/[^\s]+)/g;
                processedText = processedText.replace(wikipediaRegex, (url) => {
                    return `<a href="${url}" target="_blank" rel="noopener noreferrer">${url}</a>`;
                });
                
                // Display the analysis result in description
                artworkDescription.innerHTML = `<div style="white-space: pre-wrap; line-height: 1.5;">${processedText}</div>`;
            } else {
                // Show error
                artworkDescription.textContent = `Analysis failed: ${data.themes}`;
            }
        } catch (error) {
            // Show error
            artworkDescription.textContent = `Connection error: ${error.message}`;
        }
    }

    async loadSuggestions(artworkName) {
        const suggestionsContent = document.getElementById('suggestionsContent');
        
        if (!suggestionsContent) return;
        
        if (!artworkName || artworkName === 'Artwork could not be found') {
            suggestionsContent.innerHTML = `
                <div class="suggestions-error">
                    <h4>❌ No Suggestions Available</h4>
                    <p>Unable to find suggestions for this artwork.</p>
                </div>
            `;
            return;
        }
        
        // Show loading state
        suggestionsContent.innerHTML = `
            <div class="suggestions-loading">
                <div class="loading-spinner"></div>
                <span>AI is finding similar artworks...</span>
            </div>
        `;
        
        try {
            // Call the backend suggestions endpoint
            const response = await fetch(`/get_suggestions/${encodeURIComponent(artworkName)}`);
            const data = await response.json();
            
            if (data.success && data.suggestions && data.suggestions.length > 0) {
                // Display the suggestions result as cards
                const suggestionsHtml = data.suggestions.map((suggestion, index) => `
                    <div class="suggestion-item">
                        <div class="suggestion-number">${index + 1}</div>
                        <div class="suggestion-details">
                            <div class="suggestion-title">${suggestion.Name}</div>
                            <div class="suggestion-artist">by ${suggestion.Artist}</div>
                            <div class="suggestion-year">${suggestion.Year}</div>
                            <div class="suggestion-location">📍 ${suggestion['Current Location']}</div>
                            ${suggestion.Wikipedia ? `<a href="${suggestion.Wikipedia}" target="_blank" class="suggestion-link">🔗 Learn More</a>` : ''}
                        </div>
                    </div>
                `).join('');
                
                suggestionsContent.innerHTML = suggestionsHtml;
            } else {
                // Show error or no results
                suggestionsContent.innerHTML = `
                    <div class="suggestions-error">
                        <h4>❌ No Similar Artworks Found</h4>
                        <p>Unable to find similar artworks for "${artworkName}". This might be because the artwork is not well-known or the AI couldn't identify it properly.</p>
                    </div>
                `;
            }
        } catch (error) {
            // Show error
            suggestionsContent.innerHTML = `
                <div class="suggestions-error">
                    <h4>❌ Connection Error</h4>
                    <p>Failed to connect to suggestions service: ${error.message}</p>
                </div>
            `;
        }
    }
}

// Camera functionality
class CameraCapture {
    constructor() {
        this.stream = null;
        this.video = null;
        this.canvas = null;
        this.capturedImage = null;
        this.isCaptured = false;
        
        this.initElements();
        this.bindEvents();
    }
    
    initElements() {
        this.cameraBtn = document.getElementById('cameraBtn');
        this.cameraModal = document.getElementById('cameraModal');
        this.closeCameraBtn = document.getElementById('closeCameraBtn');
        this.video = document.getElementById('cameraVideo');
        this.canvas = document.getElementById('cameraCanvas');
        this.captureBtn = document.getElementById('captureBtn');
        this.retakeBtn = document.getElementById('retakeBtn');
        this.usePhotoBtn = document.getElementById('usePhotoBtn');
    }
    
    bindEvents() {
        this.cameraBtn.addEventListener('click', (e) => {
            e.preventDefault();
            e.stopPropagation();
            this.openCamera();
        });
        this.closeCameraBtn.addEventListener('click', () => this.closeCamera());
        this.captureBtn.addEventListener('click', () => this.capturePhoto());
        this.retakeBtn.addEventListener('click', () => this.retakePhoto());
        this.usePhotoBtn.addEventListener('click', () => this.usePhoto());
        
        // Close modal when clicking outside
        this.cameraModal.addEventListener('click', (e) => {
            if (e.target === this.cameraModal) {
                this.closeCamera();
            }
        });
    }
    
    async openCamera() {
        try {
            this.cameraModal.style.display = 'flex';
            
            // Request camera access
            this.stream = await navigator.mediaDevices.getUserMedia({ 
                video: { 
                    width: { ideal: 1280 },
                    height: { ideal: 720 },
                    facingMode: 'environment' // Use back camera if available
                } 
            });
            
            this.video.srcObject = this.stream;
            this.video.play();
            
            // Reset state
            this.isCaptured = false;
            this.capturedImage = null;
            this.updateButtonStates();
            
        } catch (error) {
            console.error('Error accessing camera:', error);
            alert('Unable to access camera. Please check permissions and try again.');
            this.closeCamera();
        }
    }
    
    closeCamera() {
        // Stop camera stream
        if (this.stream) {
            this.stream.getTracks().forEach(track => track.stop());
            this.stream = null;
        }
        
        // Hide modal
        this.cameraModal.style.display = 'none';
        
        // Reset video
        if (this.video) {
            this.video.srcObject = null;
        }
        
        // Reset state
        this.isCaptured = false;
        this.capturedImage = null;
    }
    
    capturePhoto() {
        if (!this.video || !this.canvas) return;
        
        // Set canvas dimensions to match video
        this.canvas.width = this.video.videoWidth;
        this.canvas.height = this.video.videoHeight;
        
        // Draw video frame to canvas
        const ctx = this.canvas.getContext('2d');
        ctx.drawImage(this.video, 0, 0);
        
        // Convert canvas to blob
        this.canvas.toBlob((blob) => {
            this.capturedImage = blob;
            this.isCaptured = true;
            this.updateButtonStates();
            
            // Show captured image
            this.video.style.display = 'none';
            this.canvas.style.display = 'block';
            
        }, 'image/jpeg', 0.8);
    }
    
    retakePhoto() {
        this.isCaptured = false;
        this.capturedImage = null;
        this.updateButtonStates();
        
        // Show video again
        this.video.style.display = 'block';
        this.canvas.style.display = 'none';
    }
    
    usePhoto() {
        if (!this.capturedImage) return;
        
        // Create a file from the blob
        const file = new File([this.capturedImage], 'camera-photo.jpg', {
            type: 'image/jpeg',
            lastModified: Date.now()
        });
        
        // Add to file uploader using handleFiles method
        if (window.fileUploader) {
            window.fileUploader.handleFiles([file]);
        }
        
        // Close camera
        this.closeCamera();
        
        // Show success message
        const status = document.getElementById('uploadStatus');
        status.innerHTML = '<div class="success-message">📷 Photo captured and added for analysis!</div>';
        status.style.display = 'block';
        
        setTimeout(() => {
            status.style.display = 'none';
        }, 3000);
    }
    
    updateButtonStates() {
        if (this.isCaptured) {
            this.captureBtn.style.display = 'none';
            this.retakeBtn.style.display = 'inline-block';
            this.usePhotoBtn.style.display = 'inline-block';
        } else {
            this.captureBtn.style.display = 'inline-block';
            this.retakeBtn.style.display = 'none';
            this.usePhotoBtn.style.display = 'none';
        }
    }
}

// Initialize the file uploader and camera when the page loads
let fileUploader;
let cameraCapture;
document.addEventListener('DOMContentLoaded', () => {
    fileUploader = new FileUploader();
    cameraCapture = new CameraCapture();
    
    // Make fileUploader globally accessible for camera
    window.fileUploader = fileUploader;
});
