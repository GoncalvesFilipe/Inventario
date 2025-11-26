// FECHAR MODAL QUANDO O SALVAMENTO FOR BEM-SUCEDIDO (HTMX)
document.body.addEventListener("patrimonio-atualizado", function () {
    const modalEl = document.getElementById("modalPatrimonio");

    if (modalEl) {
        const modal = bootstrap.Modal.getInstance(modalEl);
        if (modal) {
            modal.hide();
        }
    }
});

// LIMPAR CONTEÚDO DO FORMULÁRIO QUANDO O MODAL FECHA
document.addEventListener("hidden.bs.modal", function (event) {
    if (event.target.id === "modalPatrimonio") {
        const body = document.getElementById("modal-patrimonio-body");
        if (body) {
            body.innerHTML = "";
        }
    }
});


// LOG OPCIONAL QUANDO A TABELA É ATUALIZADA
document.body.addEventListener("htmx:afterSwap", function (evt) {
    if (evt.detail.target.id === "tabela-patrimonios") {
        console.log("Tabela de patrimônios atualizada.");
    }
});


// ADICIONAR CSRF AUTOMATICAMENTE EM TODAS AS REQUISIÇÕES HTMX
document.body.addEventListener("htmx:configRequest", function (event) {
    document.body.addEventListener("htmx:configRequest", function (event) {
    event.detail.headers["X-CSRFToken"] = window.CSRF_TOKEN;
});

});
