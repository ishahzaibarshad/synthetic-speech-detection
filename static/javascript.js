// In script.js
document.addEventListener('DOMContentLoaded', () => {
    const uploadForm = document.getElementById('uploadForm');
    const loaderOverlay = document.getElementById('loader-overlay');
    const audioInput = document.getElementById('audioInput');
    const fileNameDisplay = document.getElementById('fileName');
    const responseMessage = document.getElementById('responseMessage');

    // Double-check elements exist
    if (!uploadForm || !loaderOverlay || !audioInput || !fileNameDisplay || !responseMessage) {
        console.error("One or more essential elements are missing!");
        return; // Stop script execution if elements aren't found
    }

    // Ensure loader is hidden on initial load (redundant if CSS is correct, but safe)
    loaderOverlay.style.display = 'none';

    // --- File Name Display Logic ---
    audioInput.addEventListener('change', function() {
        if (this.files && this.files.length > 0) {
            fileNameDisplay.textContent = this.files[0].name;
        } else {
            fileNameDisplay.textContent = 'No file chosen';
        }
    });

    // --- Loader Logic on Form Submit ---
    uploadForm.addEventListener('submit', function(event) {
        // Basic check: Ensure a file is selected
        if (audioInput.files.length === 0) {
             alert("Please select an audio file first.");
             event.preventDefault(); // Stop the form from submitting
             return; // Exit the function
        }

        // --- Show the loader ---
        loaderOverlay.style.display = 'flex'; // This makes the overlay visible

        // --- IMPORTANT ---
        // If your form submission causes a full page reload (standard form behavior),
        // the loader will only show briefly until the next page loads.
        // If you are handling the submission with JavaScript (AJAX/Fetch) to avoid a page reload,
        // you MUST hide the loader again when your operation is complete.
        // The example below includes a setTimeout to simulate this.

        // --- Example AJAX Handling (uncomment/adapt if needed) ---
        /*
        event.preventDefault(); // Prevent default page reload for AJAX

        // Simulate network request
        setTimeout(() => {
            // --- Hide the loader after task completion ---
            loaderOverlay.style.display = 'none';

            // Update response message (example)
            const isSynthetic = Math.random() > 0.5;
            if (isSynthetic) {
                responseMessage.textContent = 'Result: Synthetic Speech Detected';
                responseMessage.className = 'response-output error';
            } else {
                responseMessage.textContent = 'Result: Real Speech Detected';
                responseMessage.className = 'response-output success';
            }

        }, 3000); // Simulate a 3-second delay
        */
    });
});