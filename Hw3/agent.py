from OpenNero import *
from common import *
import random

import Maze
from Maze.constants import *
import Maze.agent
from Maze.agent import *

class MyTabularRLAgent(AgentBrain):
    """
    Tabular RL Agent
    """
    def __init__(self, gamma, alpha, epsilon):
        """
        Constructor that is called from the robot XML file.
        Parameters:
        @param gamma reward discount factor (between 0 and 1)
        @param alpha learning rate (between 0 and 1)
        @param epsilon parameter for the epsilon-greedy policy (between 0 and 1)
        """
        AgentBrain.__init__(self) # initialize the superclass
        self.gamma = gamma
        self.alpha = alpha
        self.epsilon = epsilon
        """
        Our Q-function table. Maps from a tuple of observations (state) to 
        another map of actions to Q-values. To look up a Q-value, call the predict method.
        """
        self.Q = {} # our Q-function table
        print 
    
    def __str__(self):
        return self.__class__.__name__ + \
            ' with gamma: %g, alpha: %g, epsilon: %g' \
            % (gamma, alpha, epsilon)
    
    def initialize(self, init_info):
        """
        Create a new agent using the init_info sent by the environment
        """
        self.action_info = init_info.actions
        self.sensor_info = init_info.sensors
        return True
    
    def predict(self, observations, action):
        """
        Look up the Q-value for the given state (observations), action pair.
        """
        o = tuple([x for x in observations])
        if o not in self.Q:
            return 0
        else:
            return self.Q[o][action]
    
    def update(self, observations, action, new_value):
        """
        Update the Q-function table with the new value for the (state, action) pair
        and update the blocks drawing.
        """
        o = tuple([x for x in observations])
        actions = self.get_possible_actions(observations)
        if o not in self.Q:
            self.Q[o] = [0 for a in actions]
        self.Q[o][action] = new_value
        self.draw_q(o)
    
    def draw_q(self, o):
        e = get_environment()
        if hasattr(e, 'draw_q'):
            e.draw_q(o, self.Q)

    def get_possible_actions(self, observations):
        """
        Get the possible actions that can be taken given the state (observations)
        """
        aMin = self.action_info.min(0)
        aMax = self.action_info.max(0)
        actions = range(int(aMin), int(aMax+1))
        return actions
        
    def get_max_action(self, observations):
        """
        get the action that is currently estimated to produce the highest Q
        """
        actions = self.get_possible_actions(observations)
        max_action = actions[0]
        max_value = self.predict(observations, max_action)
        for a in actions[1:]:
            value = self.predict(observations, a)
            if value > max_value:
                max_value = value
                max_action = a
        return (max_action, max_value)

    def get_epsilon_greedy(self, observations, max_action = None, max_value = None):
        """
        get the epsilon-greedy action
        """
        actions = self.get_possible_actions(observations)
        if random.random() < self.epsilon: # epsilon of the time, act randomly
            return random.choice(actions)
        elif max_action is not None and max_value is not None:
            # we already know the max action
            return max_action
        else:
            # we need to get the max action
            (max_action, max_value) = self.get_max_action(observations)
            return max_action
    
    def start(self, time, observations):
        """
        Called to figure out the first action given the first observations
        @param time current time
        @param observations a DoubleVector of observations for the agent (use len() and [])
        """
        self.previous_observations = observations
        self.previous_action = self.get_epsilon_greedy(observations)
        return self.previous_action

    def act(self, time, observations, reward):
        """
        return an action given the reward for the previous action and the new observations
        @param time current time
        @param observations a DoubleVector of observations for the agent (use len() and [])
        @param the reward for the agent
        """

        # get the reward from the previous action
        r = reward[0]
        
        # get the updated epsilon, in case the slider was changed by the user
        self.epsilon = get_environment().epsilon
        
        # get the old Q value
        Q_old = self.predict(self.previous_observations, self.previous_action)

        print "Current tile value: ", Q_old
        
        # get the max expected value for our possible actions
        (max_action, max_value) = self.get_max_action(observations)
        
        # update the Q value
        self.update( \
            self.previous_observations, \
            self.previous_action, \
            Q_old + self.alpha * (r + self.gamma * max_value - Q_old) )
        
        # select the action to take
        action = self.get_epsilon_greedy(observations, max_action, max_value)
        self.previous_observations = observations
        self.previous_action = action
        return action

    def end(self, time, reward):
        """
        receive the reward for the last observation
        """
        # get the reward from the last action
        r = reward[0]
        o = self.previous_observations
        a = self.previous_action

        # get the updated epsilon, in case the slider was changed by the user
        self.epsilon = get_environment().epsilon

        # Update the Q value
        Q_old = self.predict(o, a)
        q = self.update(o, a, Q_old + self.alpha * (r - Q_old) )
        return True

