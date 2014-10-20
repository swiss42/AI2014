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
        self.previous_action = -1 # start if off with an impossible action so we know it has not been used before
        """
        Our Q-function table. Maps from a tuple of observations (state) to 
        another map of actions to Q-values. To look up a Q-value, call the predict method.
        """
        self.Q = {} # our Q-function table
        self.predictions = [0, 0, 0, 0]
        self.last_prediction = 0
        self.weights = [{},{},{},{}]
        self.last_weights = {}
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
        self.predictions[0] = max_value
        for a in actions[1:]:
            value = self.predict(observations, a)
            self.predictions[a] = value
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
            action = random.choice(actions)
            self.last_prediction = self.predictions[action]
            #self.last_weight = self.weights[action]
            return action
        elif max_action is not None and max_value is not None:
            # we already know the max action
            self.last_prediction = self.predictions[max_action]
            #self.last_weight = self.weights[max_action]
            return max_action
        else:
            # we need to get the max action
            (max_action, max_value) = self.get_max_action(observations)
            self.last_prediction = self.predictions[max_action]
            #self.last_weight = self.weights[max_action]
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
        self.reward = r
        
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
        tile = self.map_state_action_to_tile(observations, action)

        #DEBUGGING
        self.unit_test_our_mapping(observations)
        self.print_debug_info(observations)

        # lookup tile value in tile_values and return
        prediction = -sys.maxint - 2
        if self.in_grid(tile):
            prediction = self.get_value_of_tile(tile)
        return prediction

    def update(self, observations, action, new_value):
        """
        Changes the tile values
        """

        # get tile row and column that action will place you in from given state
        tile = self.map_state_action_to_tile(observations, action)
        assert (self.in_grid(tile))

        # update with new value
        self.set_value_of_tile(tile, new_value)

        # draw q-value markers
        # o = tuple([x for x in observations])
        # self.draw_q(o)

    def get_possible_actions(self, observations):
        """
        Get the possible actions that can be taken given the state (observations)
        """
        aMin = self.action_info.min(0)
        aMax = self.action_info.max(0)
        all_actions = range(int(aMin), int(aMax+1))

        # loop over action and don't include actions that crash you into wass
        # or put you out of bounds
        actions = []
        for a in all_actions:

            # figure out which tile action puts you in
            x = observations[0]
            y = observations[1]
            cur_tile = get_environment().maze.xy2rc(x, y)
            next_tile = self.map_state_action_to_tile(observations, a)

            # check if action puts agent out of bounds
            if self.in_grid(next_tile):

                # check if there is a wall between
                if (not ((cur_tile, next_tile) in get_environment().maze.walls)):
                    actions.append(a)

        print "Possible actions: ", actions

        return actions

    def map_state_action_to_tile(self, observations, action):

        # get current micro-state(values between 0 and 63) from observations
        (micro_row, micro_col) = micro_state = self.micro_state_converter(observations)

        # map current state to destination state given action
        new_micro_state = self.apply_action_to_micro_state (micro_state, action)

        # figure out which tile the destination state is in
        (tile_row, tile_col) = self.micro_to_tile_coordinates(new_micro_state)

        #macro-state row and col
        return (tile_row, tile_col)

    def print_debug_info(self, observations):

        mx = observations[0]
        my = observations[1]
        micro_state = self.micro_state_converter(observations)
        print "START"
        self.print_tile_values()
        print "Micro-stateobservations:"
        for x in observations:
            print "Ob: ", x
        print "Current Micro Row: ", micro_state[0], "Current Micro Col: ", micro_state[1]
        print "Current Micro X: ", mx, "Current Micro Y: ", my

    def unit_test_our_mapping(self, observations):
        #TEST our mapping
        if self.previous_action != -1:
            mx = observations[0]
            my = observations[1]
            micro_state = self.micro_state_converter(observations)
            (r, c) = self.micro_to_tile_coordinates(micro_state)
            (ar,ac) = get_environment().maze.xy2rc(mx, my)
            print "######### TEST ##########"
            print "r: ", r, ", c: ", c
            print "ar: ", ar, ", ac: ", ac
            print "######### END ##########"
            assert (ar == r)
            assert (ac == c)

    def print_tile_values(self):
        s = ""
        for r in reversed(range(8)):
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
        STEP_OFFSET = 1
        if action == 0: # move up
            #if micro_row < 62:
                micro_row += STEP_OFFSET
        elif action == 1: # move down
            #if micro_row > 0:
                micro_row -= STEP_OFFSET
        elif action == 2: # move right
            #if micro_col < 62:
                micro_col += STEP_OFFSET
        elif action == 3: # move left
            #if micro_col > 0:
                micro_col -= STEP_OFFSET

        # return resultant micro state
        return (micro_row, micro_col)

    #converts the (x, y) coordinates to (micro_r, micro_c) coordinates
    def micro_state_converter(self, observations):
        micro_x = observations[0]
        micro_y = observations[1]
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
        tile_row = int(((micro_row + 1) / 8))
        tile_col = int(((micro_col + 1) / 8))
        return (tile_row, tile_col)

    #Simply check if the tile coordinates are out of bounds
    def in_grid(self, tile):
        (r, c) = tile
        if (r < 0) or (r > 7) or (c < 0) or (c > 7):
            return False
        return True

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
        MyTilingRLAgent.__init__(self, gamma, alpha, epsilon) # initialize the superclass

    def predict(self, observations, action):
        
        # convert observations to a micro state row and column
        micro_state = self.micro_state_converter(observations)

        # predict the utility of the reulstant state after taking the given action
        return self.calculate_micro_state_value(micro_state, action)

    def update(self, observations, action, new_value):

        last_micro_state = self.micro_state_converter(observations)
        cur_micro_state = self.apply_action_to_micro_state(last_micro_state, action)

        # update closest tiles
        for tile in self.last_closest_tiles:
            self.update_tile_value(observations, cur_micro_state, tile)

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
        weight = 1 - (distances[tile] / distances_sum) # BUG HERE
        return weight

    def calculate_micro_state_value(self, micro_state, action):

        # given micro state and action get resulting micro state
        new_micro_state = self.apply_action_to_micro_state (micro_state, action)

        # get closest tiles
        # remember that this returns a dictionary of tiles (closest to micro state) and distances from the given micro state
        closest_tiles = self.get_closest_tiles(new_micro_state)
        self.last_closest_tiles = closest_tiles

        # calculate tile
        value = 0;
        for tile in closest_tiles:
            weight = self.calculate_weight(tile, closest_tiles)
            value += self.get_value_of_tile(tile) * weight
            self.weights[action][tile] = weight
        return value

    #this method should tell us which 2 or 3 tiles are the closest to us
    def get_closest_tiles(self, cur_micro_state):

        # get current tile row and column from current micro state
        (cur_r, cur_c) = self.micro_to_tile_coordinates(cur_micro_state)

        # create dictionary for closest tiles with their distances
        closest_tiles = {}
        temp = []
        closest_tiles[(cur_r, cur_c)] = d = self.calculate_distance((cur_r, cur_c), cur_micro_state)
        temp.append((cur_r, cur_c, d))

        # get short list of clostest tiles
        candidate_tiles = self.inbounds_and_not_blocked((cur_r, cur_c))

        # calculate distances of tiles in candidate list
        for (r,c) in candidate_tiles:
            dist = self.calculate_distance((r, c), cur_micro_state)
            temp.append((r,c,dist))

        # get clostest tiles from candiate list
        if len(temp) == 1:
            (r,c,d) = temp.index(0)
            closest_tiles[(r, c)] = d
            print "### Closest Tiles1", closest_tiles
            return closest_tiles

        # sort list by distances and pop the two items with shortest distance, add them to clostest tiles.
        temp.sort(key = lambda tup: tup[2])
        (r, c, d) = temp.pop()
        closest_tiles[(r, c)] = d 
        (r, c, d) = temp.pop()
        closest_tiles[(r, c)] = d

        print "### Closest Tiles2", closest_tiles

        return closest_tiles

    #return a list of tiles that we can actually calculate a shortest path to
    def inbounds_and_not_blocked(self, tile):
        (x, y) = tile
        candidates = []

        # get walls
        walls = get_environment().maze.walls

        # test diagonals
        if self.in_grid((x + 1, y + 1)):
            if (not(((x+1, y+1), (x, y+1)) in walls) and 
                not(((x, y+1), (x, y)) in walls) or
                not(((x+1, y+1), (x+1, y)) in walls) and
                not(((x + 1, y), (x, y)) in walls)):
                    candidates.append((x+1, y+1))
        if self.in_grid((x - 1, y + 1)):
            if (not(((x-1, y+1), (x, y+1)) in walls) and
                not(((x, y+1), (x, y)) in walls) or 
                not(((x-1, y+1), (x-1, y)) in walls) and
                not(((x - 1, y), (x, y)) in walls)):
                    candidates.append((x-1, y+1))
        if self.in_grid((x - 1, y - 1)):
            if (not(((x-1, y-1), (x, y-1)) in walls) and
                not(((x, y-1), (x, y)) in walls) or 
                not(((x-1, y-1), (x-1, y)) in walls) and
                not(((x-1, y), (x, y)) in walls)):
                    candidates.append((x-1, y-1))
        if self.in_grid((x + 1, y - 1)):
            if (not(((x+1, y-1), (x, y-1)) in walls) and
                not(((x, y-1), (x, y)) in walls) or 
                not(((x+1, y-1), (x+1, y)) in walls) and
                not(((x + 1, y), (x, y)) in walls)):
                    candidates.append((x+1, y-1))

        # test others
        if self.in_grid((x, y+1)):
            if not(((x, y+1), (x, y)) in walls):
                candidates.append((x, y+1))

        if self.in_grid((x, y-1)):
            if not(((x, y-1), (x, y)) in walls):
                candidates.append((x, y-1))

        if self.in_grid((x+1, y)):
            if not(((x+1, y), (x, y)) in walls):
                candidates.append((x+1, y))

        if self.in_grid((x-1, y)):
            if not(((x-1, y), (x, y)) in walls):
                candidates.append((x-1, y))

        return candidates

    def update_tile_value(self, observations, cur_micro_state, tile):

        # get list of possible action
        # possible_actions = self.get_possible_actions(observations)

        # # calculate action values
        # action_values = []
        # for a in possible_actions:
        #     action_values.append(self.calculate_micro_state_value(cur_micro_state, a))

        # # get needed other values
        # if len(self.last_weights) > 0:
        #     tile_weight = self.last_weights[tile]
        # else:
        #     tile_weight = 0
        # tile_value = self.get_value_of_tile(tile)
        # reward = self.reward
        # alpha = self.alpha 
        # gamma = self.gamma

        # # calculate new update value
        # new_value = tile_value + alpha * tile_weight * (reward + gamma * max(action_values) - self.last_prediction)
        new_value = 0 
        self.set_value_of_tile(tile, new_value)








