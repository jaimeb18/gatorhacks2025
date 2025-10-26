// Food recognition JavaScript
document.addEventListener('DOMContentLoaded', function() {
    const fileInput = document.getElementById('fileInput');
    const uploadBtn = document.getElementById('uploadBtn');
    const clearBtn = document.getElementById('clearBtn');
    const fileList = document.getElementById('fileList');
    const uploadProgress = document.getElementById('uploadProgress');
    const progressFill = document.getElementById('progressFill');
    const progressText = document.getElementById('progressText');
    const uploadStatus = document.getElementById('uploadStatus');
    const foodResults = document.getElementById('foodResults');
    
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
        foodResults.style.display = 'none';
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
            
            const response = await fetch('/upload_food', {
                method: 'POST',
                body: formData
            });
            
            progressFill.style.width = '60%';
            progressText.textContent = 'Analyzing food...';
            
            const data = await response.json();
            
            progressFill.style.width = '100%';
            progressText.textContent = 'Complete!';
            
            if (response.ok && data.uploadedFiles && data.uploadedFiles.length > 0) {
                const uploadedFile = data.uploadedFiles[0];
                if (uploadedFile.food_analysis) {
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
    
    function displayResults(fileInfo) {
        const analysis = fileInfo.food_analysis;
        const imageUrl = `/uploads/${fileInfo.saved_name}`;
        
        // Show the uploaded image
        const foodImage = document.getElementById('uploadedFoodImage');
        if (foodImage) {
            foodImage.src = imageUrl;
        }
        
        // Display food name
        const foodName = document.getElementById('foodName');
        if (foodName) {
            foodName.textContent = analysis.food_name || 'Unknown Food';
        }
        
        // Display description
        const foodDescription = document.getElementById('foodDescription');
        if (foodDescription) {
            let description = `Type: ${analysis.food_type || 'General'}\n`;
            description += `Confidence: ${(analysis.confidence * 100).toFixed(1)}%\n\n`;
            
            if (analysis.food_labels && analysis.food_labels.length > 0) {
                description += 'Detected Items:\n';
                analysis.food_labels.slice(0, 5).forEach(label => {
                    description += `• ${label.description} (${(label.confidence * 100).toFixed(0)}%)\n`;
                });
            }
            
            foodDescription.textContent = description;
        }
        
        // Show results
        foodResults.style.display = 'block';
        foodResults.scrollIntoView({ behavior: 'smooth' });
        
        // Load restaurant suggestions with user's location
        const locationInput = document.getElementById('locationInput');
        const location = locationInput ? locationInput.value : 'New York';
        loadRestaurantSuggestions(analysis.food_name, location);
    }
    
    async function loadRestaurantSuggestions(foodName, location = 'New York') {
        try {
            const suggestionsContent = document.getElementById('suggestionsContent');
            if (!suggestionsContent) return;
            
            suggestionsContent.innerHTML = '<div class="suggestions-placeholder"><p>Loading restaurant suggestions...</p></div>';
            
            const response = await fetch(`/get_food_suggestions/${encodeURIComponent(foodName)}?location=${encodeURIComponent(location)}`);
            const data = await response.json();
            
            if (data.success && data.suggestions && data.suggestions.length > 0) {
                const suggestionsHtml = data.suggestions.map((restaurant, index) => `
                    <div class="suggestion-item">
                        <div class="suggestion-number">${index + 1}</div>
                        <div class="suggestion-details">
                            <div class="suggestion-title">${restaurant['Restaurant Name'] || 'Unknown'}</div>
                            <div class="suggestion-artist">${restaurant['Cuisine'] || 'Unknown Cuisine'}</div>
                            <div class="suggestion-year">Average Cost: ${restaurant['Average Costs'] || 'Unknown'}</div>
                            <div class="suggestion-location">⭐ ${restaurant['Yelp Stars'] || 'Unknown'} Rating</div>
                            ${restaurant['Address'] ? `<a href="${restaurant['Address']}" target="_blank" class="suggestion-link">View on Maps</a>` : ''}
                        </div>
                    </div>
                `).join('');
                
                suggestionsContent.innerHTML = suggestionsHtml;
            } else {
                suggestionsContent.innerHTML = '<div class="suggestions-placeholder"><p>No restaurant suggestions available</p></div>';
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