class MyTilingRLAgent(MyTabularRLAgent):
    """
    Tiling RL Agent
    """
    def __init__(self, gamma, alpha, epsilon):
        """
        Constructor that is called from the robot XML file.
        Parameters:
        @param gamma reward discount factor (between 0 and 1)
        @param alpha learning rate (between 0 and 1)
        @param epsilon parameter for the epsilon-greedy policy (between 0 and 1)
        """
        self.tile_values = [[0 for x in range(8)] for x in range(8)]  # initialize list of 64 tiles to all zeros
        MyTabularRLAgent.__init__(self, gamma, alpha, epsilon) # initialize the superclass

    def draw_q(self, o):
        e = get_environment()
        if hasattr(e, 'draw_q'):
            e.draw_q(0, self.tile_values)

    def predict(self, observations, action):
        """
        Look up the Q-value for the given state (observations), action pair.
        For the tiling approximator this means figuring out which tile the dest state is in
        and returning that tiles value from the tile_values list.
        """
        # get tile row and column that action will place you in from given state
        (tile_row, tile_col) = self.map_state_action_to_tile(observations, action)

        # lookup tile value in tile_values and return
        return self.tile_values[tile_row][tile_col]

    def update(self, observations, action, new_value):
        """
        Changes the tile values
        """

        # get tile row and column that action will place you in from given state
        (tile_row, tile_col) = self.map_state_action_to_tile(observations, action)

        # update with new value
        self.tile_values[tile_row][tile_col] = new_value

        # draw q-value markers
        # o = tuple([x for x in observations])
        # self.draw_q(o)

    def map_state_action_to_tile(self, observations, action):

        # get current micro-state(values between 0 and 63) from observations
        (micro_row, micro_col) = micro_state = self.micro_state_converter(observations)

        # print debug info
        mx = observations[0]
        my = observations[1]
        print "START"
        self.print_tile_values()
        print "Micro-stateobservations:"
        for x in observations:
            print "Ob: ", x
        print "Current Micro Row: ", micro_row, "Current Micro Col: ", micro_col
        print "Current Micro X: ", mx, "Current Micro Y: ", my

        # map current state to destination state given action
        new_micro_state = self.apply_action_to_micro_state (micro_state, action)

        # figure out which tile the destination state is in
        (tile_row, tile_col) = self.micro_to_tile_coordinates(new_micro_state)

        # print more debug info
        print "Future Tile Row: ", tile_row, "Future Tile Col: ", tile_col
        (r,c) = self.micro_to_tile_coordinates(micro_state)
        print "Cur Tile Row: ", r, "Cur Tile Col: ", c
        (ar,ac) = get_environment().maze.xy2rc(mx, my)
        print "Actual Cur Tile Row: ", ar, "Actual Cur Tile Col: ", ac
        print "END"

        #TEST our mapping
        assert (ar == r)
        assert (ac == c)

        #macro-state row and col
        return (tile_row, tile_col)

    def print_tile_values(self):
        for r in range(8):
            print self.tile_values[r]

    def get_value_of_tile(self, tile):
        (tile_row, tile_col) = tile
        return self.tile_values[tile_row][tile_col]


    def set_value_of_tile(self, tile, new_value):
        (tile_row, tile_col) = tile
        self.tile_values[tile_row][tile_col] = new_value


    def apply_action_to_micro_state(self, micro_state, action):

        # break into row and column
        (micro_row, micro_col) = micro_state

        # map current state to destination state given action
        if action == 0: # move up
            if micro_row < 61:
                micro_row += 1
        elif action == 1: # move down
            if micro_row > 0:
                micro_row -= 1
        elif action == 2: # move right
            if micro_col < 61:
                micro_col += 1
        elif action == 3: # move left
            if micro_col > 0:
                micro_col -= 1

        # return resultant micro state
        return (micro_row, micro_col)

    #converts the (x, y) coordinates to (micro_r, micro_c) coordinates
    def micro_state_converter(self, state):
        micro_x = state[0]
        micro_y = state[1]
        micro_row = ((micro_x - 12.5) / (2.5))
        micro_col = ((micro_y - 12.5) / (2.5))
        return (micro_row, micro_col)

    #returns center point of tile in terms of micro-states(values 0 to 63)
    def tile_center_point(self, tile):
        tile_row = tile[0]
        tile_col = tile[1]
        return ((tile_row * 8) + 3.5, (tile_col * 8) + 3.5)
    
    #determine which tile the micro_state is in
    def micro_to_tile_coordinates(self, micro_state):
        micro_row = micro_state[0]
        micro_col = micro_state[1]
        tile_row = int((micro_row + 1) / 8)
        tile_col = int((micro_col + 1) / 8)
        return (tile_row, tile_col)

