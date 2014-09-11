from OpenNero import *
from common import *

import Maze
from Maze.constants import *
import Maze.agent
from Maze.agent import *

class IdaStarSearchAgent(SearchAgent):
    """
    IDA* algorithm
    """
    def __init__(self):
        # this line is crucial, otherwise the class is not recognized as an AgentBrainPtr by C++
        SearchAgent.__init__(self)
        self.open = []
        slef.visited = []
        self.backpointers = {}

        self.adjlist = {}

    def reset(self):
        """
        Reset the agent
        """
        self.open = []
        slef.visited = []
        self.backpointers = {}

        self.adjlist = {}

    def initialize(self, init_info):
        """
        Initializes the agent upon reset
        """
        self.action_info = init_info.actions
        self.constraints = init_info.actions
        return True

    def start(self, time, observations):
        """
        Called on the first move
        """
        return self.idaStar(observations)
    
    def act(self, time, observations, reward):
        """
        Called every time the agent needs to take an action
        """
        return self.idaStar(observations)

    def end(self, time, reward):
        """
        at the end of an episode, the environment tells us the final reward
        """
        print  "Final reward: %f, cumulative: %f" % (reward[0], self.fitness[0])
        self.reset()
        return True

    def destroy(self):
        """
        After one or more episodes, this agent can be disposed of
        """
        return True

    def mark_path(self, r, c):
        get_environment().mark_maze_white(r,c)

    def idaStar(self, observations):
        """Depth first search will be implemented first"""
        r = observations[0]
        c = observations[1]
        
        if (r, c) not in self.visted:
            # expand
            children = []
            for m, (rd, cd) in enumerate(MAZE_MOVES):
                
                # calculate next move
                r2 = r + rd
                c2 = c + cd

                # check if we can go this way
                if not observations[2 + m] and (r2, c2) not in self.visted:
                    children.append[(r2, c2)]
                    self.adjlist[(r, c)] = children

        # if we have been here check if there are other children we have not visted
        



        # remember how to get back
        if (r + rd, c + cd) not in self.backpointers:
            self.backpointers[(r + rd, c + cd)] = (r, c)
        return v






        

