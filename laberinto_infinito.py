
import pygame
import random
import sys
from collections import deque
from enum import Enum

# Inicializar Pygame
pygame.init()

# Constantes
ANCHO_VENTANA = 800
ALTO_VENTANA = 600
TAMAÑO_CELDA = 20
FILAS = ALTO_VENTANA // TAMAÑO_CELDA
COLUMNAS = ANCHO_VENTANA // TAMAÑO_CELDA

# Colores
NEGRO = (0, 0, 0)
BLANCO = (255, 255, 255)
ROJO = (255, 0, 0)
VERDE = (0, 255, 0)
AZUL = (0, 0, 255)
AMARILLO = (255, 255, 0)
GRIS = (128, 128, 128)

class TipoCelda(Enum):
    PARED = 0
    CAMINO = 1
    JUGADOR = 2
    SALIDA = 3

class Laberinto:
    def __init__(self, filas, columnas):
        self.filas = filas
        self.columnas = columnas
        self.grid = [[TipoCelda.PARED for _ in range(columnas)] for _ in range(filas)]
        self.visitado = [[False for _ in range(columnas)] for _ in range(filas)]
        
    def es_valida(self, fila, col):
        return 0 <= fila < self.filas and 0 <= col < self.columnas
    
    def obtener_vecinos(self, fila, col):
        """Obtiene vecinos válidos para el algoritmo de generación"""
        vecinos = []
        direcciones = [(-2, 0), (2, 0), (0, -2), (0, 2)]  # Arriba, Abajo, Izquierda, Derecha
        
        for df, dc in direcciones:
            nueva_fila, nueva_col = fila + df, col + dc
            if (self.es_valida(nueva_fila, nueva_col) and 
                not self.visitado[nueva_fila][nueva_col]):
                vecinos.append((nueva_fila, nueva_col))
        
        return vecinos
    
    def generar_laberinto_dfs(self):
        """Genera laberinto usando DFS (Depth-First Search) con backtracking"""
        # Stack para DFS
        stack = []
        
        # Comenzar desde una posición aleatoria impar
        inicio_fila = random.randrange(1, self.filas, 2)
        inicio_col = random.randrange(1, self.columnas, 2)
        
        # Marcar como visitado y camino
        self.visitado[inicio_fila][inicio_col] = True
        self.grid[inicio_fila][inicio_col] = TipoCelda.CAMINO
        stack.append((inicio_fila, inicio_col))
        
        while stack:
            fila_actual, col_actual = stack[-1]
            vecinos = self.obtener_vecinos(fila_actual, col_actual)
            
            if vecinos:
                # Elegir vecino aleatorio
                siguiente_fila, siguiente_col = random.choice(vecinos)
                
                # Marcar como visitado
                self.visitado[siguiente_fila][siguiente_col] = True
                self.grid[siguiente_fila][siguiente_col] = TipoCelda.CAMINO
                
                # Crear camino entre celdas (romper pared)
                pared_fila = (fila_actual + siguiente_fila) // 2
                pared_col = (col_actual + siguiente_col) // 2
                self.grid[pared_fila][pared_col] = TipoCelda.CAMINO
                
                stack.append((siguiente_fila, siguiente_col))
            else:
                # Backtrack
                stack.pop()
    
    def colocar_entrada_y_salida(self):
        """Coloca la entrada y salida del laberinto"""
        # Entrada en la esquina superior izquierda
        for fila in range(self.filas):
            for col in range(self.columnas):
                if self.grid[fila][col] == TipoCelda.CAMINO:
                    self.entrada = (fila, col)
                    break
            else:
                continue
            break
        
        # Salida en la esquina inferior derecha
        for fila in range(self.filas-1, -1, -1):
            for col in range(self.columnas-1, -1, -1):
                if self.grid[fila][col] == TipoCelda.CAMINO:
                    self.salida = (fila, col)
                    self.grid[fila][col] = TipoCelda.SALIDA
                    break
            else:
                continue
            break

class Jugador:
    def __init__(self, fila, col):
        self.fila = fila
        self.col = col
        self.fila_anterior = fila
        self.col_anterior = col
    
    def mover(self, nueva_fila, nueva_col, laberinto):
        """Mueve el jugador si la posición es válida"""
        if (laberinto.es_valida(nueva_fila, nueva_col) and 
            laberinto.grid[nueva_fila][nueva_col] != TipoCelda.PARED):
            
            self.fila_anterior = self.fila
            self.col_anterior = self.col
            self.fila = nueva_fila
            self.col = nueva_col
            return True
        return False

