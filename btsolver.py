import filereader
import gameboard
import variable
import domain
import trail
import constraint
import constraintnetwork
import time
import queue
import math

# dictionary mapping heuristic to number
'''

for example, to set the variable selection heuristic to MRV,
you would say,
self.setVariableSelectionHeuristic(VariableSelectionHeuristic['MinimumRemainingValue'])
this is needed when you have more than one heuristic to break ties or use one over the other in precedence.
you can also manually set the heuristics in the main.py file when reading the parameters
as the primary heuristics to use and then break ties within the functions you implement
It follows similarly to the other heuristics and chekcs
'''
VariableSelectionHeuristic = {'None': 0, 'MRV': 1, 'DH': 2}
ValueSelectionHeuristic = {'None': 0, 'LCV': 1}
ConsistencyCheck = {'None': 0, 'ForwardChecking': 1, 'ArcConsistency': 2}
HeuristicCheck = {'None': 0, 'NKP': 1, 'NKT': 2}


class BTSolver:
    "Backtracking solver"

    ######### Constructors Method #########
    def __init__(self, gb):
        self.network = filereader.GameBoardToConstraintNetwork(gb)
        self.trail = trail.masterTrailVariable
        self.hassolution = False
        self.gameboard = gb

        self.step = False

        self.numAssignments = 0
        self.numBacktracks = 0
        self.preprocessing_startTime = 0
        self.preprocessing_endTime = 0
        self.startTime = None
        self.endTime = None

        self.varHeuristics = 0  # refers to which variable selection heuristic in use(0 means default, 1 means MRV, 2 means DEGREE)
        self.valHeuristics = 0  # refers to which value selection heuristic in use(0 means default, 1 means LCV)
        self.cChecks = 0  # refers to which consistency check will be run(0 for backtracking, 1 for forward checking, 2 for arc consistency)
        self.heuristicChecks = 0
        # self.runCheckOnce = False
        self.tokens = []  # tokens(heuristics to use)

    ######### Modifiers Method #########


    def setTokens(self, tokens):
        ''' set the set of heuristics to be taken into consideration'''
        self.tokens = tokens

    def setVariableSelectionHeuristic(self, vsh):
        '''modify the variable selection heuristic'''
        self.varHeuristics = vsh

    def setValueSelectionHeuristic(self, vsh):
        '''modify the value selection heuristic'''
        self.valHeuristics = vsh

    def setConsistencyChecks(self, cc):
        '''modify the consistency check'''
        self.cChecks = cc

    def setHeuristicChecks(self, hc):
        '''modify the heurisic check (naked pairs and triples)'''
        self.heuristicChecks += hc

    ######### Accessors Method #########
    def getSolution(self):
        return self.gameboard

    # @return time required for the solver to attain in seconds
    def getTimeTaken(self):
        return self.endTime - self.startTime

    ######### Helper Method #########
    def checkConsistency(self):
        '''which consistency check to run but it is up to you when implementing the heuristics to break ties using the other heuristics passed in'''
        if self.cChecks == 0:
            return self.assignmentsCheck()
        elif self.cChecks == 1:
            return self.forwardChecking()
        elif self.cChecks == 2:
            return self.arcConsistency()
        else:
            return self.assignmentsCheck()

    def checkHeuristics(self):
        if self.heuristicChecks == 1:
            return self.nakedPairs()
        elif self.heuristicChecks == 2:
            return self.nakedTriples()
        elif self.heuristicChecks == 3:
            return self.nakedPairs() and self.nakedTriples()
        else:
            return True    

    def assignmentsCheck(self):
        """
            default consistency check. Ensures no two variables are assigned to the same value.
            @return true if consistent, false otherwise.
        """
        for v in self.network.variables:
            if v.isAssigned():
                for vOther in self.network.getNeighborsOfVariable(v):
                    if v.getAssignment() == vOther.getAssignment():
                        return False
        return True

    def nakedPairs(self):
        for v in self.network.variables:
            if not v.isAssigned() and v.size() == 2:
                pairNode = None
                for vOther in self.network.getNeighborsOfVariable(v):
                    if v.Values() == vOther.Values():
                        pairNode = vOther
                        break
                        
                if(pairNode == None):
                    continue
                            
                intersect = []
                vnhd = self.network.getNeighborsOfVariable(v)
                for neighbor in vnhd:
                    if neighbor in self.network.getNeighborsOfVariable(pairNode):
                        intersect.append(neighbor)
                        
                for nb in intersect:
                    nb.removeValueFromDomain(v.Values()[0])
                    nb.removeValueFromDomain(v.Values()[1])                    
        return True

        
    def nakedTriples(self):
        for v in self.network.variables:
            if not v.isAssigned() and v.size() <= 3:
                vnhd = self.network.getNeighborsOfVariable(v)
                for vSecond in vnhd:
                    tripleVals = v.Values()
                    isTriple = False
                    intersect = []
                    if vSecond.size() == 2 or vSecond.size() == 3:
                        isTriple = True
                        for newVal in vSecond.Values():
                            if newVal not in tripleVals and len(tripleVals) == 3:
                                isTriple = False
                            if newVal not in tripleVals and len(tripleVals) < 3:
                                tripleVals.append(newVal)
                        if isTriple:
                            vnhdSecond = self.network.getNeighborsOfVariable(vSecond)
                            for neighbor in vnhd:
                                if neighbor in vnhdSecond:
                                    intersect.append(neighbor)
                            for vThird in intersect:
                                isTriple = False
                                if vThird.size() == 2 or vThird.size() == 3:
                                    isTriple = True
                                    for newVal in vThird.Values():
                                        if newVal not in tripleVals and len(tripleVals) == 3:
                                            isTriple = False
                                            continue
                                        if newVal not in tripleVals and len(tripleVals) < 3:
                                            tripleVals.append(newVal)
                                    if isTriple:
                                        break
                                            
                    if isTriple and len(tripleVals) == 3:
                        intersect = []
                        for neighbor in vnhd:
                            if neighbor in vnhdSecond and neighbor in self.network.getNeighborsOfVariable(vThird):
                                intersect.append(neighbor)
                        for toRemove in intersect:
                            toRemove.removeValueFromDomain(tripleVals[0])
                            toRemove.removeValueFromDomain(tripleVals[1])
                            toRemove.removeValueFromDomain(tripleVals[2])
                        return True
        return True
            
    def forwardChecking(self):
        for v in self.network.variables:
            if v.isAssigned():
                for vOther in self.network.getNeighborsOfVariable(v):
                    if v.getAssignment() == vOther.getAssignment():
                        return False
                    vOther.removeValueFromDomain(v.getAssignment())
                    if vOther.size() == 0:
                        return False
        return True


    def arcConsistency(self):
        q = queue.Queue()
        for node1 in self.network.variables:
            for node2 in self.network.getNeighborsOfVariable(node1):
                q.put((node1, node2))
        while not q.empty():
            arc = q.get()
            if self.revise(arc):
                if arc[0].size() == 0:
                    return False
                for node in self.network.getNeighborsOfVariable(arc[0]):
                    if node != arc[1]:
                        q.put((node, arc[0]))
        return True


    def revise(self, arc):
        revised = False
        for x in arc[0].Values():
            satisfiable = False
            for y in arc[1].Values():
                if x != y:
                    satisfiable = True
            if not satisfiable:
                arc[0].removeValueFromDomain(x)
                revised = True
        return revised


    def selectNextVariable(self):
        """
            Selects the next variable to check.
            @return next variable to check. null if there are no more variables to check.
        """
        if self.varHeuristics == 0:
            return self.getfirstUnassignedVariable()
        elif self.varHeuristics == 1:
            return self.getMRV()
        elif self.varHeuristics == 2:
            return self.getDegree()
        else:
            return self.getfirstUnassignedVariable()

    def getfirstUnassignedVariable(self):
        """
            default next variable selection heuristic. Selects the first unassigned variable.
            @return first unassigned variable. null if no variables are unassigned.
        """
        for v in self.network.variables:
            if not v.isAssigned():
                return v
        return None

    def getMRV(self):
        var = None
        minRemaining = 1024
        for v in self.network.variables:
            if not v.isAssigned():
                if v.size() < minRemaining:
                    var = v
                    minRemain = v.size()
        return var

    def getDegree(self):
        var = None
        maxUnassigned = 0
        for v in self.network.variables:
            if not v.isAssigned():
                nhd = self.network.getNeighborsOfVariable(v)
                unassigned = []
                for n in nhd:
                    if not n.isAssigned():
                        unassigned.append(n)
                if len(unassigned) > maxUnassigned:
                    var = v
                    maxUnassigned = len(unassigned)
        return var
      

    def getNextValues(self, v):
        """
            Value Selection Heuristics. Orders the values in the domain of the variable
            passed as a parameter and returns them as a list.
            @return List of values in the domain of a variable in a specified order.
        """
        if self.valHeuristics == 0:
            return self.getValuesInOrder(v)
        elif self.valHeuristics == 1:
            return self.getValuesLCVOrder(v)
        else:
            return self.getValuesInOrder(v)


    def getValuesInOrder(self, v):
        """
            Default value ordering.
            @param v Variable whose values need to be ordered
            @return values ordered by lowest to highest.
        """
        values = v.domain.values
        return sorted(values)


    def getValuesLCVOrder(self, v):
        """
            TODO: LCV heuristic
        """
        values = v.domain.values
        dic = {key: 0 for key in values}
        nhd = self.network.getNeighborsOfVariable(v)
        for n in nhd:
            if not n.isAssigned():
                for val in n.Values():
                    if val in dic:
                        dic[val] += 1
        answer = []
        for k, v in sorted(dic.items(), key=lambda kv: kv[1], reverse=False):
            answer.append(k)
        return answer

    def success(self):
        """ Called when solver finds a solution """
        self.hassolution = True
        self.gameboard = filereader.ConstraintNetworkToGameBoard(self.network,
                                                                 self.gameboard.N,
                                                                 self.gameboard.p,
                                                                 self.gameboard.q)

    def GB(self):
        output = "\n\n"
        for i in range(self.gameboard.N):
            for j in range(self.gameboard.N):
                if self.network.variables[((i)*self.gameboard.N+(j+1))-1].isAssigned():
                    v = str(self.network.variables[((i)*self.gameboard.N+(j+1))-1].getAssignment())
                    if v == '10':
                        v = 'A'
                    elif v == '11':
                        v = 'B'
                    elif v == '12':
                        v = 'C'
                    elif v == '13':
                        v = 'D'
                    elif v == '14':
                        v = 'E'
                    elif v == '15':
                        v = 'F'
                    elif v == '16':
                        v = 'G'
                    output += v + " "
                else:
                    output += "  "

                if (j+1) % self.gameboard.q == 0 and j!=0 and j != (self.gameboard.N - 1):
                    output += "| "

            output += "\n"
            if (i+1) % self.gameboard.p == 0 and i!=0 and i != (self.gameboard.N - 1):
                for k in range(self.gameboard.N + self.gameboard.p - 1):
                    output += "- "
                output += "\n"
        return output


    ######### Solver Method #########
    def solve(self):
        """ Method to start the solver """
        self.startTime = time.time()
        # try:
        self.solveLevel(0)
        # except:
        # print("Error with variable selection heuristic.")
        self.endTime = time.time()
        # trail.masterTrailVariable.trailStack = []
        self.trail.trailStack = []


    def solveLevel(self, level):
        """
            Solver Level
            @param level How deep the solver is in its recursion.
            @throws VariableSelectionException
        contains some comments that can be uncommented for more in depth analysis
        """
        # print("=.=.=.=.=.=.=.=.=.=.=.=.=.=.=.=")
        # print("BEFORE ANY SOLVE LEVEL START")
        # print(self.network)
        # print("=.=.=.=.=.=.=.=.=.=.=.=.=.=.=.=")

        first = False
        second = False
        third = False

        if self.hassolution:
            return
        # Select unassigned variable
        v = self.selectNextVariable()
        #print("V SELECTED --> " + str(v))

        # check if the assigment is complete
        if (v == None):
            # print("!!! GETTING IN V == NONE !!!")
            for var in self.network.variables:
                if not var.isAssigned():
                    raise ValueError("Something happened with the variable selection heuristic")
            self.success()
            return

        # loop through the values of the variable being checked LCV
        # print("getNextValues(v): " + str(self.getNextValues(v)))
        for i in self.getNextValues(v):
            
            # print("next value to test --> " + str(i))
            self.trail.placeTrailMarker()

            # check a value
            # print("-->CALL v.updateDomain(domain.Domain(i)) to start to test next value.")
            v.updateDomain(domain.Domain(i))
            self.numAssignments += 1
            #print(self.GB())

            #if v.name == "v144" and i == 11:
            #    first = True
            #    if input("FIRST Enter to continue") == 'y':
            #        self.step = True
            #if v.name == "v143" and i == 12:
            #    second = True
            #    if input("SECOND Enter to continue") == 'y':
            #        self.step = True
            #if v.name == "v142" and i == 10:
            #    third = True
            #    if input("THIRD Enter to continue") == 'y':
            #        self.step = True
            #if self.step:
            #    input("Enter to continue")

            # move to the next assignment
            if self.checkConsistency() and self.checkHeuristics():
                self.solveLevel(level + 1)
                print(self.GB())

            # if this assignment failed at any stage, backtrack
            if not self.hassolution:
                # print("=======================================")
                # print("AFTER PROCESSED:")
                # print(self.network)
                # print("================ ")
                # print("self.trail before revert change: ")
                for i in self.trail.trailStack:
                    pass
                    # print("variable --> " + str(i[0]))
                    # print("domain backup --> " + str(i[1]))
                # print("================= ")

                self.trail.undo()
                self.numBacktracks += 1
                # print("REVERT CHANGES:")
                # print(self.network)
                # print("================ ")
                # print("self.trail after revert change: ")
                for i in self.trail.trailStack:
                    pass
                    # print("variable --> " + str(i[0]))
                    # print("domain backup --> " + str(i[1]))
                # print("================= ")

            else:
                return


# cd Downloads\PythonSudoku-master
# python main.py ExampleSudokuFiles\PH1.txt output.txt 600 ACP MRV LCV NKP NKT
