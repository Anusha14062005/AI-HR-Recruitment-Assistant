/**
 * Dashboard Charts for AI HR Recruitment Assistant
 */

function initDashboardCharts(data) {
    if (!data) return;

    // 1. Applicants per Job (Bar Chart)
    const ctxJobs = document.getElementById('chartApplicantsPerJob');
    if (ctxJobs && data.job_applicants) {
        new Chart(ctxJobs, {
            type: 'bar',
            data: {
                labels: data.job_applicants.labels,
                datasets: [{
                    label: 'Applicants',
                    data: data.job_applicants.values,
                    backgroundColor: 'rgba(79, 70, 229, 0.85)',
                    borderColor: 'rgb(79, 70, 229)',
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
                        ticks: { stepSize: 1 }
                    }
                }
            }
        });
    }

    // 2. Candidate Match Score Distribution (Doughnut Chart)
    const ctxScores = document.getElementById('chartScoreDistribution');
    if (ctxScores && data.scores) {
        new Chart(ctxScores, {
            type: 'doughnut',
            data: {
                labels: data.scores.labels,
                datasets: [{
                    data: data.scores.values,
                    backgroundColor: [
                        '#10b981', // Strong Match
                        '#f59e0b', // Potential Match
                        '#ef4444'  // Needs Review
                    ],
                    borderWidth: 2,
                    hoverOffset: 6
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: { boxWidth: 12, padding: 15 }
                    }
                },
                cutout: '70%'
            }
        });
    }

    // 3. Recruitment Status Breakdown (Polar / Pie Chart)
    const ctxStatus = document.getElementById('chartRecruitmentStatus');
    if (ctxStatus && data.status) {
        new Chart(ctxStatus, {
            type: 'pie',
            data: {
                labels: data.status.labels,
                datasets: [{
                    data: data.status.values,
                    backgroundColor: [
                        '#64748b', // New
                        '#06b6d4', // Under Review
                        '#4f46e5', // Shortlisted
                        '#f59e0b', // Interview Scheduled
                        '#10b981', // Selected
                        '#ef4444'  // Rejected
                    ],
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: { boxWidth: 12, padding: 12 }
                    }
                }
            }
        });
    }
}

