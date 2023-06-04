# mdpAgents.py
# parsons/20-nov-2017
#
# Version 1
#
# The starting point for CW2.
#
# Intended to work with the PacMan AI projects from:
#
# http://ai.berkeley.edu/
#
# These use a simple API that allow us to control Pacman's interaction with
# the environment adding a layer on top of the AI Berkeley code.
#
# As required by the licensing agreement for the PacMan AI we have:
#
# Licensing Information:  You are free to use or extend these projects for
# educational purposes provided that (1) you do not distribute or publish
# solutions, (2) you retain this notice, and (3) you provide clear
# attribution to UC Berkeley, including a link to http://ai.berkeley.edu.
#
# Attribution Information: The Pacman AI projects were developed at UC Berkeley.
# The core projects and autograders were primarily created by John DeNero
# (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# Student side autograding was added by Brad Miller, Nick Hay, and
# Pieter Abbeel (pabbeel@cs.berkeley.edu).

# The agent here is was written by Simon Parsons, based on the code in
# pacmanAgents.py

from pacman import Directions
from game import Agent
import api
import random
import game
import util
import aStar
import aStar

class Grid:

	# Adapted from Lab Solutions 5 (Parsons, 2017)
	# Draws a grid - where an array has one position for each element on the grid
	# Not used for any function in the map other than printing a pretty grid

	def __init__(self, width, height):
		self.width = width
		self.height = height
		subgrid = []
		for i in range(self.height):
			row = []
			for j in range(self.width):
				row.append(0)
			subgrid.append(row)

		self.grid = subgrid

	def setValue(self, x, y, value):
		self.grid[y][x] = value

	def getValue(self, x, y):
		return self.grid[y][x]

	def getHeight(self):
		return self.height

	def getWidth(self):
		return self.width

	#Print grid
	def display(self):
		for i in range(self.height):
			for j in range(self.width):
				# print grid elements with no newline
				print self.grid[i][j],
			print
		print

	def prettyDisplay(self):
		for i in range(self.height):
			for j in range(self.width):
				# print grid elements with no newline
				print self.grid[self.height - (i + 1)][j],
			print
		print

