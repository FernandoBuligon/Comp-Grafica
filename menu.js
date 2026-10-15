// Os botões enviam ações ao Python; o estado confirmado controla o diálogo.
(() => {
    const cena = canvas.get_selected();
    const menu = document.getElementById("menu-parque");
    const abrir = document.getElementById("abrir-menu");
    const enviar = acao => cena.trigger("keydown", {
        key: `menu:${acao}`, which: 0, shift: false, ctrl: false, alt: false
    });
    abrir.addEventListener("click", () => enviar("alternar"));
    menu.querySelectorAll("[data-acao]").forEach(botao => {
        botao.addEventListener("click", () => enviar(botao.dataset.acao));
    });
    menu.addEventListener("cancel", evento => {
        evento.preventDefault();
        enviar("continuar");
    });
    window.addEventListener("keydown", evento => {
        if (menu.open && evento.key === "Tab") {
            const botoes = [...menu.querySelectorAll("button:not(:disabled)")];
            const atual = botoes.indexOf(document.activeElement);
            const proximo = (atual + (evento.shiftKey ? -1 : 1) + botoes.length) % botoes.length;
            evento.preventDefault();
            evento.stopImmediatePropagation();
            botoes[proximo].focus();
            return;
        }
        const tecla = evento.key.toLowerCase();
        const alternar = ["m", "escape"].includes(tecla);
        const secao = menu.open && ["1", "2", "3"].includes(tecla);
        const reiniciar = menu.open && tecla === "r";
        if (!alternar && !secao && !reiniciar) return;
        if (evento.ctrlKey || evento.altKey || evento.metaKey) return;
        evento.preventDefault();
        evento.stopImmediatePropagation();
        if (!evento.repeat) enviar(alternar ? "alternar" : reiniciar ? "reiniciar" : tecla);
    }, true);
    window.addEventListener("estado-menu", evento => {
        const {aberto, secao} = evento.detail;
        if (aberto && !menu.open) menu.showModal();
        if (!aberto && menu.open) menu.close();
        abrir.hidden = aberto;
        menu.querySelectorAll("section").forEach(painel => {
            painel.hidden = painel.id !== `secao-${secao}`;
        });
        menu.querySelectorAll("nav button").forEach(botao => {
            botao.setAttribute("aria-pressed", String(botao.dataset.acao === secao));
        });
    });
    abrir.disabled = false;
})();
