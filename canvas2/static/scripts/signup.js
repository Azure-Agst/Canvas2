// Global element variables
const errorBox = document.querySelector('.error-box');
const flashedMessages = [...document.querySelectorAll('.flashed-message')];
const roleSelect = document.getElementById('role-select');
const teacherNotice = document.querySelector('.teacher-notice');
const submitButton = document.querySelector('button');
const password = document.getElementById('password');
const passwordConfirm = document.getElementById('password-confirm');
const form = document.getElementById('signup-form');
const errorMessage = document.querySelector('.error-message');

// Shows the message flash box when there are flashed messages
if (flashedMessages.length > 0) {
  errorBox.toggleAttribute('hidden');
}

// Shows a notice when the teacher account is selected
roleSelect.addEventListener('change', (e) => {
  if (e.target.options.selectedIndex === 2) {
    teacherNotice.removeAttribute('hidden');
  } else {
    teacherNotice.setAttribute('hidden', '');
  }
});

// Checks passwords for sameness before form submission
submitButton.addEventListener('click', (e) => {
  e.preventDefault();
  isValid = form.checkValidity();
  form.reportValidity();

  if (isValid) {
    if (password.value && password.value === passwordConfirm.value) {
      form.submit();
    } else {
      password.style.cssText = 'border: 1px solid rgb(255, 0, 0, .5)';
      passwordConfirm.style.cssText = 'border: 1px solid rgb(255, 0, 0, .5)';
      errorMessage.textContent = 'Passwords are not the same';

      if (errorBox.hasAttribute('hidden')) {
        // Shows the error box
        errorBox.toggleAttribute('hidden');
      } else {
        // Clears any flashed messages so only the password error message shows
        for (let flashedMessage of flashedMessages) {
          flashedMessage.textContent = '';
        }
      }

      if (errorMessage.hasAttribute('hidden')) {
        // Shows the password error message inside of the error box
        errorMessage.toggleAttribute('hidden');
      }
    }
  }
});
