from tkinter import *
import random


# Game settings
GAME_WIDTH = 700        # Width of the game area
GAME_HEIGHT = 700
SPEED = 80
SPACE_SIZE = 50 
BODY_PARTS = 3
SNAKE_COLOR = "#00FF00"
FOOD_COLOR = "#FFF000"
BACKGROUND_COLOR = "#000000"


# Snake class to represent the snake object in the game
class Snake:
    def __init__(self):
        self.body_size = BODY_PARTS  # Set initial body size
        self.coordinates = []        # List to store coordinates of each body part
        self.squares = []            # List to store each body part as a rectangle shape
        
        # Initialize the snake at the top-left of the canvas
        for i in range(0, BODY_PARTS):
            self.coordinates.append([0,0])
        
        # Create the snake body squares on the canvas    
        for x, y in self.coordinates:
            square = canvas.create_rectangle(x, y, x + SPACE_SIZE, y + SPACE_SIZE, fill=SNAKE_COLOR, tag="snake")
            self.squares.append(square)

# Food class to represent food object in the game
class Food:
    def __init__(self):
        # Randomly place the food within the game area grid
        x = random.randint(0, (GAME_WIDTH/SPACE_SIZE)-1) * SPACE_SIZE
        y = random.randint(0, (GAME_HEIGHT/SPACE_SIZE)-1) * SPACE_SIZE 

        self.coordinates = [x, y]
        # Create food on the canvas as an oval
        canvas.create_oval(x, y, x + SPACE_SIZE, y + SPACE_SIZE, fill=FOOD_COLOR, tag="food")

# Function to execute the next turn of the game
def next_turn(snake, food):
    x, y = snake.coordinates[0] # Get current head position of the snake
    if direction == "up":
        y -= SPACE_SIZE
    elif direction == "down":
        y += SPACE_SIZE
    elif direction == "left":
        x -= SPACE_SIZE
    elif direction == "right":
        x += SPACE_SIZE
    
    # Update snake head coordinates 
    snake.coordinates.insert(0, (x,y))
    
    # Create new square for the snake's head in the new position
    square = canvas.create_rectangle(x, y, x + SPACE_SIZE, y + SPACE_SIZE, fill=SNAKE_COLOR)
    
    snake.squares.insert(0, square)
    
    # Check if snake has eaten the food
    if x == food.coordinates[0] and y == food.coordinates[1]:
        
        global score
        score += 1
        label.config(text="Score:{}".format(score))
        
        canvas.delete("food") # Remove current food from canvas
        food = Food()         # Generate new food

    
    
    else:
        # Remove last part of snake if food was not eaten
        del snake.coordinates[-1]

        canvas.delete(snake. squares[-1])

        del snake.squares[-1]
    
    # Check for collisions (with wall or self)
    if check_collisions(snake):
        game_over()  #End game if collision detected
    else:  
        # Schedule the next turn
        window.after(SPEED, next_turn, snake, food)

# Function to change the snake's direction based on key presses
def change_direction(new_direction):
    global direction
    
    if new_direction == 'left':
        if direction != 'right':
            direction = new_direction
    
    elif new_direction == 'right':
        if direction != 'left':
            direction = new_direction
    
    elif new_direction == 'up':
        if direction != 'down':
            direction = new_direction
            
    elif new_direction == 'down':
        if direction != 'up':
            direction = new_direction
            
def check_collisions(snake):
    x, y = snake.coordinates[0]
    
    # Check if snake hits the wall
    if x < 0 or x >= GAME_WIDTH:
        return True
    
    elif y < 0 or y >= GAME_HEIGHT:
        return True
    
    # Check if snake collides with itself
    for body_part in snake.coordinates[1:]:
        if x == body_part[0] and y == body_part[1]:
            return  True
        
    return False

# Function to handle game over scenario
def game_over():
    canvas.delete(ALL)
    
    canvas.create_text(canvas.winfo_width()/2, canvas.winfo_height()/2, 
                       font=("console", 70), text="GAME OVER", fill="red", tag="gameover")
    

# Setup main window
window = Tk()
window.title("Snake game")
window.resizable(False, False)


score = 0 # Initialize score
direction = 'down'  # Initialize direction of snake

# Display score on the window
label = Label(window, text="Score:{}".format(score), font=("consoles", 40))
label.pack()

# Create the game canvas
canvas = Canvas(window, bg=BACKGROUND_COLOR, height=GAME_HEIGHT, width=GAME_WIDTH)
canvas.pack()

# Update window to get final dimensions
window.update()

# Center the window on the screen
window_width = window.winfo_width()
window_height = window.winfo_height()
screen_width = window.winfo_screenwidth()
screen_height = window.winfo_screenheight()

x = int((screen_width/2) - (window_width/2))
y = int((screen_height/2) - (window_height/2))

window.geometry(f"{window_width}x{window_height}+{x}+{y}")

# Bind arrow keys to control the snake's direction
window.bind('<Left>', lambda event: change_direction('left'))
window.bind('<Right>', lambda event: change_direction('right'))
window.bind('<Up>', lambda event: change_direction('up'))
window.bind('<Down>', lambda event: change_direction('down'))



# Initialize snake and food objects and start the game loop
snake = Snake()
food = Food()
next_turn(snake, food)
window.mainloop()