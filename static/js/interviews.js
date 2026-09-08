/**
 * Interview Management and Evaluation Score Calculator
 */

document.addEventListener('DOMContentLoaded', () => {
    // Live evaluation score calculator
    const ratingInputs = document.querySelectorAll('.eval-rating-input');
    const overallDisplay = document.getElementById('overallScoreDisplay');
    const overallProgress = document.getElementById('overallScoreProgress');

    function calculateEvaluationScore() {
        if (!ratingInputs.length) return;
        let total = 0;
        let count = 0;
        ratingInputs.forEach(input => {
            total += parseInt(input.value || 3, 10);
            count++;
        });
        const maxTotal = count * 5;
        const pct = Math.round((total / maxTotal) * 100);

        if (overallDisplay) {
            overallDisplay.textContent = `${pct}%`;
        }
        if (overallProgress) {
            overallProgress.style.width = `${pct}%`;
            overallProgress.className = `progress-bar ${pct >= 85 ? 'bg-success' : pct >= 70 ? 'bg-warning' : 'bg-danger'}`;
        }
    }

    ratingInputs.forEach(input => {
        input.addEventListener('input', calculateEvaluationScore);
    });

    // Run initial calculation on page load
    calculateEvaluationScore();
});

