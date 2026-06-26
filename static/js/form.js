// Fetch countries and populate the country select box dynamically
document.addEventListener('DOMContentLoaded', async function() {
    const countrySelect = document.getElementById('country');
    const programSelect = document.getElementById('program');

    try {
        const countriesResponse = await fetch('/api/countries');
        const countries = await countriesResponse.json();

        countries.forEach(country => {
            const option = document.createElement('option');
            option.value = country;
            option.textContent = country;
            countrySelect.appendChild(option);
        });
    } catch (error) {
        console.error('Error fetching countries:', error);
    }

    try {
        const programsResponse = await fetch('/api/programs');
        const programs = await programsResponse.json();

        programs.forEach(program => {
            const option = document.createElement('option');
            option.value = program;
            option.textContent = program;
            programSelect.appendChild(option);
        });
    } catch (error) {
        console.error('Error fetching programs:', error);
    }
});
