/*
  download.js
  Author:  Nathan Filipowitz
  Date:    2026-05-12
  Purpose: Sélection de fichiers et bulk download
*/

var bulkBtn = document.getElementById('bulk-btn');
var countEl = document.getElementById('bulk-count');

// Called on every checkbox change.
// Updates the counter and shows/hides the bulk button.
function onCheck() {
  var allCheckboxes = document.querySelectorAll('.cb');
  var count = 0;

  // Count checked boxes and highlight selected cards
  for (var i = 0; i < allCheckboxes.length; i++) {
    var checkbox = allCheckboxes[i];
    var card = checkbox.closest('.file-card');

    if (checkbox.checked) {
      count = count + 1;
      card.classList.add('selected');
    } else {
      card.classList.remove('selected');
    }
  }

  // Update counter in button label
  countEl.textContent = count;

  // Show or hide bulk button depending on selection
  if (count > 0) {
    bulkBtn.classList.add('visible');
  } else {
    bulkBtn.classList.remove('visible');
  }
}

// Attach onCheck to every checkbox
var allCheckboxes = document.querySelectorAll('.cb');
for (var i = 0; i < allCheckboxes.length; i++) {
  allCheckboxes[i].addEventListener('change', onCheck);
}

// Run once on page load to sync button state with checkbox state
// (handles browser restoring checked state after a refresh)
onCheck();

// Bulk download button click: trigger one download per checked file
// Downloads are spaced 400ms apart so the browser handles each one
bulkBtn.addEventListener('click', function() {
  var checkedBoxes = document.querySelectorAll('.cb:checked');
  var delay = 0;

  for (var i = 0; i < checkedBoxes.length; i++) {
    var filename = checkedBoxes[i].value;

    // Create an invisible link, click it, then remove it
    setTimeout(function(name) {
      var link = document.createElement('a');
      link.href = '/' + encodeURIComponent(name);
      link.download = name;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    }.bind(null, filename), delay);

    delay = delay + 400;
  }
});