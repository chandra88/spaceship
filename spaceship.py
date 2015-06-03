import random, math, time, pygame, sys, copy
from pygame.locals import *
import pygame.mixer

'''-------------------------------------
Program:	Classic spaceship game	
Author:		Chandra Nepali
Version:	1.1
Date:		June 2, 2015	
Contact:	coder5678@gmail.com
-------------------------------------'''

# globals for user interface
WIDTH = 800
HEIGHT = 600
score = 0
lives = 3
timeSet = 0.5
rock_group = set([])
missile_group = set([])
started = False
explosion_group = set([])

pygame.init()
pygame.font.init()
pygame.mixer.init()
elTime = 0.0
stTime = 0.0

#-------------------------------------------------------------------------------
# covert angle to x any y-components
def angle_to_vector(ang):
	return [math.cos(ang), math.sin(ang)]

#-------------------------------------------------------------------------------
# stire image information
class ImageInfo:
	def __init__(self, center, size, radius = 0, lifespan = None, animated = False):
		self.center = center
		self.size = size
		self.radius = radius
		if lifespan: self.lifespan = lifespan
		else: self.lifespan = float('inf')
		self.animated = animated

	def get_center(self): return self.center
	def get_size(self): return self.size
	def get_radius(self): return self.radius
	def get_lifespan(self): return self.lifespan
	def get_animated(self): return self.animated

#-------------------------------------------------------------------------------
global sound_missile, sound_track, sound_explosion, ship_thrust_sound

ship_info = ImageInfo([45, 45], [90, 90], 35)

debris_info = ImageInfo([320, 240], [640, 480])
debris_image = pygame.image.load("debris2_blue.png")

nebula_info = ImageInfo([400, 300], [800, 600])
nebula_image = pygame.image.load("nebula_blue.s2014.png")

splash_info = ImageInfo([200, 150], [400, 300])
splash_image = pygame.image.load("splash.png")

missile_info = ImageInfo([5,5], [10, 10], 3, 50)
missile_image = pygame.image.load("shot2.png")

asteroid_info = ImageInfo([45, 45], [90, 90], 40)
asteroid_image = pygame.image.load("asteroid_blue.png")

explosion_info = ImageInfo([64, 64], [128, 128], 17, 24, True)
explosion_image = pygame.image.load("explosion_alpha.png")

missile_sound = pygame.mixer.Sound('missile.ogg')
missile_sound.set_volume(0.3)

sound_track = pygame.mixer.Sound('soundtrack.ogg')
sound_track.set_volume(0.1)

explosion_sound = pygame.mixer.Sound('explosion.ogg')
explosion_sound.set_volume(0.3)

ship_thrust_sound = pygame.mixer.Sound('thrust.ogg')
ship_thrust_sound.set_volume(0.2)

#-------------------------------------------------------------------------------
# Ship class
class Ship:
	def __init__(self, pos, vel, angle, image1, image2, info):
		self.pos = [pos[0], pos[1]]
		self.vel = [vel[0], vel[1]]
		self.thrust = False
		self.angle = angle
		self.angle_vel = 0
		self.image1 = image1
		self.image2 = image2
		self.radius = info.get_radius()
		self.center = info.get_center() 
   
	def get_pos(self): return self.pos
	def get_radius(self): return self.radius
    	
	#-----------------------------------------
	def draw(self, displaySurface):
		if(self.thrust):
			rot_image = pygame.transform.rotate(self.image2, self.angle)
			rot_rect = rot_image.get_rect()
			rot_rect.center = (self.pos[0], self.pos[1])
			displaySurface.blit(rot_image, rot_rect)
			ship_thrust_sound.play()
		else:
			rot_image = pygame.transform.rotate(self.image1, self.angle)
			rot_rect = rot_image.get_rect()
			rot_rect.center = (self.pos[0], self.pos[1])
			displaySurface.blit(rot_image, rot_rect)
			ship_thrust_sound.stop()
	#		sound_track.play()

	#-----------------------------------------
	def rotateRight(self): self.angle_vel -= 1.5
	def rotateLeft(self): self.angle_vel += 1.5        
	def noRotate(self): self.angle_vel = 0.0

	def set_thrust(self, th): self.thrust = th
	def get_thrust(self): return self.thrust

	def update(self):
		self.pos[0] += self.vel[0]
		self.pos[1] -= self.vel[1]
		self.angle += self.angle_vel

		if(self.pos[0] > WIDTH): self.pos[0] = 0
		if(self.pos[0] < 0): self.pos[0] = WIDTH    
		if(self.pos[1] > HEIGHT): self.pos[1] = 0  
		if(self.pos[1] < 0): self.pos[1] = HEIGHT     

		ve = math.sqrt(self.vel[0]*self.vel[0] + self.vel[1]*self.vel[1])    
		if(self.thrust): ve += 0.1  
		self.vel[0] = ve*math.cos(self.angle*3.14/180)
		self.vel[1] = ve*math.sin(self.angle*3.14/180)
        
		self.vel[0] *= 0.975
		self.vel[1] *= 0.975

	#-----------------------------------------
	def shoot(self):
		global missile_group
		pos1 = self.pos[0] + self.radius*math.cos(self.angle*3.14/180)
		pos2 = self.pos[1] - self.radius*math.sin(self.angle*3.14/180)
	
		ve = math.sqrt(self.vel[0]*self.vel[0] + self.vel[1]*self.vel[1])
		vel1 = (ve + 10.0)*math.cos(self.angle*3.14/180)
		vel2 = (ve - 10.0)*math.sin(self.angle*3.14/180)

		missile = Sprite([pos1, pos2], [vel1, vel2], 0, 0, missile_image, missile_info, missile_sound)
		missile_group.add(missile)

