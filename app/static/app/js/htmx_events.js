// ==========================================================
// HTMX Events
// Este arquivo centraliza o tratamento de eventos disparados
// pelo HTMX durante requisições assíncronas.
// ==========================================================

document.body.addEventListener('htmx:afterRequest', function(event) {
  if (event.detail.xhr.status === 403) {
    // Limpa o modal atual
    const target = document.querySelector(event.detail.target);
    if (target) target.innerHTML = '';
    
    // Mostra modal de acesso negado
    const modalAcessoNegado = new bootstrap.Modal(
      document.getElementById('modalAcessoNegado')
    );
    modalAcessoNegado.show();
  }
});

// ==========================================================
// Evento customizado: reloadPage
// Disparado pelo backend via HX-Trigger para recarregar
// toda a página após operações bem-sucedidas.
// ==========================================================
document.body.addEventListener('reloadPage', function () {
  window.location.reload();
});

// ==========================================================
// Evento customizado: closeModal
// Disparado pelo backend via HX-Trigger para fechar
// o modal de inventariante após operações bem-sucedidas.
// ==========================================================
document.body.addEventListener('closeModal', function () {
  const modalInventariante = bootstrap.Modal.getInstance(
    document.getElementById('modalInventariante')
  );
  if (modalInventariante) {
    modalInventariante.hide();
  }
});
