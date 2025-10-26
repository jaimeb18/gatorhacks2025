// Architecture recognition JavaScript
document.addEventListener('DOMContentLoaded', function() {
    const fileInput = document.getElementById('fileInput');
    const uploadBtn = document.getElementById('uploadBtn');
    const clearBtn = document.getElementById('clearBtn');
    const fileList = document.getElementById('fileList');
    const uploadProgress = document.getElementById('uploadProgress');
    const progressFill = document.getElementById('progressFill');
    const progressText = document.getElementById('progressText');
    const uploadStatus = document.getElementById('uploadStatus');
    const architectureResults = document.getElementById('architectureResults');
    
    let selectedFiles = [];
    
    // File input change
    if (fileInput) {
        fileInput.addEventListener('change', function(e) {
            handleFiles(e.target.files);
        });
    }
    
    // Upload button
    if (uploadBtn) {
        uploadBtn.addEventListener('click', function() {
            if (selectedFiles.length > 0) {
                uploadFiles();
            }
        });
    }
    
    // Clear button
    if (clearBtn) {
        clearBtn.addEventListener('click', function() {
            clearFiles();
        });
    }
    
    function handleFiles(files) {
        selectedFiles = Array.from(files);
        displayFiles();
        updateButtons();
    }
    
    function displayFiles() {
        fileList.innerHTML = '';
        selectedFiles.forEach((file, index) => {
            const fileItem = document.createElement('div');
            fileItem.className = 'file-item';
            fileItem.innerHTML = `
                <div class="file-info">
                    <div class="file-icon">🖼️</div>
                    <div class="file-details">
                        <div class="file-name">${file.name}</div>
                        <div class="file-size">${(file.size / 1024).toFixed(2)} KB</div>
                    </div>
                </div>
                <button class="remove-file" onclick="removeFile(${index})">Remove</button>
            `;
            fileList.appendChild(fileItem);
        });
    }
    
    function updateButtons() {
        uploadBtn.disabled = selectedFiles.length === 0;
        clearBtn.disabled = selectedFiles.length === 0;
    }
    
    function clearFiles() {
        selectedFiles = [];
        fileInput.value = '';
        fileList.innerHTML = '';
        architectureResults.style.display = 'none';
        updateButtons();
    }
    
    function removeFile(index) {
        selectedFiles.splice(index, 1);
        displayFiles();
        updateButtons();
    }
    
    async function uploadFiles() {
        if (selectedFiles.length === 0) return;
        
        const formData = new FormData();
        selectedFiles.forEach(file => {
            formData.append('files', file);
        });
        
        uploadProgress.style.display = 'block';
        progressFill.style.width = '0%';
        
        try {
            progressFill.style.width = '30%';
            progressText.textContent = 'Uploading image...';
            
            const response = await fetch('/upload_architecture', {
                method: 'POST',
                body: formData
            });
            
            progressFill.style.width = '60%';
            progressText.textContent = 'Analyzing architecture...';
            
            const data = await response.json();
            
            progressFill.style.width = '100%';
            progressText.textContent = 'Complete!';
            
            if (response.ok && data.uploadedFiles && data.uploadedFiles.length > 0) {
                const uploadedFile = data.uploadedFiles[0];
                if (uploadedFile.architecture_analysis) {
                    displayResults(uploadedFile);
                }
                uploadStatus.className = 'upload-status success';
                uploadStatus.textContent = data.message;
            } else {
                throw new Error(data.error || 'Upload failed');
            }
            
        } catch (error) {
            console.error('Upload error:', error);
            uploadStatus.className = 'upload-status error';
            uploadStatus.textContent = `Error: ${error.message}`;
            progressFill.style.width = '0%';
        } finally {
            setTimeout(() => {
                uploadProgress.style.display = 'none';
            }, 2000);
        }
    }
    
    async function displayResults(fileInfo) {
        const analysis = fileInfo.architecture_analysis;
        const imageUrl = `/uploads/${fileInfo.saved_name}`;
        
        // Show the uploaded image
        const architectureImage = document.getElementById('uploadedImage');
        if (architectureImage) {
            architectureImage.src = imageUrl;
        }
        
        // Display architecture name
        const architectureName = document.getElementById('architectureName');
        if (architectureName) {
            architectureName.textContent = analysis.artwork_name || 'Unknown Building';
        }
        
        // Display description - temporarily show loading
        const architectureDescription = document.getElementById('architectureDescription');
        if (architectureDescription) {
            architectureDescription.innerHTML = 'Loading description...';
        }
        
        // Show results
        architectureResults.style.display = 'block';
        architectureResults.scrollIntoView({ behavior: 'smooth' });
        
        // Load detailed description from LLM
        await loadArchitectureDetails(analysis.artwork_name);
        
        // Load architecture suggestions
        loadArchitectureSuggestions(analysis.artwork_name);
    }
    
    async function loadArchitectureDetails(buildingName) {
        try {
            const architectureDescription = document.getElementById('architectureDescription');
            if (!architectureDescription) return;
            
            const response = await fetch(`/get_architecture_details/${encodeURIComponent(buildingName)}`);
            const data = await response.json();
            
            if (data.success && data.details) {
                // Display the LLM-generated description with proper line breaks and clickable URLs
                let formattedText = data.details.split('\n').join('<br>');
                
                // Convert URLs to clickable links
                const urlRegex = /(https?:\/\/[^\s]+)/g;
                formattedText = formattedText.replace(urlRegex, (url) => {
                    return `<a href="${url}" target="_blank" rel="noopener noreferrer" style="color: #0066cc; text-decoration: underline;">${url}</a>`;
                });
                
                architectureDescription.innerHTML = formattedText;
            } else {
                architectureDescription.textContent = data.details || 'Unable to load description.';
            }
        } catch (error) {
            console.error('Error loading architecture details:', error);
            const architectureDescription = document.getElementById('architectureDescription');
            if (architectureDescription) {
                architectureDescription.textContent = 'Error loading description.';
            }
        }
    }
    
    async function loadArchitectureSuggestions(buildingName) {
        try {
            const suggestionsContent = document.getElementById('suggestionsContent');
            if (!suggestionsContent) return;
            
            suggestionsContent.innerHTML = '<div class="suggestions-placeholder"><p>Loading similar architecture...</p></div>';
            
            const response = await fetch(`/get_architecture_suggestions/${encodeURIComponent(buildingName)}`);
            const data = await response.json();
            
            if (data.success && data.suggestions && data.suggestions.length > 0) {
                const suggestionsHtml = data.suggestions.map((building, index) => `
                    <div class="suggestion-item">
                        <div class="suggestion-number">${index + 1}</div>
                        <div class="suggestion-details">
                            <div class="suggestion-title">${building.Name || 'Unknown'}</div>
                            <div class="suggestion-artist">${building['Type Of Architecture'] || 'Unknown'}</div>
                            <div class="suggestion-year">${building.Era || 'Unknown'} Era</div>
                            <div class="suggestion-location">📍 ${building.Location || 'Unknown Location'}</div>
                            <div style="display: flex; gap: 8px; margin-top: 8px; flex-wrap: wrap;">
                                ${building['Wikipedia'] ? `<a href="${building['Wikipedia']}" target="_blank" class="suggestion-link" style="margin-right: 8px;">🔗 Learn More</a>` : ''}
                                ${building['Address'] ? `<a href="${building['Address']}" target="_blank" class="suggestion-link">📍 View on Maps</a>` : ''}
                            </div>
                        </div>
                    </div>
                `).join('');
                
                suggestionsContent.innerHTML = suggestionsHtml;
            } else {
                suggestionsContent.innerHTML = '<div class="suggestions-placeholder"><p>No architecture suggestions available</p></div>';
            }
        } catch (error) {
            console.error('Error loading suggestions:', error);
            const suggestionsContent = document.getElementById('suggestionsContent');
            if (suggestionsContent) {
                suggestionsContent.innerHTML = '<div class="suggestions-placeholder"><p>Error loading suggestions</p></div>';
            }
        }
    }
    
    // Make removeFile available globally
    window.removeFile = removeFile;
    
    // Drag and drop functionality
    const uploadArea = document.getElementById('uploadArea');
    if (uploadArea) {
        ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
            uploadArea.addEventListener(eventName, preventDefaults, false);
        });
        
        function preventDefaults(e) {
            e.preventDefault();
            e.stopPropagation();
        }
        
        uploadArea.addEventListener('drop', function(e) {
            const dt = e.dataTransfer;
            const files = dt.files;
            handleFiles(files);
        });
    }
});

