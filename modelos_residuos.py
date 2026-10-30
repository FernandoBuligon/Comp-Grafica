"""Modelos leves de resíduos, com origem no chão e peças em um só compound.

Perfis de revolução tornam garrafas, copos e potes reconhecíveis. As superfícies
internas dos recipientes são geometria real; não dependem de transparência.
"""
from math import cos, hypot, sin, tau


def faces_revolucao(perfil, segmentos=16):
    """Triangula um perfil (raio, altura) percorrido da base para o topo.

    Para fechar um recipiente, continue pela parede interna e termine no eixo.
    Retorna (faixa, face, normais); a faixa permite atribuir materiais sem
    perder detalhes.

    As normais são por vértice: em cada faixa, a normal do perfil (nr, ny) é
    girada até o ângulo do vértice. Assim a superfície fica lisa em volta do
    eixo, mas as quinas do perfil (fundo, ombro, tampa) continuam marcadas.
    """
    if segmentos < 3 or len(perfil) < 2:
        raise ValueError("O perfil precisa de dois pontos e ao menos três segmentos.")
    faces = []
    circulo = [(cos(tau * i / segmentos), sin(tau * i / segmentos))
               for i in range(segmentos + 1)]
    for faixa, ((r0, y0), (r1, y1)) in enumerate(zip(perfil, perfil[1:])):
        # Perpendicular ao segmento do perfil, apontando para fora da superfície.
        comprimento = hypot(r1 - r0, y1 - y0)
        nr, ny = (y1 - y0) / comprimento, -(r1 - r0) / comprimento
        for (ca, sa), (cb, sb) in zip(circulo, circulo[1:]):
            p = (r0 * ca, y0, r0 * sa)
            q = (r1 * ca, y1, r1 * sa)
            r = (r1 * cb, y1, r1 * sb)
            s = (r0 * cb, y0, r0 * sb)
            na = (nr * ca, ny, nr * sa)
            nb = (nr * cb, ny, nr * sb)
            if r1 > 0:
                faces.append((faixa, (p, q, r), (na, na, nb)))
            if r0 > 0:
                faces.append((faixa, (p, r, s), (na, nb, nb)))
    return faces


PERFIS = {
    "garrafa plástica": [(0, 0), (.16, 0), (.20, .06), (.20, .16),
                         (.18, .20), (.18, .47), (.20, .51), (.20, .59),
                         (.10, .72), (.085, .76), (.085, .87), (0, .87)],
    "garrafa de vidro": [(0, 0), (.17, 0), (.19, .04), (.19, .51),
                         (.17, .58), (.075, .72), (.075, .91),
                         (.09, .91), (.09, .96), (.055, .96),
                         (.055, .74), (.14, .56), (.15, .08), (0, .08)],
    "copo plástico": [(0, 0), (.17, 0), (.26, .47), (.275, .48),
                       (.275, .51), (.245, .51), (.245, .48),
                       (.15, .035), (0, .035)],
    "pote de vidro": [(0, 0), (.25, 0), (.28, .045), (.28, .41),
                      (.25, .46), (.25, .53), (.27, .54), (.27, .57),
                      (.22, .57), (.22, .47), (.245, .40),
                      (.245, .06), (0, .06)],
}

CORES_RESIDUOS = {
    "garrafa plástica": (.30, .66, .88),
    "garrafa de vidro": (.10, .43, .24),
    "copo plástico": (.93, .43, .14),
    "pote de vidro": (.30, .65, .52),
}


def criar_modelo_residuo(nome, posicao):
    from vpython import box, compound, triangle, vector, vertex

    partes = []

    def bloco(centro, tamanho, cor):
        objeto = box(pos=posicao + vector(*centro), size=vector(*tamanho),
                     color=vector(*cor), shininess=.12)
        partes.append(objeto)
        return objeto

    if nome == "folha de papel":
        bloco((0, .015, 0), (.85, .03, .62), (.96, .94, .84))
        # Linhas impressas e faixa de título, visíveis pela câmera superior.
        for z, largura in ((-.20, .59), (-.09, .62), (.01, .53), (.11, .60), (.21, .39)):
            bloco((-.04, .033, z), (largura, .006, .018), (.25, .30, .34))
    elif nome == "caixa de papelão":
        madeira = (.60, .39, .19)
        bloco((0, .025, 0), (.70, .05, .66), madeira)
        for x in (-.33, .33):
            bloco((x, .28, 0), (.04, .52, .66), madeira)
        for z in (-.31, .31):
            bloco((0, .28, z), (.62, .52, .04), madeira)
            aba = bloco((0, .55, z * 1.35), (.62, .025, .24), (.72, .50, .28))
            aba.rotate(angle=.35 if z > 0 else -.35, axis=vector(1, 0, 0))
        bloco((0, .29, .335), (.27, .20, .008), (.92, .86, .69))
        for x in (-.08, -.04, .01, .065):
            bloco((x, .29, .341), (.015, .13, .004), (.22, .18, .13))
    elif nome in PERFIS:
        cor_base = vector(*CORES_RESIDUOS[nome])
        cor_rotulo = vector(.92, .94, .85)
        cor_tampa = vector(.10, .22, .58)
        for faixa, face, normais in faces_revolucao(PERFIS[nome]):
            cor = cor_base
            if nome == "garrafa plástica":
                if faixa == 4:
                    cor = cor_rotulo  # Rótulo em volta do corpo.
                elif faixa >= 9:
                    cor = cor_tampa  # Tampa e gargalo.
            partes.append(triangle(vs=[
                vertex(pos=posicao + vector(*p), normal=vector(*n), color=cor)
                for p, n in zip(face, normais)]))
    else:
        raise ValueError(f"Modelo desconhecido: {nome}")

    return compound(partes, origin=posicao, pos=posicao,
                    shininess=.55 if "vidro" in nome else .18)
