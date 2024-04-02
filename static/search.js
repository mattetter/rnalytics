document.addEventListener('DOMContentLoaded', function() {

    const form = document.querySelector('#search-form');
  const statusMessage = document.querySelector('#status-message');
  
  form.addEventListener('submit', (event) => {
    event.preventDefault(); // prevent form from submitting normally
  
    const location = form.elements.location.value;
    const specialties = form.elements.specialties.value;
  
    if (!location && !specialties) {
      statusMessage.textContent = 'Please enter a location and specialties.';
      statusMessage.classList.remove('success-message');
      statusMessage.classList.add('error-message');
      return;
    }
  
    // Do something with the location and specialties values (e.g. fetch data from a database)
  
    statusMessage.textContent = 'This search form is not configured yet.';
    statusMessage.classList.remove('error-message');
    statusMessage.classList.add('success-message');
  });
  
  
  });
 
  