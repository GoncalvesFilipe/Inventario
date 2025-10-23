// admin_dashboard.js
document.addEventListener("DOMContentLoaded", function () {
  const menuButtons = document.querySelectorAll("#menu-admin button");

  menuButtons.forEach(button => {
    button.addEventListener("click", function () {
      // Remove a classe 'active' de todos
      menuButtons.forEach(btn => btn.classList.remove("active"));
      // Adiciona 'active' apenas ao botão clicado
      this.classList.add("active");
    });
  });
});
