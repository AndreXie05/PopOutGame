import pygame
import sys
from moves import PopOutBoard
from mcst import mcts

class PopOutGame:
    def __init__(self):
        pygame.init()
        self.SQUARESIZE = 100
        self.width = 7 * self.SQUARESIZE
        self.height = 7 * self.SQUARESIZE 
        
        # Define a janela sem bordas (NOFRAME) como tinhas antes
        self.screen = pygame.display.set_mode((self.width, self.height), pygame.NOFRAME)
        self.board = PopOutBoard()
    
        self.font_title = pygame.font.SysFont("monospace", 45, bold=True)
        self.font_menu = pygame.font.SysFont("monospace", 28, bold=True)
        
        try:
            menu_raw = pygame.image.load("menu.jpg") 
            self.splash_image = pygame.transform.scale(menu_raw, (self.width, self.height))
        except:
            self.splash_image = None

        self.state = "SPLASH"
        self.mode = 1 

    def draw_board(self):
        # Desenha a estrutura azul e os buracos brancos
        for c in range(self.board.cols):
            for r in range(self.board.rows):
                pygame.draw.rect(self.screen, (0, 0, 255), 
                                (c*self.SQUARESIZE, r*self.SQUARESIZE + self.SQUARESIZE, self.SQUARESIZE, self.SQUARESIZE))
                pygame.draw.circle(self.screen, (255, 255, 255), 
                                  (int(c*self.SQUARESIZE + self.SQUARESIZE/2), int(r*self.SQUARESIZE + self.SQUARESIZE + self.SQUARESIZE/2)), 
                                  int(self.SQUARESIZE/2 - 5))
        
        # Desenha as peças dos jogadores
        for c in range(self.board.cols):
            for r in range(self.board.rows):
                if self.board.board[r][c] == 1:
                    pygame.draw.circle(self.screen, (255, 0, 0), 
                                      (int(c*self.SQUARESIZE + self.SQUARESIZE/2), int(r*self.SQUARESIZE + self.SQUARESIZE + self.SQUARESIZE/2)), 
                                      int(self.SQUARESIZE/2 - 5))
                elif self.board.board[r][c] == 2:
                    pygame.draw.circle(self.screen, (255, 255, 0), 
                                      (int(c*self.SQUARESIZE + self.SQUARESIZE/2), int(r*self.SQUARESIZE + self.SQUARESIZE + self.SQUARESIZE/2)), 
                                      int(self.SQUARESIZE/2 - 5))

    def draw_game(self):
        # Fundo do topo branco para consistência
        self.screen.fill((255, 255, 255))  
        posx = pygame.mouse.get_pos()[0]
        col = posx // self.SQUARESIZE
        if col >= self.board.cols: col = self.board.cols - 1
        
        color = (255, 0, 0) if self.board.current_player == 1 else (255, 255, 0)
        pygame.draw.circle(self.screen, color, 
                          (int(col * self.SQUARESIZE + self.SQUARESIZE/2), int(self.SQUARESIZE/2)), 
                          int(self.SQUARESIZE/2 - 5))
        
        self.draw_board()
        pygame.display.update()

    def run(self):
        while True:
            if self.state == "SPLASH":
                if self.splash_image:
                    self.screen.blit(self.splash_image, (0, 0))
                else:
                    self.screen.fill((50, 50, 50))
                pygame.display.update()
                
                for event in pygame.event.get():
                    if event.type == pygame.QUIT: sys.exit()
                    if event.type == pygame.MOUSEBUTTONDOWN: self.state = "SELECTION"

            elif self.state == "SELECTION":
                self.screen.fill((10, 20, 60)) # Azul escuro
                
                title_surf = self.font_title.render("MODO DE JOGO", True, (0, 255, 255))
                m1_surf = self.font_menu.render("1. Humano vs IA", True, (255, 255, 255))
                m2_surf = self.font_menu.render("2. Humano vs Humano", True, (255, 255, 255))
                m3_surf = self.font_menu.render("3. IA vs IA", True, (255, 255, 255))
                
                center_x = self.width // 2
                self.screen.blit(title_surf, (center_x - title_surf.get_width() // 2, 150))
                self.screen.blit(m1_surf, (center_x - m1_surf.get_width() // 2, 280))
                self.screen.blit(m2_surf, (center_x - m2_surf.get_width() // 2, 350))
                self.screen.blit(m3_surf, (center_x - m3_surf.get_width() // 2, 420))
                pygame.display.update()
                
                for event in pygame.event.get():
                    if event.type == pygame.QUIT: sys.exit()
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_1: self.mode = 1; self.state = "JOGANDO"
                        if event.key == pygame.K_2: self.mode = 2; self.state = "JOGANDO"
                        if event.key == pygame.K_3: self.mode = 3; self.state = "JOGANDO"

            elif self.state == "JOGANDO":
                self.draw_game()
                
                if self.board.is_terminal():
                    msg = "EMPATE!"
                    color = (100, 100, 100)
                    if self.board.check_four_in_a_row(1):
                        msg = "IA 1 VENCEU!" if self.mode == 3 else "HUMANO VENCEU!"
                        color = (255, 0, 0)
                    elif self.board.check_four_in_a_row(2):
                        msg = "HUMANO 2 VENCEU!" if self.mode == 2 else "IA VENCEU!"
                        color = (255, 220, 0)

                    pygame.draw.rect(self.screen, (255, 255, 255), (0, 0, self.width, self.SQUARESIZE))
                    txt_surf = self.font_title.render(msg, True, color)
                    txt_rect = txt_surf.get_rect(center=(self.width // 2, self.SQUARESIZE // 2))
                    self.screen.blit(txt_surf, txt_rect)
                    self.draw_board()
                    pygame.display.update()
                    pygame.time.wait(4000)
                    self.board = PopOutBoard()
                    self.state = "SPLASH"
                    continue

                is_human_turn = (self.mode == 1 and self.board.current_player == 1) or (self.mode == 2)

                if is_human_turn:
                    for event in pygame.event.get():
                        if event.type == pygame.QUIT: sys.exit()
                        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                            self.board = PopOutBoard(); self.state = "SPLASH"
                        
                        if event.type == pygame.MOUSEBUTTONDOWN:
                            mouse_x, mouse_y = event.pos
                            col = mouse_x // self.SQUARESIZE
                            if col >= self.board.cols: col = self.board.cols - 1
                            
                            # LÓGICA DE CLIQUE: Se clicar na última linha do tabuleiro, faz POP
                            if mouse_y > 6 * self.SQUARESIZE:
                                m_type = 'pop'
                            else:
                                m_type = 'drop'
                            
                            if self.board.is_valid_move(col, m_type):
                                self.board = self.board.apply_move((col, m_type))
                else:
                    for event in pygame.event.get():
                        if event.type == pygame.QUIT: sys.exit()

                    # IA Pensa
                    best_node = mcts(self.board, iterations=600)
                    
                    if best_node.move:
                        col_ia, m_type = best_node.move
                        # Visualização da IA no topo
                        self.screen.fill((255, 255, 255))
                        color = (255, 0, 0) if self.board.current_player == 1 else (255, 255, 0)
                        pygame.draw.circle(self.screen, color, 
                                          (int(col_ia * self.SQUARESIZE + self.SQUARESIZE/2), int(self.SQUARESIZE/2)), 
                                          int(self.SQUARESIZE/2 - 5))
                        self.draw_board()
                        pygame.display.update()
                        pygame.time.wait(800) 
                    
                    self.board = best_node.state