#-------------------------------------------------------------------------------
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
			sound.play()
   
	def get_pos(self): return self.pos
	def get_radius(self): return self.radius
	def get_velocity(self): return self.vel
	def get_image(self): return self.image 
	def get_animated(self): return self.animated   

	def draw(self, displaySurface):
		if(self.animated):
			pos1 = self.age*self.image_size[0]
			pos2 = self.image_center[1]/2
			size1 = self.image_size[0]
			size2 = self.image_size[1]
			displaySurface.blit(self.image, self.pos, (pos1, pos2, size1, size2))
		else:
			displaySurface.blit(self.image, self.pos)

	def update(self):
		self.pos[0] += self.vel[0]
		self.pos[1] += self.vel[1]
		self.angle += self.angle_vel
        
		if(self.pos[0] > WIDTH): self.pos[0] = 0
		if(self.pos[0] < 0): self.pos[0] = WIDTH
		if(self.pos[1] > HEIGHT): self.pos[1] = 0
		if(self.pos[1] < 0): self.pos[1] = HEIGHT
		self.age += 1
		if(self.age < self.lifespan): return True
		else: return False
        
	def collide(self, other):
		r1 = self.get_radius()
		pos1 = self.get_pos()
		r2 = other.get_radius()
		pos2 = other.get_pos()

		d = math.sqrt( (pos1[0]-pos2[0])*(pos1[0]-pos2[0]) + (pos1[1]-pos2[1])*(pos1[1]-pos2[1]) )
		if(d <= (r1+r2)): return True
		else: return False

#-------------------------------------------------------------------------------
def draw():
	global timeSet, lives, score, started
    
	# animiate background
	timeSet += 1
	wtime = (timeSet/4) % WIDTH
	center = debris_info.get_center()
	size = debris_info.get_size()

	displaySurface.blit(debris_image, (wtime - WIDTH/1, HEIGHT/8))
	displaySurface.blit(debris_image, (wtime - WIDTH/2, HEIGHT/8))

	my_ship.update()
	my_ship.draw(displaySurface)

	rock_spawner(my_ship)
	process_sprite_group(rock_group)
	if(group_collide(rock_group, my_ship)): lives -= 1

	process_sprite_group(missile_group)
	if(group_group_collide(rock_group, missile_group)): score += 1

	process_sprite_group(explosion_group)
	if(lives <= 0):	started = False

	if(not started):
		copy_group = set(rock_group)
		for rock in copy_group: rock_group.remove(rock)
		displaySurface.blit(splash_image, [WIDTH/4, HEIGHT/4])

	writeScore(displaySurface)

#-------------------------------------------------------------------------------
def rock_spawner(my):
	global rock_group
	pos1 = random.random() * WIDTH
	pos2 = random.random() * HEIGHT
	ship_pos = my.get_pos()
	d = math.sqrt( (ship_pos[0]-pos1)*(ship_pos[0]-pos1) + (ship_pos[1]-pos2)*(ship_pos[1]-pos2) )
