// Handle async status update form submission
document.addEventListener('DOMContentLoaded', function() {
    const statusForm = document.getElementById('statusForm');
    const statusSelect = document.getElementById('statusSelect');

    if (statusForm) {
        statusForm.addEventListener('submit', async function(e) {
            e.preventDefault();

            const formData = new FormData(statusForm);

            try {
                const response = await fetch(statusForm.action, {
                    method: 'POST',
                    body: formData
                });

                const result = await response.json();

                if (result.success) {
                    const statusElement = document.querySelector('.student-info .status-' + result.status.toLowerCase());
                    if (statusElement) {
                        statusElement.textContent = result.status;
                    } else {
                        location.reload();
                    }
                    alert('Status updated successfully!');
                } else {
                    alert('Error updating status: ' + result.error);
                }
            } catch (error) {
                alert('Error updating status: ' + error.message);
            }
        });
    }
});
