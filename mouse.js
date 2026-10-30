// Arrastar com o botão esquerdo gira o personagem; a roda aproxima ou afasta a câmera.
(() => {
    const cena = canvas.get_selected();
    const area = cena.wrapper[0];
    const enviar = acao => cena.trigger("keydown", {
        key: `mouse:${acao}`, which: 0, shift: false, ctrl: false, alt: false
    });
    let arrastando = false;
    let deslocamento = 0;
    // Fase de captura: o GlowScript interrompe a propagação dos eventos do canvas.
    const naCena = evento => area.contains(evento.target);
    window.addEventListener("mousedown", evento => {
        if (evento.button === 0 && naCena(evento)) arrastando = true;
    }, true);
    window.addEventListener("mouseup", () => { arrastando = false; }, true);
    window.addEventListener("mousemove", evento => {
        if (arrastando) deslocamento += evento.movementX;
    }, true);
    window.addEventListener("wheel", evento => {
        if (!naCena(evento)) return;
        evento.preventDefault();
        enviar(`zoom:${Math.sign(evento.deltaY)}`);
    }, {capture: true, passive: false});
    // Agrupa o movimento de cada quadro em um único envio ao Python.
    (function enviarGiro() {
        if (deslocamento !== 0) {
            enviar(`girar:${deslocamento}`);
            deslocamento = 0;
        }
        window.requestAnimationFrame(enviarGiro);
    })();
})();
