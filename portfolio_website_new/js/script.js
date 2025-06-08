// Set dynamic year in footer
window.addEventListener('DOMContentLoaded', function() {
  var yearSpan = document.getElementById('currentYear');
  if (yearSpan) {
    yearSpan.textContent = new Date().getFullYear();
  }
});

// (Optional) Add reveal-on-scroll animation for sections
// You can expand this for more interactivity if desired.
