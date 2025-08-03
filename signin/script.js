const signinBtn = document.getElementById('signinBtn');
const signupBtn = document.getElementById('signupBtn');
const container = document.getElementById('container');

signinBtn.addEventListener('click', function () {
  container.classList.remove('right-panel-active');
});

signupBtn.addEventListener('click', function () {
  container.classList.add('right-panel-active');
});

function validatePassword() {
  var password = document.getElementById("password").value;
  var message = document.getElementById("message");

  // Define password criteria
  var minLength = 8;
  var maxLength = 16;
  var hasUpperCase = /[A-Z]/.test(password);
  var hasLowerCase = /[a-z]/.test(password);
  var hasNumber = /\d/.test(password);
  var hasSpecialChar = /[!@#$%^&*()_+\-=\[\]{};':"\\|,.<>\/?]+/.test(password);

  // Check if password meets criteria
  if (password.length < minLength || password.length > maxLength) {
    message.textContent = "Password must be between " + minLength + " and " + maxLength + " characters long";
  } else if (!hasUpperCase || !hasLowerCase || !hasNumber || !hasSpecialChar) {
    message.textContent = "Password must contain at least one uppercase letter, one lowercase letter, one number, and one special character";
  } else {
    message.textContent = "Password is valid";
  }
}