class MDPAgent(Agent):
	"""
	The MDP Agent is one that calculates utilities for the map and for pacman's location
	In order to gain the best movement policy for every state of the map

	It updates every time a move is made (i.e. when a food is eaten, or a ghost moves)
	(i.e. recalculates using valueIteration)
	Number of loops in valueIteration depends on map size for efficiency. The smaller the map is,
	the lower the number of loops required.
	"""
	# Constructor: this gets run when we first invoke pacman.py
	def __init__(self):
		print "Starting up MDPAgent!"
		name = "Pacman"

		# Store permanent values
		# These lists store values that remain more or less static throughout
		# the entire game (with the exception of coordinates moving from capsules/foodMap to visited)
		self.visited = []
		self.foodMap = []
		self.wallMap = []
		self.capsuleMap = []
		self.stateHistory = []


	# Gets run after an MDPAgent object is created and once there is
	# game state to access.
	def registerInitialState(self, state):
		print "Running registerInitialState for MDPAgent!"
		print "I'm at:"
		print api.whereAmI(state)

		# Make map. taken from lab 5 solutions (Parsons, 2017)
		self.makeMap(state)
		self.addWallsToMap(state)
		self.map.display()

	# This is what gets run in between multiple games
	def final(self, state):
		print "Looks like the game just ended!"

		self.visited = []
		self.foodMap = []
		self.wallMap = []
		self.capsuleMap = []


	# Make a map of a grid
	def makeMap(self, state):
		corners = api.corners(state)
		height = self.getLayoutHeight(corners)
		width = self.getLayoutWidth(corners)

		self.map = Grid(width, height)

	# Functions that get height and width of grid (+1 to account for 0-indexing)
	def getLayoutHeight(self, corners):
		yVals = []
		for i in range(len(corners)):
			yVals.append(corners[i][1])
		return max(yVals) + 1

	def getLayoutWidth(self, corners):
		xVals = []
		for i in range(len(corners)):
			xVals.append(corners[i][0])
		return max(xVals) + 1

	# Place walls into map grids
	def addWallsToMap(self, state):
		walls = api.walls(state)
		for i in range(len(walls)):
			self.map.setValue(walls[i][0], walls[i][1], "#")

	def makeValueMap(self, state):
		# This function returns a dictionary of all possible coordinates on a grid
		# As well as all the values that are assigned to each coordinate-category
		# Food is given a value of 5
		# Empty spaces are given a value of 0
		# Capsules are given a value of 5


		food = api.food(state)
		walls = api.walls(state)
		capsules = api.capsules(state)
		pacman = api.whereAmI(state)
		corners = api.corners(state)

		# If pacman's location has not been recorded in a list of visited locations
		# Record it
		if pacman not in self.visited:
			self.visited.append(pacman)

		# Up
		for i in food:
			if i not in self.foodMap:
				self.foodMap.append(i)

		for i in walls:
			if i not in self.wallMap:
				self.wallMap.append(i)

		for i in capsules:
			if i not in self.capsuleMap:
				self.capsuleMap.append(i)


		# Create a dictionary storing all
		# Food, wall and capsule locations, while assigning values to them
		self.foodDict = dict.fromkeys(self.foodMap, 5)
		self.wallDict = dict.fromkeys(self.wallMap, '#')
		self.capsuleDict = dict.fromkeys(self.capsuleMap, 5)

		# Initiate valueMap to store all coordinates
		valueMap = {}
		valueMap.update(self.foodDict)
		valueMap.update(self.wallDict)
		valueMap.update(self.capsuleDict)

		# Using the APIs to get coordinates tends to leave out pacman
		# Initial position
		# This will sweep through all available coordinates
		# And add the square to the list with 0

		for i in range(self.getLayoutWidth(corners) - 1):
			for j in range(self.getLayoutHeight(corners) - 1):
				if (i, j) not in valueMap.keys():
					valueMap[(i, j)] = 0

		# Update function. If pacman has been seen to visit a square
		# It means he has eaten the food or capsules there
		# Thus, set their values to 0
		for i in self.foodMap:
			if i in self.visited:
				valueMap[i] = 0

		for i in self.capsuleMap:
			if i in self.visited:
				valueMap[i] = 0

		# Another update function
		# Updates the location of the ghost
		ghosts = api.ghosts(state)
		ghostStates = api.ghostStatesWithTimes(state)

		for i in valueMap.keys():
			for j in range(len(ghosts)):
				ghostTime = ghostStates[j][1]
				#Convert coordinates to int (keys are stored as int, but coordinates from API are stored as float)
				if ((int(ghosts[j][0])), (int(ghosts[j][1]))) == i and ghostTime >= 1: #230519 jjm/ Added ghostTime
					valueMap[i] = 10	#230520 jjm/ Changed 5 -> 500
				elif ((int(ghosts[j][0])), (int(ghosts[j][1]))) == i:
					valueMap[i] = -10	#230520 jjm/ Changed -10 -> -1000
				

		return valueMap


	def getTransition(self, x, y, valueMap):
		# This function calculates the maximum expected utility of a coordinate on the initiated valueMap
		# An sets the value of the coordinate to the MEU
		# Which will then later be used as the transition value during value iteration

		# initialise a dictionary to store utility values
		self.util_dict = {"n_util": 0.0, "s_util": 0.0, "e_util": 0.0, "w_util": 0.0}
		# valueMap should be a dictionary containing a list of values assigned to every grid
		self.valueMap = valueMap

		self.x = x
		self.y = y

		north = (self.x, self.y + 1)
		south = (self.x, self.y - 1)
		east = (self.x + 1, self.y)
		west = (self.x - 1, self.y)
		stay = (self.x, self.y)


		# If North is not a wall, then multiply expected utility;
		# else multiply expected utility of staying in place
		# If the perpendicular directions are not walls, then multiply expected utility of those
		# else multiply expected utility of just staying in place

		if self.valueMap[north] != "#":
			n_util =Directions.NORTH
		else:
			n_util =Directions.STOP

		self.util_dict["n_util"] = n_util


		# Repeat for the rest of the directions
		if self.valueMap[south] != "#":
			s_util = Directions.SOUTH
		else:
			s_util = Directions.STOP


		self.util_dict["s_util"] = s_util


		if self.valueMap[east] != "#":
			e_util = Directions.EAST
		else:
			e_util = Directions.STOP

		
		self.util_dict["e_util"] = e_util

		if self.valueMap[west] != "#":
			w_util = Directions.WEST
		else:
			w_util = Directions.STOP


		self.util_dict["w_util"] = w_util

		# Take the max value in the dictionary of stored utilities
		# Assign current grid MEU
		# Return updated valueMap that has transition values
		self.valueMap[stay] = max(self.util_dict.values())

		return self.valueMap[stay]

	def valueIteration(self, state, reward, gamma, V1):
		# This function does valueIteration for larger maps
		# Reward = assigned reward for every state
		# Gamma = discount function
		# V1 = valueMap initialised with values for every element in the map
		# Where food = 5, ghost = -10, capsules = 5

		corners = api.corners(state)
		walls = api.walls(state)
		food = api.food(state)
		ghosts = api.ghosts(state)
		capsules = api.capsules(state)
		ghostStates = api.ghostStatesWithTimes(state) # 230520 added

		#Get max width and height
		maxWidth = self.getLayoutWidth(corners) - 1
		maxHeight = self.getLayoutHeight(corners) - 1

		# Create a list of buffer coordinates within 3 squares NSEW of ghosts to calculate
		# value iteration around the ghosts (otherwise, food taken to be terminal value)
		# will not have negative utilities - meaning pacman will still go for those food
		# if a ghost is near by
		# This does not work in small maps due to the virtue of those maps being far too small
		# making this function redundant for them


		
		foodToCalculate = []
		for i in range(3): #230520 jjm/ Changed 5 -> 3
			for j in range(len(ghosts)):			#230520 jjm/ Add for check ghostState
				ghostTime = ghostStates[j][1]		#
				if (ghostTime <= 1) :				#
					for x in range(len(ghosts)):
						# Append coordinates 3 squares east to ghost
						if (int(ghosts[x][0] + i), int(ghosts[x][1])) not in foodToCalculate:
							foodToCalculate.append((int(ghosts[x][0] + i), int(ghosts[x][1])))
						# Append coordinates 3 squares west to ghost
						if (int(ghosts[x][0] - i), int(ghosts[x][1])) not in foodToCalculate:
							foodToCalculate.append((int(ghosts[x][0] - i), int(ghosts[x][1])))
						# Append coordinates 3 squares north to ghost
						if (int(ghosts[x][0]), int(ghosts[x][1] + 1)) not in foodToCalculate:
							foodToCalculate.append((int(ghosts[x][0]), int(ghosts[x][1] + i)))
						# Append coordinates 3 squares south to ghost
						if (int(ghosts[x][0]), int(ghosts[x][1] - 1)) not in foodToCalculate:
							foodToCalculate.append((int(ghosts[x][0]), int(ghosts[x][1] - i)))


		# A list of coordinates that should not be calculated
		# Although it might be simple to just use foodToCalculate
		# it does not take into account when the food is eaten or not
		# So this list checks against available food that intersect with being outside of
		# 5 squares of each ghost
		doNotCalculate = []
		for i in food:
			if i not in foodToCalculate:
				doNotCalculate.append(i)

		# raise value error if gamma is not between 0 and 1
		if not (0 < gamma <= 1):
			raise ValueError("MDP must have a gamma between 0 and 1.")

		# Implement Bellman equation with _-loop iteration
		loops = 200	#230520 jjm/ Changed 100 -> ?
		while loops > 0:
			V = V1.copy() # This will store the old values
			for i in range(maxWidth):
				for j in range(maxHeight):
					# Exclude any food because in this case it is the terminal state
					# Except for food that are within 5 squares north/south/east/west of the ghost
					if (i, j) not in walls and (i, j) not in doNotCalculate and (i, j) not in ghosts and (i, j) not in capsules:
						V1[(i, j)] = reward + gamma * self.getTransition(i, j, V)
					
					#230520 jjm, Add panalty for not moving
					if (i, j) == api.whereAmI(state):
						V1[(i, j)] -= 5
			loops -= 1

	def valueIterationSmall(self, state, reward, gamma, V1):
		# Similar to valueIteration function
		# does not calculate buffers around ghosts (cause it would be too small)
		# meant for maps smaller than 10 x 10

		corners = api.corners(state)
		walls = api.walls(state)
		food = api.food(state)
		ghosts = api.ghosts(state)
		capsules = api.capsules(state)

		maxWidth = self.getLayoutWidth(corners) - 1
		maxHeight = self.getLayoutHeight(corners) - 1

		if not (0 < gamma <= 1):
			raise ValueError("MDP must have a gamma between 0 and 1.")

		# Implement Bellman equation with 10-loop iteration
		# Since smaller maps do not require as big of a value iteration loop
		loops = 100
		while loops > 0:
			V = V1.copy() # This will store the old values
			for i in range(maxWidth):
				for j in range(maxHeight):
					# Exclude any food because in this case it is the terminal state
					if (i, j) not in walls and (i, j) not in food and (i, j) not in ghosts and (i, j) not in capsules:
						V1[(i, j)] = reward + gamma * self.getTransition(i, j, V)
			loops -= 1

	#230601 jjm/ add dangerDirection
	def getPolicy(self, state, iteratedMap, dangerDirection):
		# gets movement policy for pacman's location at a given state
		# using valueiteration map that is updated at every step

		pacman = api.whereAmI(state)

		# put in a valueMap that has been run across valueIteration (otherwise)
		# a proper policy would not be able to be retrieved
		self.valueMap = valueMap

		# get pacman locations
		x = pacman[0]
		y = pacman[1]

		# initialise dictionaries to hold expected utilities
		self.util_dict = {"n_util": 0.0, "s_util": 0.0, "e_util": 0.0, "w_util": 0.0}

		corners = api.corners(state)
		maxWidth = self.getLayoutWidth(corners) - 1
		maxHeight = self.getLayoutHeight(corners) - 1

		# get directions relative to pacman's location
		north = (x, y + 1)
		south = (x, y - 1)
		east = (x + 1, y)
		west = (x - 1, y)
		stay = (x, y)

		# If North is not a wall, then multiply expected utility;
		# else multiply expected utility of staying in place
		# If the perpendicular directions are not walls, then multiply expected utility of those
		# else multiply expected utility of just staying in place

		#230601 jjm/ dangerDirection is ignored
		if self.valueMap[north] != "#" and dangerDirection != 'North':
			n_util = (self.valueMap[north])
		else:
			n_util =Directions.STOP

		self.util_dict["n_util"] = n_util

		if self.valueMap[south] != "#" and dangerDirection != 'South':
			s_util = (self.valueMap[south])
		else:
			s_util = Directions.STOP


		self.util_dict["s_util"] = s_util

		if self.valueMap[east] != "#" and dangerDirection != 'East':
			e_util = (self.valueMap[east])
		else:
			e_util = Directions.STOP

		
		self.util_dict["e_util"] = e_util

		if self.valueMap[west] != "#" and dangerDirection != 'West':
			w_util = (self.valueMap[west])
		else:
			w_util = Directions.STOP


		self.util_dict["w_util"] = w_util


		# get max expected utility
		maxMEU = max(self.util_dict.values())
		# return the move with the highest MEU
		return self.util_dict.keys()[self.util_dict.values().index(maxMEU)]

	#230531 jjm/ A* direction decision
	def getNextStep(self, pacman, next_step, legal):
		next_step = aStar.reverse_coordinates(next_step)
		dx, dy = next_step[0] - pacman[0], next_step[1] - pacman[1]
		if dx != 0 and dy != 0:
			if dx > 0:
				next_step = (pacman[0] + 1, pacman[1])
			else:
				next_step = (pacman[0] - 1, pacman[1])

		print('current location = %s' % (pacman,))
		print('next location = %s' % (next_step,))

		dx, dy = next_step[0] - pacman[0], next_step[1] - pacman[1]
		if dx > 0: 
			next_step_direction = 'East'
		elif dx < 0: 
			next_step_direction = 'West'
		elif dy > 0: 
			next_step_direction = 'North'
		elif dy < 0: 
			next_step_direction = 'South'
		else: 
			next_step_direction = 'Stop'
		
		print('next direction = %s' % (next_step_direction,))
		return api.makeMove(next_step_direction, legal)

	def getDangerDirection(self, pacman, next_step, legal):
		next_step = aStar.reverse_coordinates(next_step)
		dx, dy = next_step[0] - pacman[0], next_step[1] - pacman[1]
		if dx != 0 and dy != 0:
			if dx > 0:
				next_step = (pacman[0] + 1, pacman[1])
			else:
				next_step = (pacman[0] - 1, pacman[1])

		print('current location = %s' % (pacman,))
		print('ghost location = %s' % (next_step,))

		dx, dy = next_step[0] - pacman[0], next_step[1] - pacman[1]
		if dx > 0: next_step_direction = 'East'
		elif dx < 0: next_step_direction = 'West'
		elif dy > 0: next_step_direction = 'North'
		elif dy < 0: next_step_direction = 'South'
		else: next_step_direction = 'Stop'
		
		print('danger direction = %s' % (next_step_direction,))
		return next_step_direction

	def detectLoop(self, pacman):
		self.stateHistory.append(pacman)
		if len(self.stateHistory) < 6:
			return False
		
		if self.stateHistory[-1] == self.stateHistory[-5] or self.stateHistory[-1] == self.stateHistory[-6]:
			return True
		else:
			return False
		
	def getRandomAction(self, legal):
		return random.choice(legal)

	def getAction(self, state):
		print "-" * 30
		legal = api.legalActions(state)
		corners = api.corners(state)
		pacman = api.whereAmI(state)				#230530 jjm/ for a* algorithm
		ghosts = api.ghostStatesWithTimes(state)	#
		capsules = api.capsules(state)				#
		food = api.food(state)						#
		walls = api.walls(state)					#

		maxWidth = self.getLayoutWidth(corners) - 1
		maxHeight = self.getLayoutHeight(corners) - 1

		#230530 jjm/ get map array
		array = [[0] * (maxWidth + 1) for i in range(maxHeight + 1)]
		for wall in walls:
			array[wall[1]][wall[0]] = 1

		#230601 jjm/ detect closeGhost
		closeGhost = False
		normalGhosts = [ghost for ghost in ghosts if ghost[1] <= 1]
		pathToNormalGhost = []
		dangerDirection = None
		for ghost in normalGhosts:
			roundedNormalGhost = (round(ghost[0][0]), round(ghost[0][1]))
			path = aStar.astar(array, pacman, roundedNormalGhost)
			if len(path) < 3:
				closeGhost = True
				print('Close Ghost Detected')
				if path:
					pathToNormalGhost.append((len(path), path))
			if pathToNormalGhost:
				pathToNormalGhost.sort()
				if len(pathToNormalGhost[0][1]) > 1:
					dangerDirection = self.getDangerDirection(pacman, pathToNormalGhost[0][1][1], legal)
				elif len(pathToNormalGhost[0][1]) > 0:
					dangerDirection = self.getDangerDirection(pacman, pathToNormalGhost[0][1][0], legal)

		#230601 jjm/ detect scaredGhost
		scaredGhosts = [ghost for ghost in ghosts if ghost[1] > 1]

		#230601 jjm/ use MDP if closeGhost, or not capsules, not scaredGhosts
		if (not capsules and not scaredGhosts) or closeGhost:
			
			# This function updates all locations at every state
			# for every action retrieved by getAction, thi3s map is recalibrated
			
			valueMap = self.makeValueMap(state)

			# If the map is large enough, calculate buffers around ghosts
			# also use higher number of iteration loops to get a more reasonable policy

			if maxWidth >= 10 and maxHeight >= 10:
				self.valueIteration(state, 0, 0.6, valueMap)
			else:
				self.valueIterationSmall(state, 0.2, 0.7, valueMap)


			#print ("best move: ")
			bestPolicy = self.getPolicy(state, valueMap, dangerDirection)
			print('best move : %s' %bestPolicy)

			# Update values in map with iterations
			for i in range(self.map.getWidth()):
				for j in range(self.map.getHeight()):
					if self.map.getValue(i, j) != "#":
						self.map.setValue(i, j, valueMap[(i, j)])

			#230601 jjm/ disabled
			#self.map.prettyDisplay()

			# If the key of the move with MEU = n_util, return North as the best decision
			# And so on...

			#230601 jjm/ if loop detected, random move
			if self.detectLoop(pacman) and dangerDirection == None:
				print('Loop Detected')
				return api.makeMove(self.getRandomAction(legal), legal)
			else:
				if bestPolicy == "n_util":
					return api.makeMove('North', legal)
				elif bestPolicy == "s_util":
					return api.makeMove('South', legal)
				elif bestPolicy == "e_util":
					return api.makeMove('East', legal)
				elif bestPolicy == "w_util":
					return api.makeMove('West', legal)
				else:
					return api.makeMove('Stop', legal)
		
		#230531 jjm/ if scared ghosts, use A* algorithm to ghosts
		scaredGhosts = [ghost for ghost in ghosts if ghost[1] > 2]
		if scaredGhosts:
			print('Scared Ghost Detected')
			path_to_ghost = []
			for ghost in scaredGhosts:
				rounded_ghost = (round(ghost[0][0]), round(ghost[0][1]))
				path = aStar.astar(array, pacman, rounded_ghost)
				if path:
					path_to_ghost.append((len(path), path))
			if path_to_ghost:
				path_to_ghost.sort()
				if len(path_to_ghost[0][1]) > 0:
					return self.getNextStep(pacman, path_to_ghost[0][1][-1], legal)

		#230530 jjm/ if capsules, use A* algorithm to capsules
		elif capsules:
			print('Capsule Detected')
			path_to_capsule = []
			for capsule in capsules:
				path = aStar.astar(array, pacman, capsule)
				if path:
					path_to_capsule.append((len(path), path))
			if path_to_capsule:
				path_to_capsule.sort()
				if len(path_to_capsule[0][1]) > 0:
					return self.getNextStep(pacman, path_to_capsule[0][1][-1], legal)