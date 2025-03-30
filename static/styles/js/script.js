window.addEventListener("DOMContentLoaded", () => {
    // Check if the audio element exists or create it dynamically
    let bgMusic = document.getElementById("bgMusic");

    if (!bgMusic) {
        // Create the audio element if it doesn't exist in HTML
        bgMusic = document.createElement("audio");
        bgMusic.id = "bgMusic"; // Give it an ID to reference it later
        bgMusic.src = "/static/audio/bgmusic.mp3"; // Corrected path to your audio file
        bgMusic.loop = true; // Set it to loop if desired
        document.body.appendChild(bgMusic); // Add the audio element to the DOM
    }

    // Set volume and other properties
    bgMusic.volume = 0.5;

    // Retrieve the saved time from sessionStorage if available
    const savedTime = sessionStorage.getItem("bgMusicTime");

    if (savedTime && !isNaN(savedTime)) {
        // If saved time exists, continue from there
        bgMusic.currentTime = parseFloat(savedTime);
    } else {
        // Otherwise, start from the beginning
        bgMusic.currentTime = 0;
    }

    // Start the music if not already playing
    bgMusic.play().catch(() => {
        console.log("Autoplay blocked, user interaction required.");
    });

    // Update sessionStorage on beforeunload to save current playback position
    window.addEventListener("beforeunload", () => {
        sessionStorage.setItem("bgMusicTime", bgMusic.currentTime); // Save current time before page unload
    });

    // Add animations to title elements after a short delay
    setTimeout(() => {
        document.querySelector(".title h1")?.classList.add("slide-text");
        document.querySelector(".title img")?.classList.add("slide-image");
    }, 1000);
});
