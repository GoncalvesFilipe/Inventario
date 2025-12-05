/* ============================================================
   CSRF PARA TODAS AS REQUISIÇÕES HTMX
============================================================ */
document.body.addEventListener("htmx:configRequest", function (event) {
    event.detail.headers["X-CSRFToken"] = window.CSRF_TOKEN;
});


/* ============================================================
   FECHAR MODAL DO INVENTÁRIO VIA "HX-Trigger: closeModal"
============================================================ */
document.body.addEventListener("closeModal", function () {
    const modalEl = document.getElementById("modalInventario");
    if (!modalEl) return;

    let modal = bootstrap.Modal.getInstance(modalEl);
    if (!modal) modal = new bootstrap.Modal(modalEl);
    modal.hide();
});


/* ============================================================
   FECHAR MODAL APÓS SWAP — APENAS PARA modalInventario
============================================================ */
document.body.addEventListener("htmx:afterSwap", function (event) {

    const target = event.detail.target;

    // Aceita apenas swaps dentro do modalInventario
    if (!["modal-content", "modal-inventario-body"].includes(target.id)) {
        return;  // impede fechar o modalRegistro
    }

    if (target.innerHTML.includes("close-modal")) {
        document.body.dispatchEvent(new Event("closeModal"));
    }
});


/* ============================================================
   LIMPAR modalInventario AO FECHAR
============================================================ */
document.addEventListener("hidden.bs.modal", function (event) {
    if (event.target.id === "modalInventario") {
        const body = document.getElementById("modal-inventario-body");
        if (body) body.innerHTML = "";
    }
});
