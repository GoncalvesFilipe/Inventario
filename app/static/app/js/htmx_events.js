// ==========================================================
// HTMX + BOOTSTRAP MODAL EVENTS
// Centraliza o tratamento de eventos assíncronos,
// garantindo integridade visual e funcional da interface.
// ==========================================================


/**
 * ==========================================================
 * EVENTO: htmx:afterRequest
 * ==========================================================
 *
 * Disparado após qualquer requisição HTMX.
 * Utilizado aqui para tratar respostas HTTP 403
 * (acesso negado) de forma centralizada.
 */
document.body.addEventListener('htmx:afterRequest', function (event) {

  if (event.detail.xhr && event.detail.xhr.status === 403) {

    // --------------------------------------------------
    // Limpeza segura do conteúdo de destino do HTMX
    // --------------------------------------------------
    const targetElement = event.detail.target instanceof HTMLElement
      ? event.detail.target
      : null;

    if (targetElement) {
      targetElement.innerHTML = '';
    }

    // --------------------------------------------------
    // Exibição do modal de acesso negado
    // --------------------------------------------------
    const modalEl = document.getElementById('modalAcessoNegado');
    if (modalEl) {
      const modalAcessoNegado = new bootstrap.Modal(modalEl);
      modalAcessoNegado.show();
    }
  }
});


/**
 * ==========================================================
 * EVENTO CUSTOMIZADO: reloadPage
 * ==========================================================
 *
 * Disparado via HX-Trigger pelo backend
 * para forçar recarregamento completo da página.
 */
document.body.addEventListener('reloadPage', function () {
  window.location.reload();
});


/**
 * ==========================================================
 * EVENTO CUSTOMIZADO: closeModal
 * ==========================================================
 *
 * Fecha qualquer modal atualmente aberto na interface.
 * Compatível com múltiplos fluxos (inventariante, patrimônio, etc).
 */
document.body.addEventListener('closeModal', function () {
  const modalAberto = document.querySelector('.modal.show');
  if (!modalAberto) return;

  const modalInstance = bootstrap.Modal.getInstance(modalAberto);
  if (modalInstance) {
    modalInstance.hide();
  }
});


/**
 * ==========================================================
 * EVENTO CUSTOMIZADO: planilhaAtualizada
 * ==========================================================
 *
 * Fluxo:
 * 1) Exibe mensagem de sucesso no modal aberto
 * 2) Aguarda 3 segundos
 * 3) Fecha o modal corretamente
 * 4) Recarrega a página
 */
document.body.addEventListener('planilhaAtualizada', function () {

  const modalAberto = document.querySelector('.modal.show');
  if (!modalAberto) return;

  // --------------------------------------------------
  // Injeção de feedback visual ao usuário
  // --------------------------------------------------
  const modalBody = modalAberto.querySelector('.modal-body');
  if (modalBody) {
    modalBody.innerHTML = `
      <div class="alert alert-success text-center fw-bold">
        Planilha enviada com sucesso!
      </div>
    `;
  }

  // --------------------------------------------------
  // Encerramento controlado do fluxo
  // --------------------------------------------------
  setTimeout(() => {

    const modalInstance = bootstrap.Modal.getInstance(modalAberto);
    if (modalInstance) {
      modalInstance.hide();
    }

    window.location.reload();

  }, 3000);
});


/**
 * ==========================================================
 * EVENTO GLOBAL: hidden.bs.modal
 * ==========================================================
 *
 * Garantia de limpeza total do estado visual
 * após o fechamento de QUALQUER modal.
 *
 * Essencial em aplicações que combinam
 * Bootstrap Modal + HTMX.
 */
document.body.addEventListener('hidden.bs.modal', function () {

  // Restaura o scroll da página
  document.body.classList.remove('modal-open');

  // Remove qualquer backdrop residual
  document.querySelectorAll('.modal-backdrop').forEach(function (backdrop) {
    backdrop.remove();
  });

});

/* ==========================================================
   EVENTO CUSTOMIZADO – patrimonioExcluido
   ----------------------------------------------------------
   Fluxo após exclusão de patrimônio:
   1) Exibe mensagem temporária de sucesso (toast)
   2) Fecha automaticamente o modal de confirmação
   3) Recarrega a página após 3 segundos
   ========================================================== */
document.body.addEventListener("patrimonioExcluido", function () {

    // ---------------------------------------------
    // Exibe toast de confirmação
    // ---------------------------------------------
    const toastEl = document.createElement("div");
    toastEl.className = "toast align-items-center text-bg-success border-0 show";
    toastEl.style = "position: fixed; top: 1rem; right: 1rem; z-index: 2000;";
    toastEl.innerHTML = `
      <div class="d-flex">
        <div class="toast-body fw-bold">
          Patrimônio excluído com sucesso!
        </div>
        <button type="button" class="btn-close btn-close-white me-2 m-auto" 
                data-bs-dismiss="toast" aria-label="Fechar"></button>
      </div>
    `;
    document.body.appendChild(toastEl);

    // ---------------------------------------------
    // Fecha o modal de confirmação
    // ---------------------------------------------
    const modalEl = document.getElementById("modalConfirm");
    if (modalEl) {
        const modal = bootstrap.Modal.getInstance(modalEl) 
                   || bootstrap.Modal.getOrCreateInstance(modalEl);
        modal.hide();
    }

    // ---------------------------------------------
    // Recarrega a página após feedback visual
    // ---------------------------------------------
    setTimeout(() => {
        window.location.reload();
    }, 3000);
});

/* ==========================================================
   EVENTO CUSTOMIZADO – planilhaExcluida
   ----------------------------------------------------------
   Fluxo após exclusão de planilha:
   1) Exibe mensagem de sucesso dentro do modal de confirmação
   2) Aguarda 3 segundos
   3) Fecha o modal corretamente
   4) Recarrega a página inteira
   ========================================================== */
document.body.addEventListener("planilhaExcluida", function () {

    const modalAberto = document.querySelector(".modal.show");
    if (!modalAberto) return;

    // --------------------------------------------------
    // Injeção de feedback visual dentro do modal
    // --------------------------------------------------
    const modalBody = modalAberto.querySelector(".modal-body");
    if (modalBody) {
        modalBody.innerHTML = `
          <div class="alert alert-success text-center fw-bold">
            Planilha excluída com sucesso!
          </div>
        `;
    }

    // --------------------------------------------------
    // Encerramento controlado do fluxo
    // --------------------------------------------------
    setTimeout(() => {
        const modalInstance = bootstrap.Modal.getInstance(modalAberto);
        if (modalInstance) {
            modalInstance.hide();
        }
        window.location.reload();
    }, 3000);
});
