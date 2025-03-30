const grayscaleButton = document.getElementById('grayscaleToggle');
let grayscaleMode = localStorage.getItem('grayscale') === 'true';

// Function to apply or remove grayscale
function updateGrayscale() {
    if (grayscaleMode) {
        document.documentElement.classList.add('greyscale'); // Apply globally
        if (grayscaleButton) grayscaleButton.textContent = "Disable Grayscale Mode";
    } else {
        document.documentElement.classList.remove('greyscale');
        if (grayscaleButton) grayscaleButton.textContent = "Enable Grayscale Mode";
    }
}

// Run on page load
updateGrayscale();

// Only allow toggling on the /accessibility page
if (grayscaleButton) {
    grayscaleButton.addEventListener('click', () => {
        grayscaleMode = !grayscaleMode;
        localStorage.setItem('grayscale', grayscaleMode.toString());
        updateGrayscale();
    });
}
