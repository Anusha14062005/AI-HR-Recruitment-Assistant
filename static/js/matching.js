/**
 * Candidate Matching Interactive Controller
 */

document.addEventListener('DOMContentLoaded', () => {
    const jobSelect = document.getElementById('matchJobSelect');
    const candSelect = document.getElementById('matchCandidateSelect');

    function updateMatchQuery() {
        if (jobSelect && candSelect) {
            const jobId = jobSelect.value;
            const candId = candSelect.value;
            if (jobId && candId) {
                window.location.href = `/matching?job_id=${jobId}&candidate_id=${candId}`;
            }
        }
    }

    if (jobSelect) jobSelect.addEventListener('change', updateMatchQuery);
    if (candSelect) candSelect.addEventListener('change', updateMatchQuery);
});

