import math
import random
import simplegui
# globals for user interface
WIDTH = 800
HEIGHT = 600
score = 0
lives = 3
time = 0
started = False
rock_num = 0
rock_group = set([])
collision = False
missile_group = set([])
num = 0
explosion_group = set([])
ROCK_DIM = 64

class ImageInfo:
    def __init__(self, center, size, radius = 0, lifespan = None, animated = False):
        self.center = center
        self.size = size
        self.radius = radius
        if lifespan:
            self.lifespan = lifespan
        else:
            self.lifespan = float('inf')
        self.animated = animated

    def get_center(self):
        return self.center

    def get_size(self):
        return self.size

    def get_radius(self):
        return self.radius

    def get_lifespan(self):
        return self.lifespan

    def get_animated(self):
        return self.animated

    
# debris images - debris1_brown.png, debris2_brown.png, debris3_brown.png, debris4_brown.png
#                 debris1_blue.png, debris2_blue.png, debris3_blue.png, debris4_blue.png, debris_blend.png
debris_info = ImageInfo([320, 240], [640, 480])
debris_image = simplegui.load_image("http://commondatastorage.googleapis.com/codeskulptor-assets/lathrop/debris2_blue.png")

# nebula images - nebula_brown.png, nebula_blue.png
nebula_info = ImageInfo([400, 300], [800, 600])
nebula_image = simplegui.load_image("http://commondatastorage.googleapis.com/codeskulptor-assets/lathrop/nebula_blue.f2014.png")

# splash image
splash_info = ImageInfo([200, 150], [400, 300])
splash_image = simplegui.load_image("http://commondatastorage.googleapis.com/codeskulptor-assets/lathrop/splash.png")

# ship image
ship_info = ImageInfo([45, 45], [90, 90], 35)

ship_image = simplegui.load_image("http://commondatastorage.googleapis.com/codeskulptor-assets/lathrop/double_ship.png")

# missile image - shot1.png, shot2.png, shot3.png
missile_info = ImageInfo([5,5], [10, 10], 3, 50)
missile_image = simplegui.load_image("http://commondatastorage.googleapis.com/codeskulptor-assets/lathrop/shot2.png")

# asteroid images - asteroid_blue.png, asteroid_brown.png, asteroid_blend.png
asteroid_info = ImageInfo([45, 45], [90, 90], 40)
asteroid_image = simplegui.load_image("http://commondatastorage.googleapis.com/codeskulptor-assets/lathrop/asteroid_blue.png")

# animated explosion - explosion_orange.png, explosion_blue.png, explosion_blue2.png, explosion_alpha.png
explosion_info = ImageInfo([64, 64], [128, 128], 17, 24, True)
explosion_image = simplegui.load_image("http://commondatastorage.googleapis.com/codeskulptor-assets/lathrop/explosion_alpha.png")

# sound assets purchased from sounddogs.com, please do not redistribute
soundtrack = simplegui.load_sound("http://commondatastorage.googleapis.com/codeskulptor-assets/sounddogs/soundtrack.mp3")
missile_sound = simplegui.load_sound("http://commondatastorage.googleapis.com/codeskulptor-assets/sounddogs/missile.mp3")
missile_sound.set_volume(.5)
ship_thrust_sound = simplegui.load_sound("http://commondatastorage.googleapis.com/codeskulptor-assets/sounddogs/thrust.mp3")
explosion_sound = simplegui.load_sound("http://commondatastorage.googleapis.com/codeskulptor-assets/sounddogs/explosion.mp3")

# alternative upbeat soundtrack by composer and former IIPP student Emiel Stopler
# please do not redistribute without permission from Emiel at http://www.filmcomposer.nl
#soundtrack = simplegui.load_sound("https://storage.googleapis.com/codeskulptor-assets/ricerocks_theme.mp3")

# helper functions to handle transformations
def angle_to_vector(ang):
    return [math.cos(ang), math.sin(ang)]

def dist(p,q):
    return math.sqrt((p[0] - q[0]) ** 2+(p[1] - q[1]) ** 2)


