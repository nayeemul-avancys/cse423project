from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import random


class GameState:
    def __init__(self):
        self.score = 0
        self.missed_circles = 0
        self.missed_bullets = 0  
        self.paused = False
        self.game_over = False
        self.width = 700
        self.height = 700
        self.level = 1
        self.base_width = 700
        self.base_height = 700
        self.health = 3  # Add initial health
        self.special_circle_chance = 0.05
        self.healing_circle_chance = 0.02
        self.tough_circle_chance = 0.01
        self.score_circle_chance = 0.005
        self.forgiveness_circle_chance = 0.01
        self.homing_circle_chance = 0.005


        
    def get_current_width(self):
        return self.base_width - ((self.level - 1) * 50)  

    def get_current_height(self):
        return self.base_height - ((self.level - 1) * 50)  

    def get_offset_x(self):
        return (self.base_width - self.get_current_width()) // 2

    def get_offset_y(self):
        return (self.base_height - self.get_current_height()) // 2


game = GameState()
shooter = {'x': game.width//2, 'y': 10, 'width': 40, 'height': 50, 'speed': 18}  
bullets = []
circles = []



def draw_circle(xc, yc, radius):
    x = 0
    y = radius
    d = 1 - radius

    glBegin(GL_POINTS)
    while x <= y:
        
        glVertex2f(xc + x, yc + y)
        glVertex2f(xc - x, yc + y)
        glVertex2f(xc + x, yc - y)
        glVertex2f(xc - x, yc - y)
        glVertex2f(xc + y, yc + x)
        glVertex2f(xc - y, yc + x)
        glVertex2f(xc + y, yc - x)
        glVertex2f(xc - y, yc - x)

        x += 1
        if d < 0:
            d += 2 * x + 1
        else:
            y -= 1
            d += 2 * (x - y) + 1
    glEnd()


def draw_line(x1, y1, x2, y2):
    glBegin(GL_POINTS)
    
    dx = abs(x2 - x1)
    dy = abs(y2 - y1)
    

    x_inc = 1 if x2 > x1 else -1
    y_inc = 1 if y2 > y1 else -1
    
    x = x1
    y = y1
    
    glVertex2f(x, y)
    
    if dx > dy:
        d = 2*dy - dx
        for _ in range(dx):
            x += x_inc
            if d > 0:
                y += y_inc
                d += 2*(dy - dx)
            else:
                d += 2*dy
            glVertex2f(x, y)
    else:
        d = 2*dx - dy
        for _ in range(dy):
            y += y_inc
            if d > 0:
                x += x_inc
                d += 2*(dx - dy)
            else:
                d += 2*dx
            glVertex2f(x, y)
    
    glEnd()


def draw_shooter_at_pos(x, y):
    draw_line(x - 20, y + 30, x + 20, y + 30)
    draw_line(x - 20, y + 30, x, y + 50)
    draw_line(x + 20, y + 30, x, y + 50)
    draw_line(x - 20, y, x + 20, y)
    draw_line(x - 20, y + 30, x - 20, y)
    draw_line(x + 20, y + 30, x + 20, y)


def draw_shooter():
    glColor3f(1.0, 1.0, 1.0)
    draw_shooter_at_pos(shooter['x'] + game.get_offset_x(), 
                       shooter['y'] + game.get_offset_y())


def draw_buttons():

    glColor3f(0.0, 1.0, 0.0)
    draw_line(50, game.height - 30, 70, game.height - 20)
    draw_line(50, game.height - 30, 70, game.height - 40)

    glColor3f(1.0, 0.75, 0.0)
    if game.paused:
        draw_line(120, game.height - 40, 120, game.height - 20)
        draw_line(130, game.height - 40, 130, game.height - 20)
    else:
        draw_line(120, game.height - 40, 140, game.height - 30)
        draw_line(140, game.height - 30, 120, game.height - 20)

    glColor3f(1.0, 0.0, 0.0)
    draw_line(180, game.height - 40, 200, game.height - 20)
    draw_line(180, game.height - 20, 200, game.height - 40)


def check_collision(box1, box2):
    box1_left = box1['x'] - box1['width'] // 2
    box1_right = box1['x'] + box1['width'] // 2
    box1_bottom = box1['y'] - box1['height'] // 2
    box1_top = box1['y'] + box1['height'] // 2

    box2_left = box2['x'] - box2['width'] // 2
    box2_right = box2['x'] + box2['width'] // 2
    box2_bottom = box2['y'] - box2['height'] // 2
    box2_top = box2['y'] + box2['height'] // 2

    return (box1_right > box2_left and
            box1_left < box2_right and
            box1_top > box2_bottom and
            box1_bottom < box2_top)


def spawn_circle():
    chance = random.random()
    if chance < game.homing_circle_chance:  # Check for homing circle first
        circle = {
            'x': random.randint(50, game.get_current_width()-50),
            'y': game.get_current_height(),
            'radius': 20,
            'speed': 0.5,  # Slightly faster than normal circles
            'special': False,
            'healing': False,
            'tough': False,
            'score_boost': False,
            'forgiveness': False,
            'homing': True,  # New property
            'width': 40,
            'height': 40
        }
    elif chance < game.homing_circle_chance + game.forgiveness_circle_chance:  # Check for forgiveness circle first
        circle = {
            'x': random.randint(50, game.get_current_width()-50),
            'y': game.get_current_height(),
            'radius': 20,
            'speed': 0.3,
            'special': False,
            'healing': False,
            'tough': False,
            'score_boost': False,
            'forgiveness': True,  # New property
            'width': 40,
            'height': 40
        }
    elif chance < game.homing_circle_chance + game.forgiveness_circle_chance + game.score_circle_chance:  # Check for score circle first
        circle = {
            'x': random.randint(50, game.get_current_width()-50),
            'y': game.get_current_height(),
            'radius': 30,  # Largest radius
            'speed': 0.3,
            'special': False,
            'healing': False,
            'tough': False,
            'score_boost': True,  # New property
            'hitpoints': 5,  # 5 hits to destroy
            'width': 60,
            'height': 60
        }
    elif chance < game.homing_circle_chance + game.forgiveness_circle_chance + game.score_circle_chance + game.tough_circle_chance:  # Check for tough circle first
        circle = {
            'x': random.randint(50, game.get_current_width()-50),
            'y': game.get_current_height(),
            'radius': 25,  # Bigger radius to show it's tougher
            'speed': 0.3,
            'special': False,
            'healing': False,
            'tough': True,  # New property for tough circles
            'hitpoints': 3,  # Requires 3 hits
            'width': 50,
            'height': 50
        }
    elif chance < game.homing_circle_chance + game.forgiveness_circle_chance + game.score_circle_chance + game.tough_circle_chance + game.healing_circle_chance:
        circle = {
            'x': random.randint(50, game.get_current_width()-50),
            'y': game.get_current_height(),
            'radius': 15,
            'speed': 0.3,
            'special': False,
            'healing': True,  # New property for healing circles
            'width': 30,
            'height': 30
        }
    elif chance < game.homing_circle_chance + game.forgiveness_circle_chance + game.score_circle_chance + game.tough_circle_chance + game.healing_circle_chance + game.special_circle_chance:
        circle = {
            'x': random.randint(50, game.get_current_width()-50),
            'y': game.get_current_height(),
            'radius': 20,
            'speed': 0.3,
            'special': True,
            'healing': False,
            'expanding': True,
            'width': 40,
            'height': 40
        }
    else:
        circle = {
            'x': random.randint(50, game.get_current_width()-50),
            'y': game.get_current_height(),
            'radius': 15,
            'speed': 0.3,
            'special': False,
            'healing': False,
            'width': 30,
            'height': 30
        }
    circles.append(circle)


def handle_mouse(button, state, x, y):
    y = game.height - y  
    if state == GLUT_DOWN:

        if 50 <= x <= 70 and game.height - 40 <= y <= game.height - 20:
            reset_game()
            print("Starting Over")

        elif 120 <= x <= 140 and game.height - 40 <= y <= game.height - 20:
            game.paused = not game.paused
            print("Game", "Paused" if game.paused else "Resumed")

        elif 180 <= x <= 200 and game.height - 40 <= y <= game.height - 20:
            print(f"Goodbye! Final score: {game.score}")
            glutLeaveMainLoop()


def handle_keyboard(key, x, y):
    if game.paused or game.game_over:
        return

    if key == b'a' and shooter['x'] > 20:
        shooter['x'] -= shooter['speed']
    elif key == b'd' and shooter['x'] < game.get_current_width() - 20:
        shooter['x'] += shooter['speed']
    elif key == b' ':
        bullets.append({
            'x': shooter['x'],
            'y': shooter['y'] + 30,
            'width': 5,
            'height': 10,
            'speed': 8  # Increased from 1
        })


def reset_game():
    game.level=1
    game.score = 0
    game.missed_circles = 0
    game.missed_bullets = 0  
    game.paused = False
    game.game_over = False
    game.health = 3  # Reset health
    circles.clear()
    bullets.clear()
    shooter['x'] = game.width // 2
    game.special_circle_chance = 0.05
    game.healing_circle_chance = 0.02
    game.tough_circle_chance = 0.01
    game.score_circle_chance = 0.005
    game.forgiveness_circle_chance = 0.01
    game.homing_circle_chance = 0.005

def update():
    if game.paused or game.game_over:
        return

    for bullet in bullets[:]:
        bullet['y'] += bullet['speed']
        if bullet['y'] > game.get_current_height():
            bullets.remove(bullet)
            game.missed_bullets += 1  
            # print(f"Missed shots: {game.missed_bullets}")
            # if game.missed_bullets >= 5:
            #     game.game_over = True
            #     print(f"Game Over! Too many missed shots! Final score: {game.score}")
            #     return

    for circle in circles[:]:
        if circle.get('homing'):  # Add homing behavior
            dx = shooter['x'] - circle['x']
            dy = shooter['y'] - circle['y']
            distance = (dx**2 + dy**2)**0.5
            if distance > 0:  # Avoid division by zero
                circle['x'] += (dx/distance) * circle['speed']
                circle['y'] += (dy/distance) * circle['speed']
        else:
            circle['y'] -= circle['speed']
        
        if circle['special']:
            if circle['expanding']:
                circle['radius'] += 0.2
                if circle['radius'] >= 25:
                    circle['expanding'] = False
            else:
                circle['radius'] -= 0.2
                if circle['radius'] <= 15:
                    circle['expanding'] = True
            circle['width'] = circle['radius'] * 2
            circle['height'] = circle['radius'] * 2

        for bullet in bullets[:]:
            if check_collision(bullet, circle):
                if circle.get('forgiveness'):  # Handle forgiveness circle
                    game.missed_circles = max(0, game.missed_circles - 1)  # Can't go below 0
                    print(f"Forgiveness circle! Missed circles reduced to: {game.missed_circles}")
                    circles.remove(circle)
                elif circle.get('score_boost'):  # Handle score boost circle
                    circle['hitpoints'] -= 1
                    if circle['hitpoints'] <= 0:
                        game.score += 10  # Add 10 to score
                        circles.remove(circle)
                    print(f"Hit score circle! Remaining HP: {circle.get('hitpoints', 0)}")
                elif circle.get('tough'):  # Handle tough circle collision
                    circle['hitpoints'] -= 1
                    if circle['hitpoints'] <= 0:
                        game.score += 5  # More points for destroying tough circle
                        circles.remove(circle)
                    print(f"Hit tough circle! Remaining HP: {circle.get('hitpoints', 0)}")
                elif circle['healing']:
                    game.health = min(game.health + 1, 3)  # Cap health at 3
                    print(f"Health restored! Current health: {game.health}")
                elif circle['special']:
                    game.score += 3
                else:
                    game.score += 1
                print(f"Score: {game.score}")
                if bullet in bullets:
                    bullets.remove(bullet)
                if circle in circles and not circle.get('tough', False) and not circle.get('score_boost', False):  # Only remove non-tough circles immediately
                    circles.remove(circle)

        if check_collision(circle, shooter):
            game.health -= 1  # Reduce health instead of immediate game over
            circles.remove(circle)  # Remove the circle that hit the player
            print(f"Hit! Health remaining: {game.health}")
            if game.health <= 0:
                game.game_over = True
                print(f"Game Over! Final score: {game.score}")
                return
            break  # Exit the loop since we removed a circle

        if circle['y'] < 0:
            if circle in circles:
                game.missed_circles += 1
                circles.remove(circle)
                print(f"Missed circles: {game.missed_circles}")
                if game.missed_circles >= 3:
                    game.game_over = True
                    print(f"Game Over! Final score: {game.score}")
                    return

    if len(circles) < 5 and random.random() < 0.02:
        spawn_circle()

    if game.score >= game.level * 10:  # Progress every 10 points
        game.level += 1
        game.missed_bullets = 0
        game.special_circle_chance += 0.005
        game.healing_circle_chance += 0.001
        game.tough_circle_chance += 0.001
        game.score_circle_chance += 0.0005
        game.forgiveness_circle_chance += 0.001
        game.homing_circle_chance += 0.005
        circles.clear()  # Clear all circles when zone shrinks
        print(f"Level {game.level}! Field is shrinking!")
        shooter['x'] = min(shooter['x'], game.get_current_width() - 20)


def display():
    glClear(GL_COLOR_BUFFER_BIT)
    
    # Draw boundary for current level
    glColor3f(0.5, 0.5, 0.5)  # Gray color for boundary
    current_width = game.get_current_width()
    current_height = game.get_current_height()
    offset_x = game.get_offset_x()
    offset_y = game.get_offset_y()
    
    # Draw centered boundary
    draw_line(offset_x, offset_y, offset_x + current_width, offset_y)  # bottom
    draw_line(offset_x + current_width, offset_y, offset_x + current_width, offset_y + current_height)  # right
    draw_line(offset_x + current_width, offset_y + current_height, offset_x, offset_y + current_height)  # top
    draw_line(offset_x, offset_y + current_height, offset_x, offset_y)  # left

    # Adjust all game elements by offset
    shooter_x = shooter['x'] + offset_x
    shooter_y = shooter['y'] + offset_y
    
    # Draw shooter at offset position
    glColor3f(1.0, 1.0, 1.0)
    draw_shooter_at_pos(shooter_x, shooter_y)

    # Draw bullets with offset
    glColor3f(1.0, 1.0, 0.0)
    for bullet in bullets:
        draw_line(bullet['x'] + offset_x, bullet['y'] + offset_y, 
                 bullet['x'] + offset_x, bullet['y'] + offset_y + 10)

    # Draw circles with offset
    for circle in circles:
        if circle.get('homing'):
            glColor3f(1.0, 0.0, 0.0)  # Bright red for homing circles
        elif circle.get('forgiveness'):
            glColor3f(0.0, 0.5, 1.0)  # Blue color for forgiveness circles
        elif circle.get('score_boost'):
            glColor3f(1.0, 0.843, 0.0)  # Gold color for score boost circles
        elif circle.get('tough'):
            glColor3f(0.5, 0.8, 1.0)  # Light blue for tough circles
        elif circle['healing']:
            glColor3f(1.0, 1.0, 1.0)  # White for healing circles
        elif circle['special']:
            glColor3f(1.0, 0.0, 1.0)  # Existing purple for special circles
        else:
            glColor3f(0.0, 1.0, 0.0)  # Existing green for normal circles
        draw_circle(circle['x'] + offset_x, circle['y'] + offset_y, int(circle['radius']))

    draw_buttons()

    glutSwapBuffers()


def init_gl():
    glClearColor(0.0, 0.0, 0.0, 1.0)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluOrtho2D(0, game.base_width, 0, game.base_height)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    glPointSize(2.0)


def main():
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB)
    glutInitWindowSize(game.width, game.height)
    glutInitWindowPosition(100, 100)
    glutCreateWindow(b"Shoot The Circles!")
    
    init_gl()
    
    glutDisplayFunc(display)
    glutIdleFunc(lambda: (update(), glutPostRedisplay()))
    glutKeyboardFunc(handle_keyboard)
    glutMouseFunc(handle_mouse)

    print("Game Controls:")
    print("A - Move Left")
    print("D - Move Right")
    print("Spacebar - Shoot")
    print("Click the green arrow to restart")
    print("Click the yellow button to pause/resume")
    print("Click the red X to exit")
    
    glutMainLoop()


if __name__ == "__main__":
    main()