# ==============================CS-199==================================
# FILE:			MyAI.py
#
# AUTHOR: 		Justin Chung
#
# DESCRIPTION:	This file contains the MyAI class. You will implement your
#				agent in this file. You will write the 'getAction' function,
#				the constructor, and any additional helper functions.
#
# NOTES: 		- MyAI inherits from the abstract AI class in AI.py.
#
#				- DO NOT MAKE CHANGES TO THIS FILE.
# ==============================CS-199==================================

from AI import AI
from Action import Action


class MyAI( AI ):

	def __init__(self, rowDimension, colDimension, totalMines, startX, startY):

		########################################################################
		#							YOUR CODE BEGINS						   #
		########################################################################
		
		self.__cols = colDimension
		self.__rows = rowDimension

		# FIRST DIGIT: 
			# * = unmarked / not visited yet
			# M = flagged 
			# number = label

		# SECOND DIGIT: Number of still-covered mines
			# 0 means we have already flagged all of its mines
			# FIRST==SECOND have not flagged any of its mines
			
		# THIRD DIGIT: Number of neighbors that are COVERED and NOT flagged
			# 0 means all neighbors are uncovered/flagged

		self.__board = [[['*',0,0] for _ in range(colDimension)] for _ in range(rowDimension)]
		self.__totalMines = totalMines
		self.__uncoveredFrontier = set()
		self.__coveredFrontier = set()
		self.__prevRow, self.__prevCol = self.__toRowCol(startX, startY) 
		self.__moveCount = 1
		self.__actionQueue = set() # contains tiles guaranteed mines or guaranteed safe (x, y, z) x, y = index, z = -1 : mine, 1: safe
		self.__backtrackStack = []

	#assuming the very first call to getAction is the move AFTER the starting tile
	def getAction(self, number: int) -> "Action Object":
		########################################################################
		#							YOUR CODE BEGINS						   #
		########################################################################
		if self.__moveCount == ((self.__cols*self.__rows)-self.__totalMines):  #or (len(self.__coveredFrontier) <= self.__totalMines):
			return Action(AI.Action.LEAVE)
		else:
			self.__updateAfterLabel(number)
			self.__updateBoard(number)
			# print("Action List: ", self.__actionQueue)

			if self.__actionQueue:
				# print('Performing from Action List')
				action_x, action_y = self.__actionQueue.pop() #potentially add error checking
				# print("Action X, Y:", action_x, action_y)
			else:
				C,V = self.__preprocessBacktrack()
				self.__backtrack(C,V)
				#TO BE IMPLEMENTED
				# print('Performing Random Action')
				# action_x, action_y = self.__coveredFrontier.pop()

			# self.__uncoveredFrontier.remove((action_x,action_y))
			
			# print("LENGTH OF UNCOVERED ",len(self.__uncoveredFrontier))
			# print("UNCOVERED FRONTIER:", self.__uncoveredFrontier)
			# print("LENGTH OF COVERED ",len(self.__coveredFrontier))
			# print("COVERED FRONTIER:",self.__coveredFrontier)
			self.__prevRow = action_x
			self.__prevCol = action_y
			self.__moveCount += 1
			
			return Action(AI.Action.UNCOVER, *self.__toCartesian(self.__prevRow, self.__prevCol))


	def __buildFrontiers(self):
		pass


	def __preprocessBacktrack(self): 
		# v = covered tiles
		# c = uncovered tiles (aka exposed labels)
		C = {} # KEY = tile coordinate, VALUE = set of neighbors in the uncovered frontier
		for x,y in self.__coveredFrontier:
			neighbors = self.__getNeighbors(x,y)
			uncovNeighbors = set()
			for n in neighbors:
				if n in self.__uncoveredFrontier:
					uncovNeighbors.add(n)
			C[(x,y)] = uncovNeighbors

		V = {}
		for x, y in self.__uncoveredFrontier:
			neighbors = self.__getNeighbors(x,y)
			covNeighbors = set()
			for n in neighbors:
				if n in self.__coveredFrontier:
					covNeighbors.add(n)
			V[(x,y)] = covNeighbors
		# MUST IMPLEMENT POTENTIAL SEPARATE FRONTIERS...
		return C, V
	
	def __backtrack(self, C, V):
		# cv, vc = self.__preprocessBacktrack() this should actually be computed on each frontier and then called in get action i think
		

		# frontier v1, v2, v3, v4
		# V = [v1, v2, v3, v4, ...]
		def __recursive_backtrack(varset, index):
			var = V[index] # this gives you the node
			for assignment in [0, 1]:
				varset[var] = assignment
				if self.__checkVarConstraint(var, varset):
					self.__recursive_backtrack(varset, index + 1)
				varset[var] = None # backtrack if no assignemnts left
		
		varset = {var: None for var in V} # V is the covered frontier

		return
		
	
	
	# 1) When flagging a tile, check the neighbors of each of its neighbors to ensure that
