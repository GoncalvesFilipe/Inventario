document.body.addEventListener("htmx:configRequest", function (event) {
    let token = document.querySelector("#csrf-token-global")?.value;

    if (!token) {
        const input = document.querySelector("[name=csrfmiddlewaretoken]");
        token = input ? input.value : null;
    }

    if (token) {
        event.detail.headers["X-CSRFToken"] = token;
    }
});