class JuegoLaberinto:
    def __init__(self):
        self.pantalla = pygame.display.set_mode((ANCHO_VENTANA, ALTO_VENTANA))
        pygame.display.set_caption("Laberinto Infinito - Nivel 1")
        self.reloj = pygame.time.Clock()
        
        self.nivel = 1
        self.generar_nuevo_nivel()
        
    def generar_nuevo_nivel(self):
        """Genera un nuevo nivel del laberinto"""
        self.laberinto = Laberinto(FILAS, COLUMNAS)
        self.laberinto.generar_laberinto_dfs()
        self.laberinto.colocar_entrada_y_salida()
        
        # Colocar jugador en la entrada
        entrada_fila, entrada_col = self.laberinto.entrada
        self.jugador = Jugador(entrada_fila, entrada_col)
        
        pygame.display.set_caption(f"Laberinto Infinito - Nivel {self.nivel}")
    
    def manejar_eventos(self):
        """Maneja los eventos del juego"""
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                return False
            
            elif evento.type == pygame.KEYDOWN:
                nueva_fila, nueva_col = self.jugador.fila, self.jugador.col
                
                if evento.key == pygame.K_UP or evento.key == pygame.K_w:
                    nueva_fila -= 1
                elif evento.key == pygame.K_DOWN or evento.key == pygame.K_s:
                    nueva_fila += 1
                elif evento.key == pygame.K_LEFT or evento.key == pygame.K_a:
                    nueva_col -= 1
                elif evento.key == pygame.K_RIGHT or evento.key == pygame.K_d:
                    nueva_col += 1
                elif evento.key == pygame.K_r:
                    # Regenerar nivel actual
                    self.generar_nuevo_nivel()
                
                # Intentar mover jugador
                if self.jugador.mover(nueva_fila, nueva_col, self.laberinto):
                    # Verificar si llegó a la salida
                    if (self.jugador.fila, self.jugador.col) == self.laberinto.salida:
                        self.nivel += 1
                        self.generar_nuevo_nivel()
        
        return True
    
    def dibujar(self):
        """Dibuja el juego en pantalla"""
        self.pantalla.fill(NEGRO)
        
        # Dibujar laberinto
        for fila in range(self.laberinto.filas):
            for col in range(self.laberinto.columnas):
                x = col * TAMAÑO_CELDA
                y = fila * TAMAÑO_CELDA
                rect = pygame.Rect(x, y, TAMAÑO_CELDA, TAMAÑO_CELDA)
                
                if self.laberinto.grid[fila][col] == TipoCelda.PARED:
                    pygame.draw.rect(self.pantalla, BLANCO, rect)
                elif self.laberinto.grid[fila][col] == TipoCelda.CAMINO:
                    pygame.draw.rect(self.pantalla, NEGRO, rect)
                elif self.laberinto.grid[fila][col] == TipoCelda.SALIDA:
                    pygame.draw.rect(self.pantalla, VERDE, rect)
        
        # Dibujar jugador
        jugador_x = self.jugador.col * TAMAÑO_CELDA
        jugador_y = self.jugador.fila * TAMAÑO_CELDA
        jugador_rect = pygame.Rect(jugador_x, jugador_y, TAMAÑO_CELDA, TAMAÑO_CELDA)
        pygame.draw.rect(self.pantalla, ROJO, jugador_rect)
        
        # Dibujar información del nivel
        fuente = pygame.font.Font(None, 36)
        texto_nivel = fuente.render(f"Nivel: {self.nivel}", True, AMARILLO)
        self.pantalla.blit(texto_nivel, (10, 10))
        
        # Instrucciones
        fuente_pequeña = pygame.font.Font(None, 24)
        instrucciones = [
            "WASD o Flechas: Mover",
            "R: Regenerar nivel",
            "Verde: Salida"
        ]
        
        for i, instruccion in enumerate(instrucciones):
            texto = fuente_pequeña.render(instruccion, True, BLANCO)
            self.pantalla.blit(texto, (10, ALTO_VENTANA - 80 + i * 25))
        
        pygame.display.flip()
    
    def ejecutar(self):
        """Bucle principal del juego"""
        ejecutando = True
        
        while ejecutando:
            ejecutando = self.manejar_eventos()
            self.dibujar()
            self.reloj.tick(60)  # 60 FPS
        
        pygame.quit()
        sys.exit()

# Ejecutar el juego
if __name__ == "__main__":
    juego = JuegoLaberinto()
    juego.ejecutar()
