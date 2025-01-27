const weekPicker = document.querySelector('.week-picker');
const monthPicker = document.querySelector('.month-picker');
const fallbackWeekPicker = document.querySelector('.fallback-week');
const fallbackYearPicker = document.querySelector('.fallback-year');
const fallbackMonthPicker = document.querySelector('.fallback-month');

const yearSelect = document.querySelector('#fallbackYear');
const weekSelect = document.querySelector('#fallbackWeek');
const monthSelect = document.querySelector('#fallbackMonth');

// Hide fallback initially
fallbackWeekPicker.style.display = 'none';
fallbackYearPicker.style.display = 'none';
fallbackMonthPicker.style.display = 'none';

// Test whether a new date input falls back to a text input or not
const test = document.createElement('input');

try {
    test.type = 'week';
} catch (e) {
    console.log(e.description);
}

// If it does, run the code inside the if () {} block
if ( test.type === 'text') {
// Hide the native picker and show the fallback
    weekPicker.style.display = 'none';
    monthPicker.style.display = 'none';
    fallbackWeekPicker.style.display = 'block';
    fallbackYearPicker.style.display = 'block';
    fallbackMonthPicker.style.display = 'block';
    // populate the weeks dynamically
    populateWeeks();
    populateMonths();
}

function populateWeeks() {
// Populate the week select with 52 weeks
    for (let i = 1; i <= 52; i++) {
        const option = document.createElement('option');
        option.textContent = (i < 10) ? `0${i}` : i;
        weekSelect.appendChild(option);
    }
}
function populateMonths() {
// Populate the week select with 12 months
    for (let i = 1; i <= 12; i++) {
        const option = document.createElement('option');
        option.textContent = (i < 10) ? `0${i}` : i;
        monthSelect.appendChild(option)
    }
}