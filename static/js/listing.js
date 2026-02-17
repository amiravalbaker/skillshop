(function() {
  const NEW_VALUE = "__new__";
  const selectEl = document.getElementById("id_skill_choice");
  const box = document.getElementById("new-skill-box");

  function toggle() {
    if (!selectEl || !box) return;

    if (selectEl.value === NEW_VALUE) {
      box.style.display = "block";
    } else {
      box.style.display = "none";
      const input = document.getElementById("id_new_skill");
      if (input) input.value = "";
    }
  }

  if (selectEl) {
    selectEl.addEventListener("change", toggle);
    toggle();
  }
})();
