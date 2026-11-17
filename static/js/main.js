/**
 * AI-Powered Interview Experience and Preparation Portal
 * Frontend JavaScript Controller
 */

document.addEventListener('DOMContentLoaded', function () {
  // 1. Setup CSRF Token for Fetch API
  const csrfTokenMeta = document.querySelector('meta[name="csrf-token"]');
  const csrfToken = csrfTokenMeta ? csrfTokenMeta.getAttribute('content') : '';

  // 2. Auto-dismiss alerts after 5 seconds
  setTimeout(function () {
    const alerts = document.querySelectorAll('.alert-dismissible');
    alerts.forEach(function (alert) {
      const bsAlert = bootstrap.Alert.getOrCreateInstance(alert);
      if (bsAlert) bsAlert.close();
    });
  }, 5000);

  // 3. Mobile Sidebar Toggle
  const sidebarToggleBtn = document.getElementById('sidebarToggleBtn');
  const portalSidebar = document.querySelector('.portal-sidebar');
  if (sidebarToggleBtn && portalSidebar) {
    sidebarToggleBtn.addEventListener('click', function () {
      portalSidebar.classList.toggle('show');
    });
  }

  // 4. Bookmark / Save Question Toggle Handler
  document.querySelectorAll('.btn-bookmark-question').forEach(function (btn) {
    btn.addEventListener('click', function (e) {
      e.preventDefault();
      const questionId = this.dataset.questionId;
      const isSaved = this.dataset.saved === 'true';
      const endpoint = isSaved ? '/question-generator/unsave' : '/question-generator/save';

      const formData = new FormData();
      formData.append('question_id', questionId);

      fetch(endpoint, {
        method: 'POST',
        headers: {
          'X-CSRFToken': csrfToken
        },
        body: formData
      })
      .then(res => res.json())
      .then(data => {
        if (data.status === 'success') {
          if (isSaved) {
            this.dataset.saved = 'false';
            this.innerHTML = '<i class="bi bi-bookmark"></i> Save';
            this.classList.remove('btn-warning');
            this.classList.add('btn-outline-secondary');
          } else {
            this.dataset.saved = 'true';
            this.innerHTML = '<i class="bi bi-bookmark-fill"></i> Saved';
            this.classList.remove('btn-outline-secondary');
            this.classList.add('btn-warning');
          }
        } else {
          alert(data.message || 'Operation failed');
        }
      })
      .catch(err => {
        console.error('Bookmark error:', err);
      });
    });
  });

  // 5. Mock Interview Answer Submission via AJAX
  const mockAnswerForm = document.getElementById('mockAnswerForm');
  if (mockAnswerForm) {
    mockAnswerForm.addEventListener('submit', function (e) {
      e.preventDefault();
      const submitBtn = document.getElementById('submitAnswerBtn');
      const spinner = document.getElementById('aiEvalSpinner');
      const evalContainer = document.getElementById('evalContainer');
      const answerInput = document.getElementById('user_answer');

      if (!answerInput.value.trim()) {
        alert('Please type your answer before submitting.');
        return;
      }

      // Show loading indicator
      submitBtn.disabled = true;
      if (spinner) spinner.classList.remove('d-none');

      const formData = new FormData(mockAnswerForm);

      fetch(mockAnswerForm.action, {
        method: 'POST',
        headers: {
          'X-CSRFToken': csrfToken
        },
        body: formData
      })
      .then(res => res.json())
      .then(data => {
        if (spinner) spinner.classList.add('d-none');
        if (data.status === 'success') {
          const ev = data.evaluation;
          // Populate feedback modal/container
          document.getElementById('scoreOverall').textContent = ev.overall_score + '%';
          document.getElementById('scoreRelevance').textContent = ev.relevance_score + '%';
          document.getElementById('scoreCorrectness').textContent = ev.correctness_score + '%';
          document.getElementById('scoreCompleteness').textContent = ev.completeness_score + '%';
          document.getElementById('scoreClarity').textContent = ev.clarity_score + '%';
          document.getElementById('evalFeedback').textContent = ev.feedback;
          document.getElementById('evalStrengths').textContent = ev.strengths;
          document.getElementById('evalWeaknesses').textContent = ev.weaknesses;
          document.getElementById('evalSuggested').textContent = ev.suggested_answer;

          // Show evaluation view
          mockAnswerForm.classList.add('d-none');
          evalContainer.classList.remove('d-none');
          window.scrollTo({ top: evalContainer.offsetTop - 80, behavior: 'smooth' });

          const nextBtn = document.getElementById('nextQuestionBtn');
          if (data.is_last) {
            nextBtn.textContent = 'View Final Comprehensive Report';
            nextBtn.classList.remove('btn-primary');
            nextBtn.classList.add('btn-success');
            nextBtn.href = mockAnswerForm.dataset.finalizeUrl;
          } else {
            nextBtn.textContent = 'Proceed to Next Question';
            nextBtn.href = window.location.href; // refresh for next index
          }
        } else {
          alert('Evaluation error: ' + (data.error || 'Server error'));
          submitBtn.disabled = false;
        }
      })
      .catch(err => {
        console.error('Submission error:', err);
        if (spinner) spinner.classList.add('d-none');
        submitBtn.disabled = false;
        alert('Network error while evaluating answer. Please try again.');
      });
    });
  }
});
