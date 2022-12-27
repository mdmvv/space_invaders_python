import os
import time
import sys
import termios
import fcntl

def set_lines(n):
	sys.stdout.write("\r\x1b[K")
	for i in range(n-1):
		sys.stdout.write("\n\x1b[K")

def clear_lines(n):
	sys.stdout.write("\r\x1b[K")
	for i in range(n-1):
		sys.stdout.write("\x1b[F\x1b[K")

def save_cursor_position():
	sys.stdout.write("\x1b[s")

def set_cursor_position(x, y):
	if x < 0:
		sys.stdout.write("\x1b[%dD" % -x)
	if x > 0:
		sys.stdout.write("\x1b[%dC" % x)
	if y < 0:
		sys.stdout.write("\x1b[%dB" % -y)
	if y > 0:
		sys.stdout.write("\x1b[%dA" % y)

def reset_cursor_position():
	sys.stdout.write("\x1b[u")

def hide_cursor():
	sys.stdout.write("\x1b[?25l")

def show_cursor():
	sys.stdout.write("\x1b[?25h")

def disable_echo():
	fd = sys.stdin.fileno()
	new_attr = termios.tcgetattr(fd)
	new_attr[3] &= ~termios.ECHO
	termios.tcsetattr(fd, termios.TCSANOW, new_attr)

def enable_echo():
	fd = sys.stdin.fileno()
	new_attr = termios.tcgetattr(fd)
	new_attr[3] |= termios.ECHO
	termios.tcsetattr(fd, termios.TCSANOW, new_attr)

def get_input():
	fd = sys.stdin.fileno()

	old_attr = termios.tcgetattr(fd)
	new_attr = termios.tcgetattr(fd)
	new_attr[3] &= ~termios.ICANON
	termios.tcsetattr(fd, termios.TCSANOW, new_attr)

	old_flags = fcntl.fcntl(fd, fcntl.F_GETFL)
	new_flags = fcntl.fcntl(fd, fcntl.F_GETFL)
	new_flags |= os.O_NONBLOCK
	fcntl.fcntl(fd, fcntl.F_SETFL, new_flags)

	try:
		return ord(sys.stdin.read(1))
	except TypeError:
		return None
	finally:
		termios.tcsetattr(fd, termios.TCSAFLUSH, old_attr)
		fcntl.fcntl(fd, fcntl.F_SETFL, old_flags)

def get_action(input):
	input_map = {"left": 97, "right": 100, "exit": 27}

	for action in input_map.keys():
		if input_map[action] == input:
			return action

class Cannon:
	def __init__(self, x, y, speed, left_limit, right_limit):
		self.shape = "▄■▄"
		self.x = x
		self.y = y
		self.speed = speed
		self.move = 0
		self.left_limit = left_limit
		self.right_limit = right_limit - (len(self.shape) - 1)

	def update_logic(self, action):
		if action == "left":
			self.move -= self.speed
		if action == "right":
			self.move += self.speed
		while self.move <= -1:
			if self.x > self.left_limit:
				self.x -= 1
			self.move += 1
		while self.move >= 1:
			if self.x < self.right_limit:
				self.x += 1
			self.move -= 1

class Invader:
	def __init__(self, x, y, direction, speed, left_limit, right_limit):
		self.shape = "╒■╕"
		self.x = x
		self.y = y
		self.direction = direction
		self.speed = speed
		self.move = 0
		self.left_limit = left_limit
		self.right_limit = right_limit - (len(self.shape) - 1)

	def update_logic(self, action):
		self.move += self.speed
		while self.move >= 1:
			if self.x <= self.left_limit or self.x >= self.right_limit:
				self.y -= 1
				self.direction *= -1
			self.x += 1 * self.direction
			self.move -= 1

def update_logic(units, action):
	for unit in units:
		unit.update_logic(action)

def refresh_field(height, units):
	clear_lines(height)
	reset_cursor_position()

	for unit in units:
		set_cursor_position(unit.x, unit.y)
		sys.stdout.write(unit.shape)
		reset_cursor_position()

	sys.stdout.flush()

field_width = 55
field_height = 32
updates_per_second = 60

hide_cursor()
disable_echo()
set_lines(field_height)
save_cursor_position()

units = []
cannon = Cannon(x=26, y=4, speed=1, left_limit=4, right_limit=50)
invader = Invader(x=6, y=23, direction=1, speed=1/120, left_limit=2, right_limit=52)
units.append(cannon)
units.append(invader)
action = None

refresh_field(field_height, units)

updates = 0
last_update_time = time.time()

while True:
	input = get_input()
	if input:
		action = get_action(input)

	if action == "exit":
		break

	if time.time() - last_update_time >= 1 / updates_per_second:
		update_logic(units, action)
		refresh_field(field_height, units)

		action = None
		updates += 1
		last_update_time = time.time()

clear_lines(field_height)
enable_echo()
show_cursor()