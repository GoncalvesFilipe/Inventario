/* CSRF PARA TODAS AS REQUISIÇÕES HTMX */
document.body.addEventListener("htmx:configRequest", function (event) {
    event.detail.headers["X-CSRFToken"] = window.CSRF_TOKEN;
});


/* FECHAR MODAIS VIA "HX-Trigger: closeModal"
   - A view inventariante_add (e outras) podem retornar HX-Trigger: closeModal
   - Esse listener fecha automaticamente qualquer modal listado em 'modais'
   - Garante que o modal não permaneça aberto após operações bem-sucedidas
*/
document.body.addEventListener("closeModal", function () {
    const modais = [
        "modalInventariante",
        "modalPatrimonio",
        "modalRegistro",
        "modalErro",
        "modalConfirm"
    ];

    modais.forEach(id => {
        const el = document.getElementById(id);
        if (!el) return;

        let modal = bootstrap.Modal.getInstance(el);
        if (!modal) modal = new bootstrap.Modal(el);

        modal.hide();
    });
});


/* ABRIR MODAL AUTOMATICAMENTE APÓS HTMX SWAP
   - Quando o HTMX injeta conteúdo em um body de modal,
     este listener abre o modal correspondente automaticamente.
   - Evita que o usuário precise clicar manualmente para abrir.
*/
document.body.addEventListener("htmx:afterSwap", function (event) {
    const target = event.detail.target;

    if (target.id === "modal-inventariante-body") {
        new bootstrap.Modal(document.getElementById("modalInventariante")).show();
    }

    if (target.id === "modal-patrimonio-body") {
        new bootstrap.Modal(document.getElementById("modalPatrimonio")).show();
    }

    if (target.id === "modal-registro-body") {
        new bootstrap.Modal(document.getElementById("modalRegistro")).show();
    }

    // Abre o modal de exclusão
    if (target.id === "modal-confirm-body") {
        new bootstrap.Modal(document.getElementById("modalConfirm")).show();
    }
});


/* LIMPAR OS MODAIS AO FECHAR
   - Após o fechamento de um modal, limpa o conteúdo do body correspondente.
   - Evita que dados antigos fiquem visíveis quando o modal for reaberto.
*/
document.addEventListener("hidden.bs.modal", function (event) {
    const id = event.target.id;

    const map = {
        modalInventariante: "modal-inventariante-body",
        modalPatrimonio: "modal-patrimonio-body",
        modalRegistro: "modal-registro-body",
        modalErro: "modal-erro-body",
        modalConfirm: "modal-confirm-body"  
    };

    if (map[id]) {
        const body = document.getElementById(map[id]);
        if (body) body.innerHTML = "";
    }
});


/* CORREÇÃO GLOBAL – REMOVER BACKDROP PRESO E DESCONGELAR TELA
   - Corrige problemas ocasionais em que o backdrop do Bootstrap
     permanece preso ou o scroll da página fica bloqueado.
   - Remove manualmente o backdrop e garante que o body volte ao normal.
*/
document.addEventListener("hidden.bs.modal", function () {
    // Remover qualquer backdrop fantasma
    document.querySelectorAll('.modal-backdrop').forEach(backdrop => {
        backdrop.remove();
    });

    // Garantir que o body volte ao normal
    document.body.classList.remove('modal-open');
    document.body.style.removeProperty('overflow');
    document.body.style.removeProperty('padding-right');

    // Garantir que o scroll não fique travado
    setTimeout(() => {
        document.body.classList.remove('modal-open');
    }, 10);
});

function fecharModalInventariante() {
  const modalEl = document.getElementById('modalInventariante');
  if (modalEl) {
    const modal = bootstrap.Modal.getInstance(modalEl) 
               || bootstrap.Modal.getOrCreateInstance(modalEl);
    modal.hide();
  }
}
