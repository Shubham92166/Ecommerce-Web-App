// Get the modal
var modal = document.getElementById("session-timeout-modal");

// Get the close button
var close = document.getElementsByClassName("close")[0];

// Get the extend button
var extend = document.getElementById("extend-session");

// Get the logout button
var logout = document.getElementById("logout");

// Show the modal before the session expires
setTimeout(function() {
  modal.style.display = "block";
}, 600);

// Close the modal when the user clicks the close button
close.onclick = function() {
  modal.style.display = "none";
}

// Extend the session when the user clicks the extend button
extend.onclick = function() {
  // Code to extend the session goes here
  modal.style.display = "none";
}

// Logout the user when the user clicks the logout button
logout.onclick = function() {
  // Code to logout the user goes here
  modal.style.display = "none";
}
