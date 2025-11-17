// admin_dashboard.js
document.addEventListener("DOMContentLoaded", function () {
  const menuButtonsContainer = document.querySelector("#menu-admin");
  if (!menuButtonsContainer) return; // Evita erros se não existir

  const menuButtons = menuButtonsContainer.querySelectorAll("button");

  menuButtons.forEach(button => {
    button.addEventListener("click", function () {
      menuButtons.forEach(btn => btn.classList.remove("active"));
      this.classList.add("active");
    });
  });
});