#    decrementing the second digit doesn'tlead to negative values 
#    negative value means that there can't possibly be a mine there, must backtrack and reconfigure

	def __checkVarConstraint(self, var, varset, C, V) -> bool:
		for uncoveredNeighbor in C[var]: # go through each constraint
			unassignedNeighbors = 0
			mineCount = 0
			for coveredNeighbor in V[uncoveredNeighbor]:
				if varset[coveredNeighbor] is None:
					unassignedNeighbors += 1
				elif varset[coveredNeighbor] == 1:
					mineCount += 1
			
			result = (mineCount <= self.__getEffectiveLabel(unassignedNeighbor)) && (self.__getEffectiveLabel(unassignedNeighbor) <= mineCount += unassignedNeighbors)
			return False if not result

	def __getEffectiveLabel(self, var):
		return self.__board[var[0]][var[1]][1]

	
	def __updateAfterFlag(self, x, y):
		# Updates the neighbors of a flagged tile
		self.__board[x][y][0] = 'M'
		self.__coveredFrontier.remove((x, y))
		thirdCount = 0
		neighbors = self.__getNeighbors(x,y)
		for nx, ny in neighbors:
			if self.__board[nx][ny][0] != '*' and self.__board[nx][ny][0] != 'M': 
				# decrement uncovered neighbor's 2nd digit (still-covered mines)
				self.__board[nx][ny][1] -= 1
				# decrement uncovered neighbor's 3rd digit (unflagged neighbors)
				self.__board[nx][ny][2] -= 1
			elif self.__board[nx][ny][0] == '*':
				# increment number of flag's neighbors that are COVERED and NOT flagged
				thirdCount += 1
		self.__board[x][y][2] = thirdCount


	def __getNeighbors(self, x, y):
		returnSet = set()
		checkX = x-1
		checkY = y-1
		for i in range(3):
			i += checkX
			for j in range(3):
				j += checkY
				if (i == x and j == y) or self.__outOfBounds(i,j):
					pass
				else:
					returnSet.add((i, j))
		return returnSet


	def __getRandomAction(self):
		pass


	def __getGuaranteedActions(self):
		for x, y in self.__uncoveredFrontier:
			# if x == 1 and y == 3:
				# print("We at (1,3): ", self.__board[x][y])
			if self.__board[x][y][1] == self.__board[x][y][2]: # first rule, EffectiveLabel = numOfUnmarkedNeighbors, set all covered neighbors to a mine
				neighbors = self.__getNeighbors(x, y)
				for nx, ny in neighbors:
					# if (nx, ny) in self.__coveredFrontier:
					if self.__board[nx][ny][0] == '*':
						self.__updateAfterFlag(nx, ny)
			elif self.__board[x][y][1] == 0: # second rule, Effectivelabel = 0, add all actions to the GuaranteedActionsList because they are all safe to be uncovered
				neighbors = self.__getNeighbors(x, y)
				for nx, ny in neighbors:
					# if (nx, ny) in self.__coveredFrontier:
					if self.__board[nx][ny][0] == '*':
						self.__actionQueue.add((nx, ny)) # safe to be uncovered		


	def __updateAfterLabel(self, label):
		# Updates the neighbors of a labelled tile
		self.__board[self.__prevRow][self.__prevCol][0] = label
		numFlags = 0
		thirdCount = 0
		neighbors = self.__getNeighbors(self.__prevRow, self.__prevCol)
		for nx, ny in neighbors:
			if self.__board[nx][ny][0] == 'M':
				numFlags += 1
			elif self.__board[nx][ny][0] == '*':
				thirdCount += 1
			# Decrement each uncovered neighbor's THIRD digit
			if self.__board[nx][ny][0] != '*':
				self.__board[nx][ny][2] -= 1
				
		self.__board[self.__prevRow][self.__prevCol][1] = label-numFlags
		self.__board[self.__prevRow][self.__prevCol][2] = thirdCount
	

	def __updateBoard(self, label: int)  -> None:
		# Updates the label correctly, repopulating the respective frontiers

		# Empties the frontiers before updating board
		self.__coveredFrontier = set()
		self.__uncoveredFrontier = set()

		for x in range(self.__rows):
			for y in range(self.__cols):
				if self.__board[x][y][0] == '*':
					self.__addUncoveredFrontier(x,y)
				elif self.__board[x][y][0] != 'M':
					self.__addCoveredFrontier(x, y)
		# print("After update board:",self.__uncoveredFrontier)
		# print("After update board:",self.__coveredFrontier)
		self.__getGuaranteedActions()
					# this is adding to the frontier, but we also need to adjust for the numbers


	def __toRowCol(self, x: int, y: int) -> (int, int):
		# Converts x,y coordinates to row,col 
		return (4 - y , x)


	def __toCartesian(self, row: int, col: int) -> (int, int):
		# Converts row,col to x,y coordinates
		return (col, 4 - row)
			

	def __addUncoveredFrontier(self, x, y) -> None:
		# Adds all of (x,y)'s uncovered neighbors (no * or M) to uncoveredFrontier
		checkX = x-1
		checkY = y-1
		for i in range(3):
			i += checkX
			for j in range(3):
				j += checkY
				if (i == x and j == y) or self.__outOfBounds(i,j) :
					pass
				else:
					if self.__board[i][j][0] != 'M' and self.__board[i][j][0] != '*':
		 				self.__uncoveredFrontier.add((i, j))
		   

	def __addCoveredFrontier(self, x, y) -> None:
		# Adds all of (x,y)'s covered neighbors (symbolized with *) to coveredFrontier
		checkX = x-1
		checkY = y-1
		for i in range(3):
			i += checkX
			for j in range(3):
				j += checkY
				if (i == x and j == y) or self.__outOfBounds(i,j) :
					pass
				else:
					if self.__board[i][j][0] == '*':
		 				self.__coveredFrontier.add((i, j))
		
				
	def __outOfBounds(self, x, y) -> None:
		# Returns true if x or y is out of bounds; false otherwise
		if x < 0 or y >= self.__cols or y < 0 or x >= self.__rows:
			return True
		return False

# Set of constraints
# 1) When flagging a tile, check the neighbors of each of its neighbors to ensure that
#    decrementing the second digit doesn't lead to negative values 
#    negative value means that there can't possibly be a mine there, must backtrack and reconfigure

# 2) 




# General Outline:
# 1) Use equivalence classes to separate the frontier
# 2) In each frontier, order the variables (titles) according to some heuristic
# 3) Perform backtracking on each frontier, getting all possible solutions
# 4) For tiles that are consistently mines, you can flag them
# 5) For tiles that are consistently safe, you can uncover them
# 6) Otherwise, assign them a probability of them being a mine = # of times they were mines / # total number of solutions