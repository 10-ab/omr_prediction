// NEET College Predictor - Main JavaScript

class NEETCollegePredictor {
    constructor() {
        this.currentScore = 0;
        this.states = [];
        this.categories = ['General', 'OBC', 'SC', 'ST', 'EWS'];
        this.rounds = ['Round 1', 'Round 2', 'Mop Up'];
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.loadStates();
        this.setupDragAndDrop();
        this.addAnimations();
    }

    setupEventListeners() {
        // File upload handling
        const fileInput = document.getElementById('omrFile');
        if (fileInput) {
            fileInput.addEventListener('change', (e) => this.handleFileUpload(e));
        }

        // College prediction form
        const predictionForm = document.getElementById('predictionForm');
        if (predictionForm) {
            predictionForm.addEventListener('submit', (e) => this.handlePredictionSubmit(e));
        }

        // Smooth scrolling for navigation links
        document.querySelectorAll('a[href^="#"]').forEach(anchor => {
            anchor.addEventListener('click', (e) => {
                e.preventDefault();
                const target = document.querySelector(anchor.getAttribute('href'));
                if (target) {
                    target.scrollIntoView({
                        behavior: 'smooth',
                        block: 'start'
                    });
                }
            });
        });

        // Auto-fill score from OMR processing
        const scoreInput = document.getElementById('score');
        if (scoreInput) {
            scoreInput.addEventListener('input', (e) => {
                this.currentScore = parseInt(e.target.value) || 0;
            });
        }
    }

    setupDragAndDrop() {
        const uploadArea = document.getElementById('uploadArea');
        if (!uploadArea) return;

        uploadArea.addEventListener('dragover', (e) => {
            e.preventDefault();
            uploadArea.classList.add('dragover');
        });

        uploadArea.addEventListener('dragleave', () => {
            uploadArea.classList.remove('dragover');
        });

        uploadArea.addEventListener('drop', (e) => {
            e.preventDefault();
            uploadArea.classList.remove('dragover');
            const files = e.dataTransfer.files;
            if (files.length > 0) {
                this.handleFileUpload({ target: { files: files } });
            }
        });

        // Click to upload
        uploadArea.addEventListener('click', () => {
            document.getElementById('omrFile').click();
        });
    }

