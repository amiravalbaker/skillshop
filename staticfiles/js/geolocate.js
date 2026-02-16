(function () {
  const btn = document.getElementById("use-location-btn");
  const latEl = document.getElementById("lat");
  const lonEl = document.getElementById("lon");
  const locationInput = document.getElementById("location-input");

  if (!btn) return;

  btn.addEventListener("click", function () {
    if (!navigator.geolocation) {
      alert("Geolocation is not supported by your browser.");
      return;
    }

    navigator.geolocation.getCurrentPosition(
      function (pos) {
        latEl.value = pos.coords.latitude;
        lonEl.value = pos.coords.longitude;
        locationInput.value = "Current location";
      },
      function () {
        alert("Unable to retrieve your location (permission denied?).");
      }
    );
  });
})();
