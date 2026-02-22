console.log("Search page JS loaded");

document.addEventListener("DOMContentLoaded", function () {
    const locationInput = document.getElementById("location-input");
    const latField = document.getElementById("lat");
    const lonField = document.getElementById("lon");
    const geoStatus = document.getElementById("geo-status");
    const useLocationBtn = document.getElementById("use-location-btn");
    const clearBtn = document.getElementById("clear-location-btn");

    // --- Helper: Show failure message ---
    function showFallback() {
        locationInput.value = "Location not detected";
        latField.value = "";
        lonField.value = "";
        geoStatus.textContent = ""; // no visible status
    }

    // --- Helper: Fill visible box + hidden fields ---
    function setLocation(lat, lon) {
        latField.value = lat;
        lonField.value = lon;

        // Show lat/lon in the visible input
        locationInput.value = `${lat.toFixed(2)}, ${lon.toFixed(2)}`;

        geoStatus.textContent = ""; // no success message
    }

    // --- Geolocation function ---
    function detectLocation() {
        // ⭐ Show detecting message AFTER clearing any template value 
        locationInput.value = ""; 
        setTimeout(() => { 
            locationInput.value = "Detecting location…"; 
        }, 10);

        geoStatus.textContent = ""; // no "detecting" message

        if (!navigator.geolocation) {
            showFallback();
            return;
        }

        navigator.geolocation.getCurrentPosition(
            (pos) => {
                const lat = pos.coords.latitude;
                const lon = pos.coords.longitude;
                setLocation(lat, lon);
            },
            () => {
                showFallback();
            },
            { enableHighAccuracy: true, timeout: 8000 }
        );
    }


    // --- Manual "Use my location" button ---
    useLocationBtn.addEventListener("click", detectLocation);

    // --- Clear button ---
    if (clearBtn) {
        clearBtn.addEventListener("click", function () {
            locationInput.value = "";
            latField.value = "";
            lonField.value = "";
            geoStatus.textContent = "";
            const skillInput = document.querySelector("input[name='skill']");
            if (skillInput) skillInput.value = "";
        });
    }
});
