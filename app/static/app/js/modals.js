document.addEventListener("htmx:afterSwap", (event) => {
    // Verifica se a partial carregada contém o modal
    const modalEl = document.getElementById("modalInventario");
    if (modalEl) {
        bootstrap.Modal.getOrCreateInstance(modalEl).show();
    }
});
