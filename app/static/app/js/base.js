/* ============================================================
   CSRF PARA TODAS AS REQUISIÇÕES HTMX
============================================================ */
document.body.addEventListener("htmx:configRequest", function (event) {
    event.detail.headers["X-CSRFToken"] = window.CSRF_TOKEN;
});


/* ============================================================
   FECHAR MODAIS VIA "HX-Trigger: closeModal"
============================================================ */
document.body.addEventListener("closeModal", function () {

    const modais = [
        "modalInventariante",
        "modalPatrimonio",
        "modalRegistro"
    ];

    modais.forEach(id => {
        const el = document.getElementById(id);
        if (!el) return;

        let modal = bootstrap.Modal.getInstance(el);
        if (!modal) modal = new bootstrap.Modal(el);

        modal.hide();
    });
});


/* ============================================================
   ABRIR MODAL AUTOMATICAMENTE APÓS HTMX SWAP
============================================================ */
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
});


/* ============================================================
   LIMPAR OS MODAIS AO FECHAR
============================================================ */
document.addEventListener("hidden.bs.modal", function (event) {

    const id = event.target.id;

    const map = {
        modalInventariante: "modal-inventariante-body",
        modalPatrimonio: "modal-patrimonio-body",
        modalRegistro: "modal-registro-body"
    };

    if (map[id]) {
        const body = document.getElementById(map[id]);
        if (body) body.innerHTML = "";
    }
});

/* ============================================================
   CORREÇÃO GLOBAL – REMOVER BACKDROP PRESO E DESCONGELAR TELA
============================================================ */
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
