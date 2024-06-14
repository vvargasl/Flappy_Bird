import pygame
import os
import random

# definindo as costantes (configs de jogo)
larg_tela = 500
alt_tela = 800

img_cano = pygame.transform.scale2x(pygame.image.load(os.path.join('imgs', 'pipe.png')))
img_chao = pygame.transform.scale2x(pygame.image.load(os.path.join('imgs', 'base.png')))
img_backg = pygame.transform.scale2x(pygame.image.load(os.path.join('imgs', 'bg.png')))
imgs_bird = [
    pygame.transform.scale2x(pygame.image.load(os.path.join('imgs', 'bird1.png'))),
    pygame.transform.scale2x(pygame.image.load(os.path.join('imgs', 'bird2.png'))),
    pygame.transform.scale2x(pygame.image.load(os.path.join('imgs', 'bird3.png')))
]

pygame.font.init()
fonte_pontos = pygame.font.SysFont('arial', 50)
fonte_reiniciar = pygame.font.SysFont('arial', 30)

# definindo as classes
class Passaro:
    imgs = imgs_bird

    # animações da rotação
    rotacaoMax = 25
    velocidadeRotac = 20
    tempoAnimacao = 5

    # atributos do passaro
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.angulo = 0
        self.velocidade = 0
        self.altura = self.y
        self.tempo = 0
        self.contagemImg = 0
        self.imagem = self.imgs[0]

    # funcao de pular
    def pular(self):
        self.velocidade = -10.5
        self.tempo = 0
        self.altura = self.y

    # funcao de mover
    def mover(self):
        # calcular o deslocamento
        self.tempo += 1
        deslocamento = 1.5 * (self.tempo ** 2) + self.velocidade * self.tempo

        # restringir o deslocamento
        if deslocamento > 16:
            deslocamento = 16
        elif deslocamento < 0:
            deslocamento -= 2

        self.y += deslocamento

        # angulo do passaro
        if deslocamento < 0 or self.y < (self.altura + 50):
            if self.angulo < self.rotacaoMax:
                self.angulo = self.rotacaoMax
        else:
            if self.angulo > -90:
                self.angulo -= self.velocidadeRotac

    # funcao de desenhar
    def desenhar(self, tela):
        # definir qual imagem vai usar
        self.contagemImg += 1

        if self.contagemImg < self.tempoAnimacao:
            self.imagem = self.imgs[0]
        elif self.contagemImg < self.tempoAnimacao * 2:
            self.imagem = self.imgs[1]
        elif self.contagemImg < self.tempoAnimacao * 3:
            self.imagem = self.imgs[2]
        elif self.contagemImg < self.tempoAnimacao * 4:
            self.imagem = self.imgs[1]
        elif self.contagemImg >= self.tempoAnimacao * 4 + 1:
            self.imagem = self.imgs[0]
            self.contagemImg = 0

        # se o passaro tiver caindo, não vai bater asa
        if self.angulo <= -80:
            self.imagem = self.imgs[1]
            self.contagemImg = self.tempoAnimacao * 2  # ultima batida de asa pra baixo

        # desenhar a imagem
        img_rotacionada = pygame.transform.rotate(self.imagem, self.angulo)
        posicCentroImg = self.imagem.get_rect(topleft=(self.x, self.y)).center
        retangulo = img_rotacionada.get_rect(center=posicCentroImg)
        tela.blit(img_rotacionada, retangulo.topleft)

    # identificar a colisao dos objetos / cria uma mascara de pixels para avaliar a colisao
    def get_mask(self):
        return pygame.mask.from_surface(self.imagem)


class Cano:
    # parametros padroes(constantes)
    distancia = 200
    velocidade = 5

    # atributos do cano
    def __init__(self, x):
        self.x = x
        self.altura = 0
        self.posicTopo = 0
        self.posicBase = 0
        self.canoTopo = pygame.transform.flip(img_cano, False, True)
        self.canoBase = img_cano
        self.passou = False
        self.definirAltura()

    # definir altura que o cano vai aparecer
    def definirAltura(self):
        self.altura = random.randrange(50, 450)
        self.posicTopo = self.altura - self.canoTopo.get_height()
        self.posicBase = self.altura + self.distancia

    # definir movimento do cano
    def mover(self):
        self.x -= self.velocidade

    # desenhar o cano
    def desenhar(self, tela):
        tela.blit(self.canoTopo, (self.x, self.posicTopo))
        tela.blit(self.canoBase, (self.x, self.posicBase))

    # definir o colisor
    def colidir(self, passaro):
        passaroMask = passaro.get_mask()
        topoMask = pygame.mask.from_surface(self.canoTopo)
        baseMask = pygame.mask.from_surface(self.canoBase)

        distanciaTopo = (self.x - passaro.x, self.posicTopo - round(passaro.y))
        distanciaBase = (self.x - passaro.x, self.posicBase - round(passaro.y))

        topoPonto = passaroMask.overlap(topoMask, distanciaTopo)
        basePonto = passaroMask.overlap(baseMask, distanciaBase)

        if basePonto or topoPonto:
            return True
        else:
            return False