    addAnimations() {
        // Add fade-in animation to cards
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('fade-in');
                }
            });
        }, { threshold: 0.1 });

        document.querySelectorAll('.card').forEach(card => {
            observer.observe(card);
        });
    }

    async loadStates() {
        try {
            const response = await fetch('/get_states');
            const data = await response.json();
            this.states = data.states;
            this.populateStateSelect();
        } catch (error) {
            console.error('Error loading states:', error);
            this.showNotification('Error loading states', 'error');
        }
    }

    populateStateSelect() {
        const stateSelect = document.getElementById('state');
        if (!stateSelect) return;

        stateSelect.innerHTML = '<option value="">Select State</option>';
        this.states.forEach(state => {
            const option = document.createElement('option');
            option.value = state;
            option.textContent = state;
            stateSelect.appendChild(option);
        });
    }

    handleFileUpload(event) {
        const file = event.target.files[0];
        if (!file) return;

        if (!file.type.startsWith('image/')) {
            this.showNotification('Please upload an image file', 'error');
            return;
        }

        this.uploadOMR(file);
    }

    async uploadOMR(file) {
        const formData = new FormData();
        formData.append('omr_image', file);

        this.showLoading(true);
        this.hideScoreResult();

        try {
            const response = await fetch('/upload_omr', {
                method: 'POST',
                body: formData
            });

            const data = await response.json();
            this.showLoading(false);

            if (data.success) {
                this.displayScore(data.score_result);
                this.currentScore = data.score_result.total_score;
                this.updateScoreInput();
                this.showNotification('OMR processed successfully!', 'success');
            } else {
                this.showNotification('Error: ' + data.error, 'error');
            }
        } catch (error) {
            this.showLoading(false);
            this.showNotification('Error uploading file: ' + error.message, 'error');
        }
    }

    async handlePredictionSubmit(event) {
        event.preventDefault();

        const formData = {
            score: parseInt(document.getElementById('score').value),
            caste: document.getElementById('caste').value,
            state: document.getElementById('state').value,
            round: document.getElementById('round').value
        };

        // Validate form
        if (!this.validatePredictionForm(formData)) {
            return;
        }

        try {
            const response = await fetch('/predict_colleges', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(formData)
            });

            const data = await response.json();

            if (data.success) {
                this.displayPredictions(data.prediction);
                this.showNotification('College predictions generated!', 'success');
            } else {
                this.showNotification('Error: ' + data.error, 'error');
            }
        } catch (error) {
            this.showNotification('Error predicting colleges: ' + error.message, 'error');
        }
    }

    validatePredictionForm(formData) {
        if (!formData.score || formData.score < 0 || formData.score > 720) {
            this.showNotification('Please enter a valid NEET score (0-720)', 'error');
            return false;
        }

        if (!formData.caste) {
            this.showNotification('Please select your category', 'error');
            return false;
        }

        if (!formData.state) {
            this.showNotification('Please select your state', 'error');
            return false;
        }

        if (!formData.round) {
            this.showNotification('Please select counselling round', 'error');
            return false;
        }

        return true;
    }

    displayScore(scoreResult) {
        const elements = {
            totalScore: document.getElementById('totalScore'),
            correctAnswers: document.getElementById('correctAnswers'),
            incorrectAnswers: document.getElementById('incorrectAnswers'),
            unattempted: document.getElementById('unattempted'),
            scoreResult: document.getElementById('scoreResult')
        };

        if (elements.totalScore) elements.totalScore.textContent = scoreResult.total_score;
        if (elements.correctAnswers) elements.correctAnswers.textContent = scoreResult.correct_answers;
        if (elements.incorrectAnswers) elements.incorrectAnswers.textContent = scoreResult.incorrect_answers;
        if (elements.unattempted) elements.unattempted.textContent = scoreResult.unattempted_questions;

        if (elements.scoreResult) {
            elements.scoreResult.style.display = 'block';
            elements.scoreResult.classList.add('fade-in');
        }
    }

    displayPredictions(prediction) {
        const collegeList = document.getElementById('collegeList');
        if (!collegeList) return;

        collegeList.innerHTML = '';

        // Display predicted college
        if (prediction.predicted_college) {
            const predictedDiv = document.createElement('div');
            predictedDiv.className = 'alert alert-success fade-in';
            predictedDiv.innerHTML = `
                <h5><i class="fas fa-star me-2"></i>Top Prediction</h5>
                <p class="mb-0"><strong>${prediction.predicted_college}</strong></p>
                <small>Confidence: ${(prediction.confidence * 100).toFixed(1)}%</small>
            `;
            collegeList.appendChild(predictedDiv);
        }

        // Display recommended colleges
        if (prediction.recommended_colleges && prediction.recommended_colleges.length > 0) {
            const recommendedDiv = document.createElement('div');
            recommendedDiv.innerHTML = '<h5 class="mt-4 mb-3"><i class="fas fa-list me-2"></i>Recommended Colleges</h5>';
            
            prediction.recommended_colleges.forEach((college, index) => {
                const isGovernment = this.isGovernmentCollege(college);
                
                const collegeCard = document.createElement('div');
                collegeCard.className = `college-card ${isGovernment ? 'government' : 'private'} fade-in`;
                collegeCard.style.animationDelay = `${index * 0.1}s`;
                
                collegeCard.innerHTML = `
                    <div class="d-flex justify-content-between align-items-center">
                        <div>
                            <h6 class="mb-1">${college}</h6>
                            <small class="text-muted">
                                <i class="fas fa-${isGovernment ? 'landmark' : 'building'} me-1"></i>
                                ${isGovernment ? 'Government' : 'Private'} Medical College
                            </small>
                        </div>
                        <span class="badge bg-${isGovernment ? 'success' : 'warning'}">${index + 1}</span>
                    </div>
                `;
                recommendedDiv.appendChild(collegeCard);
            });
            
            collegeList.appendChild(recommendedDiv);
        }

        const predictionResult = document.getElementById('predictionResult');
        if (predictionResult) {
            predictionResult.style.display = 'block';
            predictionResult.classList.add('fade-in');
        }
    }

    isGovernmentCollege(college) {
        const governmentKeywords = ['AIIMS', 'JIPMER', 'MAMC', 'GMC', 'BHU', 'AMU', 'JNU', 'DU', 'KGMU', 'IMS', 'LHMC', 'UCMS', 'VMMC', 'Safdarjung', 'RML', 'Lady Hardinge'];
        return governmentKeywords.some(keyword => college.includes(keyword));
    }

    showLoading(show) {
        const loading = document.getElementById('loading');
        if (loading) {
            loading.style.display = show ? 'block' : 'none';
        }
    }

    hideScoreResult() {
        const scoreResult = document.getElementById('scoreResult');
        if (scoreResult) {
            scoreResult.style.display = 'none';
        }
    }

    updateScoreInput() {
        const scoreInput = document.getElementById('score');
        if (scoreInput) {
            scoreInput.value = this.currentScore;
        }
    }

    showNotification(message, type = 'info') {
        // Create notification element
        const notification = document.createElement('div');
        notification.className = `alert alert-${type === 'error' ? 'warning' : type === 'success' ? 'success' : 'info'} notification`;
        notification.style.cssText = `
            position: fixed;
            top: 100px;
            right: 20px;
            z-index: 9999;
            min-width: 300px;
            animation: slideIn 0.3s ease-out;
        `;
        notification.innerHTML = `
            <i class="fas fa-${type === 'error' ? 'exclamation-triangle' : type === 'success' ? 'check-circle' : 'info-circle'} me-2"></i>
            ${message}
        `;

        document.body.appendChild(notification);

        // Remove notification after 5 seconds
        setTimeout(() => {
            notification.style.animation = 'slideOut 0.3s ease-out';
            setTimeout(() => {
                if (notification.parentNode) {
                    notification.parentNode.removeChild(notification);
                }
            }, 300);
        }, 5000);
    }

    // Utility methods
    formatNumber(num) {
        return num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
    }

    calculatePercentage(part, total) {
        return total > 0 ? ((part / total) * 100).toFixed(1) : 0;
    }

    // Chart creation (if needed)
    createScoreChart(scoreResult) {
        // This could be used to create charts with Chart.js or similar
        const ctx = document.getElementById('scoreChart');
        if (!ctx) return;

        // Example chart creation
        const data = {
            labels: ['Correct', 'Incorrect', 'Unattempted'],
            datasets: [{
                data: [
                    scoreResult.correct_answers,
                    scoreResult.incorrect_answers,
                    scoreResult.unattempted_questions
                ],
                backgroundColor: ['#27ae60', '#e74c3c', '#95a5a6']
            }]
        };

        // Chart.js implementation would go here
    }
}

// Initialize the application when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.neetApp = new NEETCollegePredictor();
});

// Add CSS animations for notifications
const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from { transform: translateX(100%); opacity: 0; }
        to { transform: translateX(0); opacity: 1; }
    }
    
    @keyframes slideOut {
        from { transform: translateX(0); opacity: 1; }
        to { transform: translateX(100%); opacity: 0; }
    }
    
    .notification {
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    }
`;
document.head.appendChild(style); 