# Ship class
class Ship:
    def __init__(self, pos, vel, angle, image, info):
        self.pos = [pos[0],pos[1]]
        self.vel = [vel[0],vel[1]]
        self.thrust = False
        self.angle = angle
        self.angle_vel = 0
        self.image = image
        self.image_center = info.get_center()
        self.image_size = info.get_size()
        self.radius = info.get_radius()
        
    def draw(self,canvas):
        canvas.draw_image(self.image, self.image_center, self.image_size, self.pos, self.image_size, self.angle)

    def update(self):
        friction_index = 0.03
        acc = 0.5
        self.pos[0] += self.vel[0]
        self.pos[1] += self.vel[1]
        self.angle += self.angle_vel
        self.vel[0] *= (1 - friction_index)
        self.vel[1] *= (1 - friction_index) 
        if self.thrust:
            angle_to_vector(self.angle)
            self.vel[0] += acc * math.cos(self.angle)
            self.vel[1] += acc * math.sin(self.angle)
            
        # ship's position wraps around the screen when it goes off the edge
        if self.pos[0] <= 0:
            self.pos[0] += 800
        if self.pos[0] >= 800:
            self.pos[0] = 0
        if self.pos[1] <= 0:
            self.pos[1] += 600
        if self.pos[1] >= 600:
            self.pos[1] = 0
        
    def turn_left(self):
        self.angle_vel -= 0.08
        
    def turn_right(self):
        self.angle_vel += 0.08 
     
    def rotate_stop(self):
        self.angle_vel = 0
        
    def thrust_on(self, option):
        if option == "on":
            self.thrust = True
            self.image_center = [135, 45]
            ship_thrust_sound.play()
        if option == "off":
            self.thrust = False
            self.image_center= [45, 45]
            ship_thrust_sound.rewind()
            
    def missile(self):
        forward = angle_to_vector(self.angle)
        missile_pos = [self.pos[0] + self.radius * forward[0], self.pos[1] + self.radius * forward[1]]
        missile_vel = [self.vel[0] + 6 * forward[0], self.vel[1] + 6 * forward[1]]
        a_missile = Sprite(missile_pos, missile_vel, self.angle, 0, missile_image, missile_info, missile_sound)
        missile_group.add(a_missile)
        
    def get_pos(self):
        return self.pos
    
    def get_radius(self):
        return self.radius
    

# Sprite class
class Sprite:
    def __init__(self, pos, vel, ang, ang_vel, image, info, sound = None):
        self.pos = [pos[0],pos[1]]
        self.vel = [vel[0],vel[1]]
        self.angle = ang
        self.angle_vel = ang_vel
        self.image = image
        self.image_center = info.get_center()
        self.image_size = info.get_size()
        self.radius = info.get_radius()
        self.lifespan = info.get_lifespan()
        self.animated = info.get_animated()
        self.age = 0
        if sound:
            sound.rewind()
            sound.play()
   
    def draw(self, canvas):
        canvas.draw_image(self.image, self.image_center, self.image_size, self.pos, self.image_size, self.angle)
    
    def update(self):
        self.angle += self.angle_vel        
        self.pos[0] += self.vel[0]
        self.pos[1] += self.vel[1]
        # ship's position wraps around the screen when it goes off the edge
        if self.pos[0] <= 0:
            self.pos[0] += 800
        if self.pos[0] >= 800:
            self.pos[0] = 0
        if self.pos[1] <= 0:
            self.pos[1] += 600
        if self.pos[1] >= 600:
            self.pos[1] = 0 
            
        #fix the issue of missile sticking around forever
        self.age += 1
        if self.age >= self.lifespan:
            return True
        return False
    
    def collide(self, other_object):
        if dist(self.pos, other_object.pos) <= self.radius + other_object.radius:
            return True
        return False
    

def key_down(key):
    if key == simplegui.KEY_MAP["left"]:
        my_ship.turn_left() 
    if key == simplegui.KEY_MAP["right"]:
        my_ship.turn_right()
    if key == simplegui.KEY_MAP["up"]:
        my_ship.thrust_on("on")
    if key == simplegui.KEY_MAP["space"]:
        my_ship.missile()
            
def key_up(key):
    if key == simplegui.KEY_MAP["left"]:
        my_ship.rotate_stop() 
    if key == simplegui.KEY_MAP["right"]:
        my_ship.rotate_stop()
    if key == simplegui.KEY_MAP["up"]:
        my_ship.thrust_on("off")

# mouseclick handlers that reset UI and conditions whether splash image is drawn
def click(pos):
    global started, lives, score
    center = [WIDTH / 2, HEIGHT / 2]
    size = splash_info.get_size()
    inwidth = (center[0] - size[0] / 2) < pos[0] < (center[0] + size[0] / 2)
    inheight = (center[1] - size[1] / 2) < pos[1] < (center[1] + size[1] / 2)
    if (not started) and inwidth and inheight:
        started = True        
    if started:
        soundtrack.play()
    lives = 3
    score = 0
    
