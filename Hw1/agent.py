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
        self.reset()

    def reset(self):
        """
        Reset the agent
        """
        self.open = []
        self.visited = []
        self.backpointers = {}
        self.parents = {}
        self.children = {}

    def initialize(self, init_info):
        """
        Initializes the agent upon reset
        """
        self.action_info = init_info.actions
        #self.constraints = init_info.actions
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
        
        # get observation of where we are
        r = observations[0]
        c = observations[1]
        
        # have we visted this position?
        if (r, c) not in self.visited:
            
            # if so, expand it to see who its children are
            children = []
            for m, (rd, cd) in enumerate(MAZE_MOVES):
                
                # calculate child
                r2 = r + rd
                c2 = c + cd

                # check if we should visit this child
                if not observations[2 + m] and (r2, c2) not in self.visited:
                    children.append((r2, c2))
                    self.parents[(r2, c2)] = (r, c)

            # remember who the children of this position are
            self.children[(r, c)] = children

        # if we have been here check if there are other children we could visit
        children = self.children[(r, c)]
        current = None
        for (rd, cd) in children:
            if (rd, cd) not in self.visited:

                # making a move
                current = (rd, cd) 

        # if not, then we need to backtrack
        if current == None:

            # making a move
            current = self.parents[(r, c)]

        # mark as visited and set marker
        self.visited.append((r, c))
        get_environment().mark_maze_blue(r, c)

        # return action
        return get_action_index((current[0] - r, current[1] - c))






        