class Chao:
    # definir os parametros (constantes) do chao
    velocidade = 5
    largura = img_chao.get_width()
    imagem = img_chao

    def __init__(self, y):
        self.y = y
        self.x1 = 0
        self.x2 = self.largura

    def mover(self):  # move o chao contantemente criando um atras do outro/ arrastando o 1 toda vez q chegar na largura
        self.x1 -= self.velocidade
        self.x2 -= self.velocidade

        if self.x1 + self.largura < 0:
            self.x1 = self.x2 + self.largura
        if self.x2 + self.largura < 0:
            self.x2 = self.x1 + self.largura

    def desenhar(self, tela):
        tela.blit(self.imagem, (self.x1, self.y))
        tela.blit(self.imagem, (self.x2, self.y))


# CRIANDO O JOGO

# funcao auxiliar que vai desenhar o jogo
def desenhar_tela(tela, passaros, canos, chao, pontos):
    tela.blit(img_backg, (0, 0))  # utiliza a tupla para desenhar na posição 0

    for passaro in passaros:  # passaros no plural, é no caso de treinar uma ia para jogra
        passaro.desenhar(tela)
    for cano in canos:
        cano.desenhar(tela)

    texto = fonte_pontos.render(f"Potuação: {pontos}", 1, (255, 255, 255))
    tela.blit(texto, (larg_tela - 10 - texto.get_width(), 10))
    chao.desenhar(tela)

    pygame.display.update()

# Função para desenhar o botão de reiniciar
def desenhar_botao_reiniciar(tela):
    texto = fonte_reiniciar.render("Reiniciar", True, (255, 0, 0))
    retangulo = texto.get_rect(center=(larg_tela // 2, alt_tela // 2))
    pygame.draw.rect(tela, (0, 0, 0), retangulo.inflate(20, 10))
    tela.blit(texto, retangulo)
    pygame.display.update()
    return retangulo

# Função para verificar clique no botão de reiniciar
def verificar_clique_reiniciar(retangulo):
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            pygame.quit()
            quit()
        if evento.type == pygame.MOUSEBUTTONDOWN:
            if retangulo.collidepoint(evento.pos):
                return True
    return False

# funcao principal que vai executar o jogo
def main():
    pygame.init()
    tela = pygame.display.set_mode((larg_tela, alt_tela))
    pontos = 0
    relogio = pygame.time.Clock()  # atualiza a tela com a funcao interna do pygame

    rodando = True
    while rodando:
        passaros = [Passaro(230, 350)]
        chao = Chao(730)
        canos = [Cano(700)]
        pontos = 0
        morreu = False

        while not morreu:
            relogio.tick(30)

            # Interação com o jogador
            for evento in pygame.event.get():
                if evento.type == pygame.QUIT:
                    pygame.quit()
                    quit()
                if evento.type == pygame.KEYDOWN:
                    if evento.key == pygame.K_SPACE:
                        for passaro in passaros:
                            passaro.pular()

            # Mover os objetos do jogo
            for passaro in passaros:
                passaro.mover()
            chao.mover()

            adicionarCano = False
            removerCanos = []
            for cano in canos:
                cano.mover()
                # Verificar se o cano colidiu com o passaro
                for passaro in passaros:
                    if cano.colidir(passaro):
                        morreu = True

                if cano.x + cano.canoTopo.get_width() < 0:
                    removerCanos.append(cano)

                if not cano.passou and cano.x < passaro.x:
                    cano.passou = True
                    adicionarCano = True

            if adicionarCano:
                pontos += 1
                canos.append(Cano(600))

            for cano in removerCanos:
                canos.remove(cano)

            for passaro in passaros:
                if passaro.y + passaro.imagem.get_height() >= 730 or passaro.y < 0:
                    morreu = True

            desenhar_tela(tela, passaros, canos, chao, pontos)

        # Desenhar botão de reiniciar quando o jogador morrer
        retangulo_reiniciar = desenhar_botao_reiniciar(tela)
        while morreu:
            if verificar_clique_reiniciar(retangulo_reiniciar):
                morreu = False
                rodando = True
            else:
                rodando = False

    pygame.quit()
    quit()

if __name__ == "__main__":
    main()
