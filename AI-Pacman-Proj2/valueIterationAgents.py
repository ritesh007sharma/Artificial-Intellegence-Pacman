# valueIterationAgents.py
# -----------------------
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


# valueIterationAgents.py
# -----------------------
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


import mdp, util

from learningAgents import ValueEstimationAgent
import collections

class ValueIterationAgent(ValueEstimationAgent):
    """
        * Please read learningAgents.py before reading this.*

        A ValueIterationAgent takes a Markov decision process
        (see mdp.py) on initialization and runs value iteration
        for a given number of iterations using the supplied
        discount factor.
    """
    def __init__(self, mdp, discount = 0.9, iterations = 100):
        """
          Your value iteration agent should take an mdp on
          construction, run the indicated number of iterations
          and then act according to the resulting policy.

          Some useful mdp methods you will use:
              mdp.getStates()
              mdp.getPossibleActions(state)
              mdp.getTransitionStatesAndProbs(state, action)
              mdp.getReward(state, action, nextState)
              mdp.isTerminal(state)
        """
        self.mdp = mdp
        self.discount = discount
        self.iterations = iterations
        self.values = util.Counter() # A Counter is a dict with default 0
        self.runValueIteration()

    def runValueIteration(self):
        # Write value iteration code here
        for i in range(self.iterations):
            dictionary = util.Counter()
            for state in self.mdp.getStates():
                if self.mdp.isTerminal(state):
                    continue
                maxVal = - float('inf')
                for action in self.mdp.getPossibleActions(state):
                    totalValue = self.computeQValueFromValues(state, action)
                    if totalValue > maxVal:
                        maxVal = totalValue
                        # intialize everyhting to 0 if it's not in self.values for Vk(s')
                        #set self.values at the end
                dictionary[state] = maxVal
            self.values = dictionary


    def getValue(self, state):
        """
          Return the value of the state (computed in __init__).
        """
        return self.values[state]


    def computeQValueFromValues(self, state, action):
        """
          Compute the Q-value of action in state from the
          value function stored in self.values.
        """
        "*** YOUR CODE HERE ***"
        val = 0
        for t in self.mdp.getTransitionStatesAndProbs(state, action):
            val = val + t[1] * (self.mdp.getReward(state, action, t[0]) + self.discount * self.values[t[0]])
        return val

    def computeActionFromValues(self, state):
        """
          The policy is the best action in the given state
          according to the values currently stored in self.values.

          You may break ties any way you see fit.  Note that if
          there are no legal actions, which is the case at the
          terminal state, you should return None.
        """
        "*** YOUR CODE HERE ***"
        if len(self.mdp.getPossibleActions(state)) == 0:
            return None

        valMap = util.Counter()
        for action in self.mdp.getPossibleActions(state):
            valMap[action] = self.computeQValueFromValues(state, action)

        return valMap.argMax()

    def getPolicy(self, state):
        return self.computeActionFromValues(state)

    def getAction(self, state):
        "Returns the policy at the state (no exploration)."
        return self.computeActionFromValues(state)

    def getQValue(self, state, action):
        return self.computeQValueFromValues(state, action)

class AsynchronousValueIterationAgent(ValueIterationAgent):
    """
        * Please read learningAgents.py before reading this.*

        An AsynchronousValueIterationAgent takes a Markov decision process
        (see mdp.py) on initialization and runs cyclic value iteration
        for a given number of iterations using the supplied
        discount factor.
    """
    def __init__(self, mdp, discount = 0.9, iterations = 1000):
        """
          Your cyclic value iteration agent should take an mdp on
          construction, run the indicated number of iterations,
          and then act according to the resulting policy. Each iteration
          updates the value of only one state, which cycles through
          the states list. If the chosen state is terminal, nothing
          happens in that iteration.

          Some useful mdp methods you will use:
              mdp.getStates()
              mdp.getPossibleActions(state)
              mdp.getTransitionStatesAndProbs(state, action)
              mdp.getReward(state)
              mdp.isTerminal(state)
        """
        ValueIterationAgent.__init__(self, mdp, discount, iterations)

    def runValueIteration(self):
        states = self.mdp.getStates()
        for i in range(self.iterations):
            dictionary = self.values.copy()
            # print dictionary
            state = states[i % len(states)]
            # print state
            if state == self.mdp.isTerminal(state):
                continue
            maxValue = - float('inf')
            possibleActions = self.mdp.getPossibleActions(state)
            for action in possibleActions:
                totalValue = self.computeQValueFromValues(state, action)
                if totalValue > maxValue:
                    maxValue = totalValue
                    dictionary[state] = maxValue
            self.values = dictionary

class PrioritizedSweepingValueIterationAgent(AsynchronousValueIterationAgent):
    """
        * Please read learningAgents.py before reading this.*

        A PrioritizedSweepingValueIterationAgent takes a Markov decision process
        (see mdp.py) on initialization and runs prioritized sweeping value iteration
        for a given number of iterations using the supplied parameters.
    """
    def __init__(self, mdp, discount = 0.9, iterations = 100, theta = 1e-5):
        """
          Your prioritized sweeping value iteration agent should take an mdp on
          construction, run the indicated number of iterations,
          and then act according to the resulting policy.
        """
        self.theta = theta
        ValueIterationAgent.__init__(self, mdp, discount, iterations)

    def runValueIteration(self):
        def getMaxQval(state):
            return max(self.getQValue(state, a) for a in self.mdp.getPossibleActions(state))
        # compute predecessors for all states
        predecessors = {}
        
        for state in self.mdp.getStates():
            predecessors[state] = set()
        
        for state in self.mdp.getStates():
            if not self.mdp.isTerminal(state): # for all non terminal states
                for action in self.mdp.getPossibleActions(state):
                    for successor, probability in self.mdp.getTransitionStatesAndProbs(state, action):
                        if probability > 0:
                            predecessors[successor].add(state)
        
        PQ = util.PriorityQueue()
        for state in self.mdp.getStates():
            if not self.mdp.isTerminal(state):
                maxVal = getMaxQval(state)
                diff = abs(self.values[state] - maxVal)
                PQ.push(state, -diff)
                
                #calculate highest q value from all possible actions from s
                # prioritize states with higher error
                
        for i in range(self.iterations):
            if PQ.isEmpty():
                break
                
            state = PQ.pop()
            if not self.mdp.isTerminal(state):
                maxVal = getMaxQval(state)
                self.values[state] = maxVal

            for p in predecessors[state]:
                maxVal = getMaxQval(p)
                diff = abs(self.values[p] - maxVal)
                if diff > self.theta:
                    PQ.update(p, -diff)