class MyNearestNeighborsRLAgent(MyTilingRLAgent):
    """
    Nearest Neighbors RL Agent
    """
    def __init__(self, gamma, alpha, epsilon):
        """
        Constructor that is called from the robot XML file.
        Parameters:
        @param gamma reward discount factor (between 0 and 1)
        @param alpha learning rate (between 0 and 1)
        @param epsilon parameter for the epsilon-greedy policy (between 0 and 1)
        """
        MyTabularRLAgent.__init__(self, gamma, alpha, epsilon) # initialize the superclass

    def predict(self, observations, action):
        
        # convert observations to a micro state row and column
        micro_state = self.micro_state_converter(observations)

        # predict the utility of the reulstant state after taking the given action
        return self.calculate_micro_state_value(micro_state, action)

    def update(self, observations, action, new_value):
        pass

    def calculate_distance(self, tile, cur_micro_state):

        # get center point of tile in terms of micro-states
        (tile_x, tile_y) = self.tile_center_point(tile)

        # micro-state position
        (micro_x, micro_y) = cur_micro_state

        # return distance
        return (((tile_x - micro_x) ** 2) + ((tile_y - micro_y) ** 2)) ** 0.5

    def calculate_weight(self, tile, distances):
        
        # distances is a map of 2 or 3 distances (mapped to tiles)
        # get sum of distances
        distances_sum = 0;
        for tiles in distances:
            distances_sum += distances[tiles]

        # calulate wieght and return
        return 1 - (distances[tile] / distances_sum)

    def calculate_micro_state_value(self, micro_state, action):

        # given micro state and action get resulting micro state
        new_micro_state = self.apply_action_to_micro_state (micro_state, action)

        # get closest tiles
        # remember that this returns a dictionary of tiles (closest to micro state) and distances from the given micro state
        closest_tiles = self.get_closest_tiles(new_micro_state)

        # calculate tile
        value = 0;
        for tile in closest_tiles:
            value += self.get_value_of_tile(tile) * self.calculate_weight(tile, closest_tiles)
        return value

    #this method should tell us which 2 or 3 tiles are the closest to us
    def get_closest_tiles(self, cur_micro_state):

        # get current tile row and column from current micro state
        (cur_r, cur_c) = self.micro_to_tile_coordinates(cur_micro_state)

        # create dictionary for closest tiles with their distances
        closest_tiles[(cur_r, cur_c)] = self.calculate_distance((cur_r, cur_c), cur_micro_state)

        # get short list of clostest tiles
        candidate_tiles = self.inbounds_and_not_blocked((cur_r, cur_c))
        temp = []

        # calculate distances of tiles in candidate list
        for (r,c) in candidate_tiles:
            dist = self.calculate_distance((r, c), cur_micro_state)
            temp.append((r,c,dist))

        # get clostest tiles from candiate list
        if len(temp == 1):
            (r,c,d) = temp.index(0)
            closest_tiles[(r, c)] = d
            return closest_tiles

        # sort list by distances and pop the two items with shortest distance, add them to clostest tiles.
        temp.sort(key = lambda tup: tup[2])
        (r, c, d) = temp.pop()
        closest_tiles[(r, c)] = d 
        (r, c, d) = temp.pop()
        closest_tiles[(r, c)] = d
        return closest_tiles

    #return a list of tiles that we can actually calculate a shortest path to
    def inbounds_and_not_blocked(self, tile):
        (x, y) = tile
        candidates = []

        # get walls
        walls = get_environment().maze.walls

        # test diagonals
        if in_grid(x+1, y+1):
            if (not(((x+1, y+1), (x, y+1)) in walls) and 
                not(((x, y+1), (x, y)) in walls) or
                not(((x+1, y+1), (x+1, y)) in walls) and
                not(((x + 1, y), (x, y)) in walls)):
                    candidates.append((x+1, y+1))
        if in_grid(x - 1, y + 1):
            if (not(((x-1, y+1), (x, y+1)) in walls) and
                not(((x, y+1), (x, y)) in walls) or 
                not(((x-1, y+1), (x-1, y)) in walls) and
                not(((x - 1, y), (x, y)) in walls)):
                    candidates.append((x-1, y+1))
        if in_grid(x - 1, y - 1):
            if (not(((x-1, y-1), (x, y-1)) in walls) and
                not(((x, y-1), (x, y)) in walls) or 
                not(((x-1, y-1), (x-1, y)) in walls) and
                not(((x-1, y), (x, y)) in walls)):
                    candidates.append((x-1, y-1))
        if in_grid(x + 1, y - 1):
            if (not(((x+1, y-1), (x, y-1)) in walls) and
                not(((x, y-1), (x, y)) in walls) or 
                not(((x+1, y-1), (x+1, y)) in walls) and
                not(((x + 1, y), (x, y)) in walls)):
                    candidates.append((x+1, y-1))

        # test others
        if in_grid(x, y+1):
            if not((x, y+1), (x, y) in walls):
                candidates.append(x, y+1)

        if in_grid(x, y-1):
            if not((x, y-1), (x, y) in walls):
                candidates.append(x, y-1)

        if in_grid(x+1, y):
            if not((x+1, y), (x, y) in walls):
                candidates.append(x+1, y)

        if in_grid(x-1, y):
            if not((x-1, y), (x, y) in walls):
                candidates.append(x-1, y)

        return candidates

    #Simply check if the tile coordinates are out of bounds
    def in_grid(self, tile):
        (r, c) = tile
        if (r < 0) or (r > 7) or (c < 0) or (c > 7):
            return False
        return True

    def update_tile_value(self, tile, value):
        pass








