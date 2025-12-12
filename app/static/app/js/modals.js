document.addEventListener("htmx:afterSwap", (event) => {
    if (event.detail.target.id === "modal-inventariante-body") {
        const modal = bootstrap.Modal.getOrCreateInstance(
            document.getElementById("modalInventariante")
        );
        modal.show();
    }
});
