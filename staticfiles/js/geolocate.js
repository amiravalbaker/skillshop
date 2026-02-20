(function () {
  const useBtn = document.getElementById("use-location-btn");
  const clearBtn = document.getElementById("clear-location-btn");
  const latEl = document.getElementById("lat");
  const lonEl = document.getElementById("lon");
  const locationInput = document.getElementById("location-input");
  const statusEl = document.getElementById("geo-status");

  function setStatus(msg) {
    if (statusEl) statusEl.textContent = msg;
  }

  function clearLocationOnly() {
    if (latEl) latEl.value = "";
    if (lonEl) lonEl.value = "";
    if (locationInput) locationInput.value = "";
    setStatus("Location cleared. Type a postcode/town or click “Use my location” again.");
  }
  
  if (clearBtn) clearBtn.addEventListener("click", clearLocationOnly);

  if (!useBtn) return;

  useBtn.addEventListener("click", function () {
    if (!navigator.geolocation) {
      setStatus("Geolocation is not supported by your browser. Please type your postcode.");
      return;
    }

    setStatus("Detecting your location…");

    navigator.geolocation.getCurrentPosition(
      function (pos) {
        const lat = pos.coords.latitude;
        const lon = pos.coords.longitude;
        const acc = pos.coords.accuracy; // meters
        const miles = acc / 1609.34;

        if (latEl) latEl.value = lat;
        if (lonEl) lonEl.value = lon;

         // Label accuracy so users understand reliability
        const label =
          acc <= 200 ? "Precise" :
          acc <= 2000 ? "Approximate" :
          "Very approximate";

        // Show the user what’s being used for location and accuracy, so they understand the results and can choose to clear if it looks wrong
        if (locationInput) {
          locationInput.value = `Current location (${label}, ±${miles.toFixed(2)} miles)`;
        }

        if (acc <= 2000) {
          setStatus(`Location detected (${label}, ±${miles.toFixed(2)} miles). Click Search.`);
        } else {
          setStatus(`Location detected but may be inaccurate (${label}, ±${miles.toFixed(2)} miles). If results look wrong, type your postcode instead.`);
        }
      },
      function (err) {
        console.log(err);
        setStatus("Could not get your location. Allow location access or type your postcode.");
      },
      {enableHighAccuracy: true, timeout: 10000, maximumAge: 0 }
    );
  });
})();