def draw(canvas):
    global time, started, my_ship, lives, score, num, rock_num, ROCK_DIM
    # animiate background
    time += 1
    wtime = (time / 4) % WIDTH
    center = debris_info.get_center()
    size = debris_info.get_size()
    canvas.draw_image(nebula_image, nebula_info.get_center(), nebula_info.get_size(), [WIDTH / 2, HEIGHT / 2], [WIDTH, HEIGHT])
    canvas.draw_image(debris_image, center, size, (wtime - WIDTH / 2, HEIGHT / 2), (WIDTH, HEIGHT))
    canvas.draw_image(debris_image, center, size, (wtime + WIDTH / 2, HEIGHT / 2), (WIDTH, HEIGHT))

    # check for collision
    if group_collide(rock_group, my_ship):
        lives -= 1
        #reset the game
        if lives == 0:
            soundtrack.rewind()
            reset()
            
    #detect collision between rocks and missiles
    if group_group_collide(rock_group, missile_group):
        score += num
        
    # draw ship and sprites
    my_ship.draw(canvas)
    if started:
        process_sprite_group(canvas)
        #if process_sprite_group(canvas):
            #for m in explosion_group:
                #rock_index = (time % ROCK_DIM) // 1
                #current_rock_center = [m.image_center[0] + rock_index * m.image_size[0], m.image_center[1]]
                #canvas.draw_image(explosion_image, current_rock_center, m.image_size, m.image_center, m.image_size)
        
    # update ship and sprites
    my_ship.update()
    
    # draw UI
    canvas.draw_text ('Lives: '+ str(lives), (20, 45), 40, "White")
    canvas.draw_text ('Score: '+ str(score), (650, 45), 40, "White")

    # draw splash screen if not started
    if not started:
        canvas.draw_image(splash_image, splash_info.get_center(), 
                          splash_info.get_size(), [WIDTH / 2, HEIGHT / 2], 
                          splash_info.get_size())

                
# timer handler that spawns a rock    
def rock_spawner():
    global rock_num, started, my_ship
    rock_pos = [random.randrange(0, WIDTH), random.randrange(0, HEIGHT)]
    rock_vel = [random.random() * 0.6 - 0.1, random.random() * 0.6 - 0.1]
    rock_avel = random.random() * 0.2 - 0.1
    a_rock = Sprite(rock_pos, rock_vel, 0, rock_avel, asteroid_image, asteroid_info)
    rock_num += 1
    if started:
        if rock_num <= 12:
            if dist(rock_pos, my_ship.pos) >= 75:
                rock_group.add(a_rock)        

def process_sprite_group(canvas):
    for i in rock_group:
        i.update()
        i.draw(canvas)
        #if i.animated:
            #return True
        #return False
    for a in missile_group:
        a.update()
        if a.update():
            missile_group.remove(a)
        a.draw(canvas)
        
def group_collide(rock, ship):
    for n in rock:
        if n.collide(ship):
            rock.remove(n)
            return True
    return False

def group_group_collide(rock, missile):
    global num
    for a in rock:
        for b in missile:
            if a.collide(b):
                rock.remove(a)
                explosion_group.add(a)
                explosion_sound.play()
                num = 1
                return True
    return False

# reset the game
def reset():
    global rock_group, started, rock_num
    rock_num = 0
    rock_group = set([])
    soundtrack.play()
    started = False
    
# initialize frame
frame = simplegui.create_frame("Asteroids", WIDTH, HEIGHT)

# initialize ship and two sprites
my_ship = Ship([WIDTH / 2, HEIGHT / 2], [0, 0], 0, ship_image, ship_info)
a_rock = Sprite([WIDTH / 3, HEIGHT / 3], [1, 1], 0, 0, asteroid_image, asteroid_info)
a_missile = Sprite([2 * WIDTH / 3, 2 * HEIGHT / 3], [-1,1], 0, 0, missile_image, missile_info, missile_sound)

# register handlers
frame.set_draw_handler(draw)
frame.set_keydown_handler(key_down)
frame.set_keyup_handler(key_up)
timer = simplegui.create_timer(1000.0, rock_spawner)
frame.set_mouseclick_handler(click)

# get things rolling
timer.start()
frame.start()