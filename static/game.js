console.log("✅ game.js file loaded successfully");

// Preload sounds safely
let successSound, failSound;

function loadSounds() {
    console.log("🎵 Attempting to load sounds...");
    successSound = new Audio("/static/sounds/success.mp3");
    failSound = new Audio("/static/sounds/fail.mp3");

    // Don't autoplay yet (Safari will block)
    successSound.load();
    failSound.load();

    // Try to unlock on first click or touch
    const unlock = () => {
        console.log("🟢 Trying to unlock audio...");
        try {
            successSound.play().then(() => {
                successSound.pause();
                successSound.currentTime = 0;
                console.log("✅ Success sound unlocked!");
            }).catch(() => {});
            failSound.play().then(() => {
                failSound.pause();
                failSound.currentTime = 0;
                console.log("✅ Fail sound unlocked!");
            }).catch(() => {});
        } catch (err) {
            console.warn("⚠️ Unlock failed:", err);
        }
        document.removeEventListener("click", unlock);
        document.removeEventListener("touchstart", unlock);
    };

    document.addEventListener("click", unlock);
    document.addEventListener("touchstart", unlock);
}

// Call this once when the page loads
loadSounds();

// ------------------ GAME LOGIC -------------------
document.addEventListener("DOMContentLoaded", () => {
    console.log("🎮 Game initialized");

    const form = document.getElementById("guess-form");
    const input = document.getElementById("guess-input");
    const message = document.getElementById("message");
    const playAgain = document.getElementById("play-again");

    form.addEventListener("submit", (e) => {
        e.preventDefault();
        const guess = parseInt(input.value);

        fetch("/check", {
            method: "POST",
            body: new URLSearchParams({ guess }),
            headers: { "Content-Type": "application/x-www-form-urlencoded" }
        })
            .then(res => res.json())
            .then(data => {
                message.textContent = data.message;
                message.className = data.status;

                if (data.status === "correct") {
                    successSound.currentTime = 0;
                    successSound.play();
                    playAgain.style.display = "block";
                } else {
                    failSound.currentTime = 0;
                    failSound.play();
                }
            })
            .catch(err => console.error("❌ Error:", err));
    });

    playAgain.addEventListener("click", () => {
        window.location.reload();
    });

    console.log("✨ Event listeners attached successfully");
});
