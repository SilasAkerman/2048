"""
Game Plan

A simple changeable grid of blocks that contain a bunch of classes
Each block will handel its own drawing and color through a dictionary of values
Whenever an input is gathered, go through all blocks in the correct order and tell them to move in one direction
The ordering is important, starting closest to the direction wall and then further away
While moving, if a block hits another block with the same value:
destroy itself and call a double function on the other block
After moving, get all empty squares and span 90% chance a 2-block, and 10% chance a 4-block
After all that is done, go through all the blocks and print a grey color if it's empty,
and call the block's draw function if there is a block.

Game over will be tricky. Let's make it so that if the board is full before moving, kee track of that
Then after moving, if no combining occured, then it's game over
The score will also be tricky, let's have it so that whenever fusion happens,
increase the score by whatever the resulting block is.
Restarting will be the same as always.
"""

import pygame
import random

class Block():
     colors = {
          2: (220, 220, 220),
          4: (221, 242, 199),
          8: (253, 183, 135),
          16: (255, 141, 103),
          32: (240, 122, 91),
          64: (255, 75, 40),
          128: (245, 245, 131),
          256: (245, 245, 90),
          512: (232, 235, 49),
          1024: (212, 214, 19),
          2048: (188, 188, 0)
     }
     color = (0, 0, 0)
     WHITE = (255, 255, 255)
     def __init__(self, pos, value=2):
          self.pos = pos
          self.value = value

     def move(self, direction, height, width, game):
          # Go as far in the direction as possible and check for a fusion as well
          if direction == "left":
               change = (-1, 0)
          if direction == "right":
               change = (1, 0)
          if direction == "up":
               change = (0, -1)
          if direction == "down":
               change = (0, 1)
          
          # Let's try and do this recursivly
          futurePos = (self.pos[0] + change[0], self.pos[1] + change[1])
          if futurePos[0] < 0 or futurePos[0] > width-1 or futurePos[1] < 0 or futurePos[1] > height-1:
               return # Do nothing
          if game.board[futurePos[0]][futurePos[1]]: # There is a block here
               if game.board[futurePos[0]][futurePos[1]].value == self.value:
                    game.board[futurePos[0]][futurePos[1]].double(game)
                    game.board[self.pos[0]][self.pos[1]] = None
               return

          # If we're here, that means it's free real estate
          game.board[self.pos[0]][self.pos[1]] = None
          self.pos = futurePos
          game.board[self.pos[0]][self.pos[1]] = self
          self.move(direction, height, width, game)
          


     def double(self, game):
          self.value *= 2
          game.score += self.value

     def draw(self, game, font):
          if self.value in self.colors:
               color = self.colors[self.value]
          else:
               color = self.color
          pygame.draw.rect(game.screen, color, game.getBlockRect(self.pos[0], self.pos[1]))
          # Now to do the value on top
          valueText = font.render(str(self.value), True, self.WHITE)
          game.screen.blit(valueText, game.getBlockCenter(self.pos[0]- len(str(self.value))*0.1, self.pos[1]- 0.1)) # The font needs to be offset