#	sep = d - my.get_radius()*1.5    
	sep = d - my.get_radius() - 1.2*asteroid_info.get_radius()
	vel = random.random() * 3.0
	ang = random.random() * 3.14
	vel1 = vel*math.cos(ang)
	vel2 = vel*math.sin(ang)
	ang_vel = -0.1 + random.random() * 0.1

	rock = Sprite([pos1, pos2], [vel1, vel2], ang, ang_vel, asteroid_image, asteroid_info)
	if(len(rock_group) < 12 and started and sep > 0.0): rock_group.add(rock)

#-------------------------------------------------------------------------------
def process_sprite_group(group):
	copy_group = set(group)
	for item in copy_group:
		if(not item.update()): group.remove(item)
		item.draw(displaySurface)

#-------------------------------------------------------------------------------
def group_collide(group, other):
	global explosion_group, missile_group
	copy_group = set(group)

	for item in copy_group:
		if(item.collide(other)):
			pos = item.get_pos()
			vel = item.get_velocity()
			group.remove(item)
			if(other in missile_group): 
				missile_group.remove(other)
				pass
			exp = Sprite(pos, vel, 0, 0, explosion_image, explosion_info, explosion_sound)
			explosion_group.add(exp)
			return True
	return False

#-------------------------------------------------------------------------------
def group_group_collide(rocks, missiles):
	for missile in missiles:
		if(group_collide(rocks, missile)): return True

#-------------------------------------------------------------------------------
def keystate(evt, my):
	global started, lives, score, elTime, stTime
	if evt.type == pygame.KEYDOWN:
		if(evt.key == pygame.K_LEFT and started == True): my.rotateLeft()
		elif(evt.key == pygame.K_RIGHT and started == True): my.rotateRight()
		elif(evt.key == pygame.K_UP and started == True): my.set_thrust(True)
		elif(evt.key == pygame.K_SPACE and started == True): my.shoot()
		elif(evt.key == pygame.K_RETURN and started == False):
			started = True
			lives = 3
			score = 0
			elTime = 0.0
			stTime = time.time()

	elif evt.type == pygame.KEYUP:
		if(evt.key == pygame.K_LEFT or evt.key == pygame.K_RIGHT): my.noRotate()
		elif(evt.key == pygame.K_UP): my.set_thrust(False)
		elif(evt.key == pygame.K_RETURN): pass

	elif(evt.type == pygame.MOUSEBUTTONDOWN and started == False):
		started = True
		lives = 3
		score = 0
		stTime = time.time()
#-------------------------------------------------------------------------------
saved_lives = ''
saved_score = ''
saved_elTime = ''
def writeScore(displaySurface):
	global stTime, saved_lives, saved_score, saved_elTime
	now = time.time()
	tm = now - stTime
	elTime = formatTime(tm)
	w = ''
	if(started): 
		w = 'lives = ' + str(lives) + '    score = ' + str(score) + '   elapsed time = ' + elTime
		saved_lives = lives
		saved_score = score
		saved_elTime = elTime
	else: w = 'lives = ' + str(saved_lives-1) + '    score = ' + str(saved_score) + '   elapsed time = ' + saved_elTime

	liveSurf = basicFont.render(w, 1, (0, 255, 0))
	liveRect = liveSurf.get_rect()
	liveRect.center = (240, 20)
	displaySurface.blit(liveSurf, liveRect)

#-------------------------------------------------------------------------------

def formatTime(tm):
	hr = int(tm / 3600)
	if len(str(hr)) < 2: hr = '0' + str(hr)
	else: hr = str(hr)

	mn = int((tm % 3600)/60)
	if len(str(mn)) < 2: mn = '0' + str(mn)
	else: mn = str(mn)

	se = (tm % 3600) % 60
	se = '%0.2f'%se

	tt = hr + ' : ' + mn + ' : ' + str(se)
	return tt
#-------------------------------------------------------------------------------


clock = pygame.time.Clock()
displaySurface = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Asteroids')
basicFont = pygame.font.SysFont('comicsansms', 16)

bkimage = pygame.image.load('nebula_blue.s2014.png').convert()
bkimage = pygame.transform.scale(bkimage, (WIDTH, HEIGHT))

ship1 = pygame.image.load('ship1.png')
ship2 = pygame.image.load('ship2.png')
my_ship = Ship([WIDTH/2, HEIGHT/2], [0, 0], 0, ship1, ship2, ship_info)

#-------------------------------------------------------------------------------
started = True

stTime = time.time()
while True:
	displaySurface.blit(bkimage, (0, 0))
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			pygame.quit()
			sys.exit()

		keystate(event, my_ship)

	draw()

	pygame.display.update()
	clock.tick(400)
#-------------------------------------------------------------------------------
