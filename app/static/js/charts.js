// Dashboard Chart.js Integration
document.addEventListener('DOMContentLoaded', function () {
    const volumeCanvas = document.getElementById('volumeChart');
    const nutritionCanvas = document.getElementById('nutritionChart');
    const habitsCanvas = document.getElementById('habitsChart');

    if (!volumeCanvas && !nutritionCanvas && !habitsCanvas) return;

    fetch('/dashboard/api/chart-data')
        .then(response => response.json())
        .then(data => {
            // 1. Workout Volume Chart
            if (volumeCanvas) {
                new Chart(volumeCanvas, {
                    type: 'bar',
                    data: {
                        labels: data.labels,
                        datasets: [{
                            label: 'Volume Moved (kg)',
                            data: data.volume,
                            backgroundColor: 'rgba(30, 58, 47, 0.75)',
                            borderColor: '#1E3A2F',
                            borderWidth: 1,
                            borderRadius: 6
                        }]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        plugins: {
                            legend: { display: false }
                        },
                        scales: {
                            y: {
                                beginAtZero: true,
                                title: { display: true, text: 'Total kg' }
                            }
                        }
                    }
                });
            }

            // 2. Nutrition Intake vs Target Chart
            if (nutritionCanvas) {
                new Chart(nutritionCanvas, {
                    type: 'bar',
                    data: {
                        labels: data.labels,
                        datasets: [
                            {
                                type: 'bar',
                                label: 'Logged Calories',
                                data: data.calories,
                                backgroundColor: 'rgba(141, 163, 153, 0.75)',
                                borderColor: '#8DA399',
                                borderWidth: 1,
                                borderRadius: 6
                            },
                            {
                                type: 'line',
                                label: 'Target Calories',
                                data: data.target_calories,
                                borderColor: '#1E3A2F',
                                borderWidth: 2,
                                borderDash: [6, 4],
                                pointRadius: 0,
                                fill: false
                            }
                        ]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        scales: {
                            y: {
                                beginAtZero: true,
                                title: { display: true, text: 'Calories (kcal)' }
                            }
                        }
                    }
                });
            }

            // 3. Habits Chart (Sleep & Water)
            if (habitsCanvas) {
                new Chart(habitsCanvas, {
                    type: 'line',
                    data: {
                        labels: data.labels,
                        datasets: [
                            {
                                label: 'Sleep (hours)',
                                data: data.sleep,
                                borderColor: '#2E6F40',
                                backgroundColor: 'rgba(46, 111, 64, 0.1)',
                                fill: true,
                                tension: 0.3,
                                yAxisID: 'y'
                            },
                            {
                                label: 'Water (ml)',
                                data: data.water,
                                borderColor: '#356D8A',
                                backgroundColor: 'rgba(53, 109, 138, 0.1)',
                                fill: false,
                                tension: 0.3,
                                yAxisID: 'y1'
                            }
                        ]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        scales: {
                            y: {
                                type: 'linear',
                                display: true,
                                position: 'left',
                                beginAtZero: true,
                                max: 12,
                                title: { display: true, text: 'Hours Sleep' }
                            },
                            y1: {
                                type: 'linear',
                                display: true,
                                position: 'right',
                                beginAtZero: true,
                                grid: { drawOnChartArea: false },
                                title: { display: true, text: 'Water (ml)' }
                            }
                        }
                    }
                });
            }
        })
        .catch(err => {
            console.warn('Could not load chart data:', err);
        });
});
