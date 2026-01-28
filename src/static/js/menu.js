// Espera o HTML carregar inteiro
document.addEventListener("DOMContentLoaded", function () {

    // Seleciona todos os botões de dropdown
    const buttons = document.querySelectorAll(".dropdown-btn");

    buttons.forEach(btn => {
        btn.addEventListener("click", function (event) {
            event.stopPropagation(); // impede fechar ao clicar no botão

            // Dropdown ligado ao botão clicado
            const dropdown = this.nextElementSibling;

            // Fecha os outros dropdowns
            document.querySelectorAll(".dropdown-content").forEach(dc => {
                if (dc !== dropdown) {
                    dc.classList.remove("show");
                }
            });

            // Alterna o dropdown atual
            dropdown.classList.toggle("show");
        });
    });

    // Fecha tudo ao clicar fora
    document.addEventListener("click", function () {
        document.querySelectorAll(".dropdown-content").forEach(dc => {
            dc.classList.remove("show");
        });
    });

});
