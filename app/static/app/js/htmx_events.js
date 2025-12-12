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
