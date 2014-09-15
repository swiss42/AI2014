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

    def fcost_calc(self, r, c):
        #fcost is defined as our distance from origin plus our heuristic
        return self.get_distance(r,c) + manhattan_heuristic(r,c)

    def reset(self):
        """
        Reset the agent
        """
        self.frontier = {(0,0):self.fcost_calc(0,0)}
        self.visited = []
        self.backpointers = {}
        self.parents = {}
        self.children = {}
        self.open = {} #nodes not yet expanded
        self.f_cost = 0
        self.isAtLimit = False
        #TODO: make open list to keep track of total f_cost reached

    def initialize(self, init_info):
        """
        Initializes the agent upon reset
        """
        self.action_info = init_info.actions
        self.fcost_limit = 5 #self.fcost_calc(0,0)
        #self.constraints = init_info.actions
        return True

    def start(self, time, observations):
        """
        Called on the first move
        """
        print "Strating first move!"
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
        """depth first search will be implemented first"""
        
        # get observation of where we are
        r = observations[0]
        c = observations[1]

        self.f_cost = self.fcost_calc(r,c)
        # prent debugging info
        print "\n\nstart of call"
        print "Current pos: (", r, c, ")"
        print "Current fcost: ", self.f_cost 
        print "fcost_limit: ", self.fcost_limit

        # show visible mark that we were at this position
        get_environment().mark_maze_blue(r, c)

        # have we visted this position?
        if (r, c) not in self.visited:

            # remove from open list
            del self.frontier[(r, c)]
            
            # if so, expand it to see who its children are
            children = []
            for m, (rd, cd) in enumerate(MAZE_MOVES):
                
                # calculate child
                r2 = r + rd
                c2 = c + cd

                # check if we should visit this child
                if not observations[2 + m]:
                    if (r2, c2) not in self.visited:
                        self.frontier[(r2, c2)] = self.fcost_calc(r2,c2) # add to open list
                        children.append((r2, c2, self.fcost_calc(r2, c2)))
                        self.parents[(r2, c2)] = (r, c)

            # remember who the children of this position are
            self.children[(r, c)] = children

        # check if everything at f_cost limit has been searched
        print "Frontier f_cost: ", self.frontier
        if len(self.frontier) > 0: 
            min_fcost = min(self.frontier.itervalues())
            if min_fcost > self.fcost_limit: 
                
                # increased the min_fcost
                print "Limit reached. Increasing limit"
                self.reset()
                self.fcost_limit = min_fcost
                get_environment().teleport(self, 0,0)
                return 4

        # if we have been here check if there are other children we could visit
        children = self.children[(r, c)]
        current = None
        for (rd, cd, fc) in children:
            if (rd, cd) not in self.visited and fc <= self.fcost_limit:

                # making a move
                current = (rd, cd)
                break 

        # if not, then we need to backtrack
        if current == None:

            # making a move
            current = self.parents[(r, c)]

        # mark as visited
        self.visited.append((r, c))

        # return action
        print "end of call\n\n"

        if (r + rd, c + cd) not in self.backpointers:
            self.backpointers[(r + rd, c + cd)] = (r, c)

        # return action
        return get_action_index((current[0] - r, current[1] - c))






        