class Game2048():
     backgroundColor = (100, 110, 100)
     foregroundColor = (150, 160, 150)
     def __init__(self, width, height, squareSize, squarePercentage=90):
          pygame.init()
          self.width = width
          self.height = height
          self.squareSize = squareSize
          self.squareDim = squareSize * squarePercentage // 100
          
          self.screenSize = (width*squareSize, height*squareSize)
          self.screen = pygame.display.set_mode(self.screenSize)
          self.font = pygame.font.Font("freesansbold.ttf", 64)
          self.game_init()

     def game_init(self):
          self.score = 0
          self.board = [[None for _ in range(self.width)] for _ in range(self.height)]
          self.createNewBlock(self.board)
          self.createNewBlock(self.board)

     def draw(self, board, width, height):
          self.screen.fill(self.backgroundColor)
          for column in range(width):
               for row in range(height):
                    if board[column][row]: # Is a block
                         board[column][row].draw(self, self.font)
                    else:
                         pygame.draw.rect(self.screen, self.foregroundColor, self.getBlockRect(column, row))
          
          pygame.display.update()
     
     def getBlockRect(self, column, row):
          # First, get the center of the block
          blockCenter = self.getBlockCenter(column, row)
          # Now, get the top left corner
          coords = (blockCenter[0] - self.squareDim//2, blockCenter[1] - self.squareDim//2)
          # Then, return the rectangel
          return pygame.rect.Rect(coords[0], coords[1], self.squareDim, self.squareDim)
     
     def getBlockCenter(self, column, row):
          return (column*self.squareSize + self.squareSize//2, row*self.squareSize + self.squareSize//2)

     def createNewBlock(self, board):
          spot = self.getRandomEmpty(board)
          if spot == False: # The game is over
               self.gameOver = True
               return
          value = random.choices([2, 4], weights=[9, 1])[0] # This returns a list for some reason
          board[spot[0]][spot[1]] = Block([spot[0], spot[1]], value)

     def getRandomEmpty(self, board):
          # First, gather all empties
          empties = []
          for column in range(self.width):
               for row in range(self.height):
                    if board[column][row] is None:
                         empties.append((column, row))
          if empties: # If there were any empty spots
               return random.choice(empties)
          else:
               return False # The game is over

     def moveAllBlocks(self, direction):
          # Let's add a list of ordered moves that need to be made
          orderedMoves = []
          if direction == "up":
               # The column and the row loop needs to be switched
               for row in range(self.height):
                    for column in range(self.width):
                         if self.board[column][row]:
                              orderedMoves.append((column, row))
          if direction == "down":
               # The row needs to be reversed
               for row in range(self.height-1, -1, -1): # -1 is exclusive, so it ends at 0
                    for column in range(self.width):
                         if self.board[column][row]:
                              orderedMoves.append((column, row))
          if direction == "left":
               # This is the normal way
               for column in range(self.width):
                    for row in range(self.height):
                         if self.board[column][row]:
                              orderedMoves.append((column, row))
          if direction == "right":
               # The column needs to be reversed
               for column in range(self.width-1, -1, -1):
                    for row in range(self.height):
                         if self.board[column][row]:
                              orderedMoves.append((column, row))
          
          # Now that the blocks are ordered, move each block in its order
          for block in orderedMoves:
               self.board[block[0]][block[1]].move(direction, self.width, self.height, self)
     
     def game_over(self):
          gameOver_font = pygame.font.Font("freesansbold.ttf", 64)
          score_font = pygame.font.Font("freesansbold.ttf", 32)
          info_font = pygame.font.Font("freesansbold.ttf", 16)

          gameOver_text = gameOver_font.render("GAME OVER", True, (0, 0, 0))
          score_text = score_font.render("SCORE: "+str(self.score), True, (0, 0, 0))
          info_text = info_font.render("PRESS P TO PLAY AGAIN OR PRESS BACKSPACE TO QUIT", True, (0, 0, 0))

          self.screen.blit(gameOver_text, (self.screenSize[0]//4 - 50, self.screenSize[1]//2 - 100))
          self.screen.blit(score_text, (self.screenSize[0]//4 - 50, self.screenSize[1]//2 + 100))
          self.screen.blit(info_text, (self.screenSize[0]//4 - 100, self.screenSize[1] - 100))
          pygame.display.update()

          game_running = True
          while game_running:
               clock = pygame.time.Clock()
               clock.tick(10)
               for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                         game_running = False
                    if event.type == pygame.KEYDOWN:
                         if event.key == pygame.K_p:
                              game_running = False
                              self.game_init()
                              self.play()
                         if event.key == pygame.K_BACKSPACE:
                              game_running = False

     def play(self):
          self.gameOver = False
          game_running = True
          while game_running:
               clock = pygame.time.Clock()
               clock.tick(30)
               for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                         game_running = False
                    
                    if event.type == pygame.KEYDOWN:
                         if event.key == pygame.K_UP:
                              direction = "up"
                         if event.key == pygame.K_DOWN:
                              direction = "down"
                         if event.key == pygame.K_LEFT:
                              direction = "left"
                         if event.key == pygame.K_RIGHT:
                              direction = "right"

                         if direction:
                              self.moveAllBlocks(direction)
                              self.createNewBlock(self.board)
                              direction = False
                              if self.gameOver:
                                   game_running = False
               
                    self.draw(self.board, self.width, self.height)
          self.game_over()


if __name__ == "__main__":
     Game = Game2048(4, 4, 200, squarePercentage=95)
     Game.play()