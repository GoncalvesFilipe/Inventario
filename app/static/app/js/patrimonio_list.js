// Fecha o modal quando a tabela de patrimônios é atualizada
document.body.addEventListener("htmx:afterSwap", event => {
  const tabela = document.getElementById("tabela-patrimonios");

  // Se a tabela existe e foi afetada pelo swap
  if (tabela && tabela.contains(event.target)) {
    const modalEl = document.getElementById("modalPatrimonio");
    const modalInstance = bootstrap.Modal.getInstance(modalEl);

    if (modalInstance) {
      modalInstance.hide();
    }
  }
});

// Limpa o conteúdo do modal quando ele é fechado
document.addEventListener("DOMContentLoaded", () => {
  const modalEl = document.getElementById("modalPatrimonio");
  if (!modalEl) return;

  modalEl.addEventListener("hidden.bs.modal", () => {
    const body = document.getElementById("modal-patrimonio-body");
    if (body) {
      body.innerHTML = "";
    }
  });
});
