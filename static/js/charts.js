// Charts utility for NEET College Predictor

class ChartManager {
    constructor() {
        this.charts = {};
    }

    // Create a pie chart for score breakdown
    createScoreChart(containerId, scoreData) {
        const ctx = document.getElementById(containerId);
        if (!ctx) return null;

        const data = {
            labels: ['Correct Answers', 'Incorrect Answers', 'Unattempted'],
            datasets: [{
                data: [
                    scoreData.correct_answers,
                    scoreData.incorrect_answers,
                    scoreData.unattempted_questions
                ],
                backgroundColor: [
                    '#27ae60',  // Green for correct
                    '#e74c3c',  // Red for incorrect
                    '#95a5a6'   // Gray for unattempted
                ],
                borderColor: [
                    '#2ecc71',
                    '#c0392b',
                    '#7f8c8d'
                ],
                borderWidth: 2
            }]
        };

        const config = {
            type: 'pie',
            data: data,
            options: {
                responsive: true,
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: {
                            padding: 20,
                            usePointStyle: true
                        }
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                const label = context.label || '';
                                const value = context.parsed;
                                const total = context.dataset.data.reduce((a, b) => a + b, 0);
                                const percentage = ((value / total) * 100).toFixed(1);
                                return `${label}: ${value} (${percentage}%)`;
                            }
                        }
                    }
                }
            }
        };

        return new Chart(ctx, config);
    }

    // Create a bar chart for college comparison
    createCollegeChart(containerId, colleges) {
        const ctx = document.getElementById(containerId);
        if (!ctx) return null;

        const labels = colleges.map(college => college.name);
        const scores = colleges.map(college => college.min_score_general);

        const data = {
            labels: labels,
            datasets: [{
                label: 'Minimum Score (General)',
                data: scores,
                backgroundColor: 'rgba(52, 152, 219, 0.8)',
                borderColor: 'rgba(52, 152, 219, 1)',
                borderWidth: 2
            }]
        };

        const config = {
            type: 'bar',
            data: data,
            options: {
                responsive: true,
                scales: {
                    y: {
                        beginAtZero: true,
                        max: 720,
                        title: {
                            display: true,
                            text: 'NEET Score'
                        }
                    },
                    x: {
                        title: {
                            display: true,
                            text: 'Colleges'
                        }
                    }
                },
                plugins: {
                    legend: {
                        display: false
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                return `Score: ${context.parsed.y}`;
                            }
                        }
                    }
                }
            }
        };

        return new Chart(ctx, config);
    }

    // Create a line chart for score trends
    createTrendChart(containerId, trendData) {
        const ctx = document.getElementById(containerId);
        if (!ctx) return null;

        const data = {
            labels: trendData.labels,
            datasets: [{
                label: 'Score Trend',
                data: trendData.scores,
                borderColor: 'rgba(52, 152, 219, 1)',
                backgroundColor: 'rgba(52, 152, 219, 0.1)',
                borderWidth: 3,
                fill: true,
                tension: 0.4
            }]
        };

        const config = {
            type: 'line',
            data: data,
            options: {
                responsive: true,
                scales: {
                    y: {
                        beginAtZero: true,
                        max: 720,
                        title: {
                            display: true,
                            text: 'NEET Score'
                        }
                    },
                    x: {
                        title: {
                            display: true,
                            text: 'Year'
                        }
                    }
                },
                plugins: {
                    legend: {
                        display: false
                    }
                }
            }
        };

        return new Chart(ctx, config);
    }

    // Create a radar chart for college comparison
    createRadarChart(containerId, collegeData) {
        const ctx = document.getElementById(containerId);
        if (!ctx) return null;

        const data = {
            labels: ['Ranking', 'Infrastructure', 'Faculty', 'Research', 'Placement', 'Fees'],
            datasets: [{
                label: collegeData.name,
                data: [
                    collegeData.rank,
                    collegeData.infrastructure || 7,
                    collegeData.faculty || 8,
                    collegeData.research || 6,
                    collegeData.placement || 8,
                    collegeData.fees_rating || 5
                ],
                backgroundColor: 'rgba(52, 152, 219, 0.2)',
                borderColor: 'rgba(52, 152, 219, 1)',
                borderWidth: 2,
                pointBackgroundColor: 'rgba(52, 152, 219, 1)',
                pointBorderColor: '#fff',
                pointHoverBackgroundColor: '#fff',
                pointHoverBorderColor: 'rgba(52, 152, 219, 1)'
            }]
        };

        const config = {
            type: 'radar',
            data: data,
            options: {
                responsive: true,
                scales: {
                    r: {
                        beginAtZero: true,
                        max: 10,
                        ticks: {
                            stepSize: 2
                        }
                    }
                },
                plugins: {
                    legend: {
                        display: false
                    }
                }
            }
        };

        return new Chart(ctx, config);
    }

    // Destroy a chart
    destroyChart(chartId) {
        if (this.charts[chartId]) {
            this.charts[chartId].destroy();
            delete this.charts[chartId];
        }
    }

    // Update chart data
    updateChart(chartId, newData) {
        if (this.charts[chartId]) {
            this.charts[chartId].data = newData;
            this.charts[chartId].update();
        }
    }
}

// Global chart manager instance
window.chartManager = new ChartManager(); 