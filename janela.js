// Executado pela legenda HTML do VPython, depois do bind("resize") no Python.
(() => {
    const cena = canvas.get_selected();
    document.documentElement.style.cssText = "margin:0;padding:0;overflow:hidden";
    document.body.style.cssText = "margin:0;padding:0;overflow:hidden";
    // Ancora a cena à área útil, independentemente das margens do contêiner.
    cena.wrapper.css({position: "fixed", top: 0, left: 0, display: "block"});
    cena.wrapper.find(".ui-resizable-handle").hide();

    let pendente = false;
    function ajustar() {
        pendente = false;
        const largura = Math.max(1, window.innerWidth);
        const altura = Math.max(1, window.innerHeight);
        cena.wrapper.css({width: largura, height: altura});
        if (cena.width === largura && cena.height === altura) return;
        // Alterar somente CSS esticaria a imagem sem atualizar a projeção.
        cena.width = largura;
        cena.height = altura;
        cena.trigger("resize", {event: "resize"});
    }
    function agendar() {
        if (pendente) return;
        pendente = true;
        window.requestAnimationFrame(ajustar);
    }
    window.addEventListener("resize", agendar);
    document.addEventListener("fullscreenchange", agendar);
    agendar();
})();
