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

    def reset(self):
        """
        Reset the agent
        """
        pass

    def initialize(self, init_info):
        """
        Initializes the agent upon reset
        """
        self.action_info = init_info.actions
        return True

    def start(self, time, observations):
        """
        Called on the first move
        """
        return self.action_info.random()
    
    def act(self, time, observations, reward):
        """
        Called every time the agent needs to take an action
        """
        return self.action_info.random()

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

