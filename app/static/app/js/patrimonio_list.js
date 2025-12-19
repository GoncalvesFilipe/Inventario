// ==========================================================
// Controle de fechamento automático do modal de patrimônio
// após atualização da tabela via HTMX
// ==========================================================
document.body.addEventListener("htmx:afterSwap", event => {

  // --------------------------------------------------
  // Ignora swaps que disparam o evento de upload
  // (fluxo tratado separadamente em htmx_events.js)
  // --------------------------------------------------
  const triggerHeader = event.detail.xhr?.getResponseHeader("HX-Trigger");
  if (triggerHeader && triggerHeader.includes("planilhaAtualizada")) {
    return;
  }

  // --------------------------------------------------
  // Fecha o modal apenas quando a tabela for atualizada
  // --------------------------------------------------
  const tabela = document.getElementById("tabela-patrimonios");
  if (tabela && tabela.contains(event.target)) {

    const modalEl = document.getElementById("modalPatrimonio");
    const modalInstance = bootstrap.Modal.getInstance(modalEl);

    if (modalInstance) {
      modalInstance.hide();
    }
  }
});

// ==========================================================
// Limpa o conteúdo do modal ao ser fechado
// ==========================================================
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
