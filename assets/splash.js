document.addEventListener("DOMContentLoaded", function () {

    // How long the logo stays fully visible before fade begins
    const showDuration = 3500; // 3.5 seconds — increase as needed

    setTimeout(function () {
        const splash = document.getElementById("splash-screen");

        splash.classList.add("fade-out"); // triggers zoom-out effect
        splash.style.opacity = 0;         // starts fade-out

        // Remove element after fade completes
        setTimeout(function () {
            splash.style.display = "none";
        }, 2000); // must match CSS fade duration (2s)

    }, showDuration);
});
