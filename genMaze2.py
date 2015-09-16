from numpy import array
import random
#psyco.full()
from visual import *

FILLED = 0
HOLLOW = 1

UNASSIGNED = 0
START = 1
END = 2
TUNNEL = 3
CORNER = 4
TRIPLE = 5

boxes = []

def drawMaze(maze):
    global boxes
    for bx in boxes: bx.visible = 0
    boxes = []
    for i in range(maze.N):
        for j in range(maze.N):
            for k in range(maze.N):
                if maze.data[maze.ind(i,j,k)].state == HOLLOW:
                    newBox = box(pos=(i,j,k), length=1, width=1,height=1, color = color.red)
                    boxes.append(newBox)

def drawLayers(maze):
    sticks = []
    for i in range(maze.N):
        pcs = []
        for j in range(maze.N):
            strch = []
            for k in range(maze.N):
                hol = maze.data[maze.ind(i,j,k)].state == HOLLOW
                ch = 'o'
                if hol: ch = ' '
                strch.append(ch)
            strch = 'o' + ''.join(strch) + 'o'
            pcs.append(strch)
            #print strch
            sticks.extend(strch.split())
        print '  '.join(pcs)
    cnts = [0 for i in range(maze.N + 3)]
    for stick in sticks:
        cnts[len(stick)] += 1
    print 'counts:', cnts

class Cell:
    def __init__(self):
        self.state = FILLED
        self.descrip = UNASSIGNED

    def copy(self):
        newCell = Cell()
        newCell.state = self.state
        newCell.descrip = self.descrip
        return newCell
        
class Maze:
    
    def __init__(self, N):
        self.N = N
        self.bad = False
        self.data = [Cell() for i in range(self.N**3)]

    def copy(self):
        newMaze = Maze(self.N)
        newMaze.data = [self.data[i].copy() for i in range(len(self.data))]
        return newMaze

    def ind(self, i, j, k):
        return i*(self.N**2) + j * self.N + k

    def setStart(self):
        self.data[self.ind(self.N/2, self.N/2, 0)].state = HOLLOW
        self.data[self.ind(self.N/2, self.N/2, 0)].descrip = START
        self.data[self.ind(self.N/2, self.N/2, 1)].state = HOLLOW
        self.data[self.ind(self.N/2, self.N/2, 1)].descrip = END

    # return a list of all mazes built upon the current maze by making
    # one more block hollow:
    def getValidChildMazes(self):
        newMazes = []
        for i in range(self.N):
            for j in range(self.N):
                for k in range(self.N):
                    # if the cell is already hollow, skip trying to make
                    # it hollow:
                    if self.data[self.ind(i,j,k)].state == HOLLOW: continue
                    # otherwise, make it hollow, and see if it's a valid
                    # maze:
                    newMaze = self.copy()
                    newMaze.data[self.ind(i,j,k)].state = HOLLOW
                    newMaze.data[self.ind(i,j,k)].descrip = UNASSIGNED
#                    print 'trying a hollow at %d %d %d'%(i,j,k)
                    if newMaze.checkValid(i,j,k):
#                        print 'valid hollow at %d %d %d'%(i,j,k)
                        newMazes.append(newMaze)

        print 'returning %d child mazes.'%(len(newMazes))
        return newMazes

    def getRandomValidChildMaze(self):
        inds = range(self.N**3)
        random.shuffle(inds)
        for index in inds:
            if self.data[index].state == HOLLOW: continue
            newMaze = self.copy()
            newMaze.data[index].state = HOLLOW
            newMaze.data[index].descrip = UNASSIGNED
            v = index
            i = v / self.N**2
            v -= i * self.N**2
            j = v / self.N
            v -= j * self.N
            k = v
            if newMaze.checkValid(i,j,k): 
#                print 'found a valid child at %d %d %d'%(i,j,k)
                return newMaze
        return None

    # a new maze was created by modifying cell i, j, k; check whether
    # this maze is still valid:
    def checkValid(self, i, j, k):

        for ii in range(i-1,i+2):
            if ii < 0 or ii >= self.N: continue
            for jj in range(j-1, j+2):
                if jj < 0 or jj >= self.N: continue
                for kk in range(k-1, k+2):
                    if kk < 0 or kk >= self.N: continue
                    if not self.checkCellValid(ii, jj, kk):
                        return False
        return True

    # check whether a given cell is valid;
    # we must check for four conditions:
    #   (1) no T-junctions:  hHh
    #                         h
    #   (2) no hollow squares: Hh
    #                          hh
    #   (3) no planar diagonals:  hF
    #                             Fh
    #   (4) no out-of-plane diagonals...can't draw it...
    def checkCellValid(self, i, j, k):
        if self.data[self.ind(i,j,k)].state == FILLED: return True
        
        h = array([[[False for z in range(3)] for y in range(3)] for x in range(3)])
        for ii in [-1, 0, 1]:
            if ii + i < 0 or ii + i >= self.N: continue
            for jj in [-1, 0, 1]:
                if jj + j < 0 or jj + j >= self.N: continue                
                for kk in [-1, 0, 1]:
                    if kk + k < 0 or kk + k >= self.N: continue
                    h[ii,jj,kk] = self.data[self.ind(ii+i,jj+j,kk+k)].state == HOLLOW

        nHolFaces = self.NHollowFaces(h)
        if self.data[self.ind(i,j,k)].descrip == START and nHolFaces > 1: return False
        if nHolFaces == 0: return False
        if self.isTJunction(h): return False
        if self.hollowSquare(h): return False
        if self.planarDiagonal(h): return False
        if self.nonPlanarDiagonal(h): return False
        return True

    def NHollowFaces(self, hol):
        cnt = 0
        if hol[1,0,0]: cnt += 1
        if hol[-1,0,0]: cnt += 1
        if hol[0,1,0]: cnt += 1
        if hol[0,-1,0]: cnt += 1
        if hol[0,0,1]: cnt += 1
        if hol[0,0,-1]: cnt += 1
        return cnt

    def isTJunction(self, hol):

        xHollow = hol[-1,0,0] and hol[1,0,0]
        yHollow = hol[0, -1,0] and hol[0,1,0]
        zHollow = hol[0,0,-1] and hol[0,0,1]
        if xHollow and (hol[0,1,0] or hol[0,-1,0] or hol[0,0,1] or hol[0,0,-1]): return True
        if yHollow and (hol[1,0,0] or hol[-1,0,0] or hol[0,0,1] or hol[0,0,-1]): return True
        if zHollow and (hol[1,0,0] or hol[-1,0,0] or hol[0,1,0] or hol[0,-1,0]): return True  
        return False

    def hollowSquare(self, hol):
        for x in [-1,0,1]:
            for y in [-1,0,1]:
                for z in [-1,0,1]:
                    s = abs(x) + abs(y) + abs(z)
                    if s != 2: continue
                    edge = [x,y,z]
                    if x == 0:
                        face1 = [0,y,0]
                        face2 = [0,0,z]
                    elif y == 0:
                        face1 = [x,0,0]
                        face2 = [0,0,z]
                    else:
                        face1 = [x,0,0]
                        face2 = [0,y,0]
                    if hol[edge[0], edge[1], edge[2]] and hol[face1[0], face1[1], face1[2]] \
                       and hol[face2[0], face2[1], face2[2]]: return True
        return False

    def planarDiagonal(self, hol):
        for x in [-1,0,1]:
            for y in [-1,0,1]:
                for z in [-1,0,1]:
                    s = abs(x) + abs(y) + abs(z)
                    if s != 2: continue
                    edge = hol[x,y,z]
                    if x == 0:
                        face1 = hol[0,y,0]
                        face2 = hol[0,0,z]
                    elif y == 0:
                        face1 = hol[x,0,0]
                        face2 = hol[0,0,z]
                    else:
                        face1 = hol[x,0,0]
                        face2 = hol[0,y,0]
                    if edge and not (face1 or face2): return True
        return False

    def nonPlanarDiagonal(self, hol):
        for x in [-1,0,1]:
            for y in [-1,0,1]:
                for z in [-1,0,1]:
                    s = abs(x) + abs(y) + abs(z)
                    if s != 3: continue
                    corner = hol[x,y,z]
                    face1 = hol[x,0,0]
                    face2 = hol[0,y,0]
                    face3 = hol[0,0,z]
                    if corner and not (face1 or face2 or face3): return True
        return False

                                                              
    # describe the maze; print how many of each type of tunnel element
    # there is:
    def describeMaze(self):
#        drawMaze(self)
#        drawLayers(self)
#        while True:
#            sleep(1)
        nCorners = nTriples = nTunnels = nHollow = 0
        for i in range(len(self.data)):
            curCell = self.data[i]
            if curCell.state == HOLLOW:
                nHollow += 1
                if curCell.descrip == CORNER:
                    nCorners += 1
                elif curCell.descrip == TRIPLE:
                    nTriples += 1
                elif curCell.descrip == TUNNEL:
                    nTunnels += 1
                    
#        print 'maze has %d hollows, %d corners, %d triples, and %d tunnels.'%(nHollow, nCorners, nTriples, nTunnels)

    # explore the virtual tree of mazes:
    def exploreMazes(self, depth = 0):
        self.depth = depth
#        print 'doing explore, depth = %d'%depth
        childMaze = self.getRandomValidChildMaze()
        if childMaze == None:
            #            print 'found finished maze!'
            self.describeMaze()
            return self
        return childMaze.exploreMazes(depth + 1)

    def getNEndsTriples(self):
        nEnds = 0
        nTriples = 0
        for i in range(self.N):
            for j in range(self.N):
                for k in range(self.N):
                    if self.data[self.ind(i,j,k)].state != HOLLOW: continue
                    h = array([[[False for z in range(3)] for y in range(3)] for x in range(3)])
                    for ii in [-1, 0, 1]:
                        if ii + i < 0 or ii + i >= self.N: continue
                        for jj in [-1, 0, 1]:
                            if jj + j < 0 or jj + j >= self.N: continue                
                            for kk in [-1, 0, 1]:
                                if kk + k < 0 or kk + k >= self.N: continue
                                h[ii,jj,kk] = self.data[self.ind(ii+i,jj+j,kk+k)].state == HOLLOW

                    nHolFaces = self.NHollowFaces(h)
                    if nHolFaces == 1: nEnds += 1
                    if nHolFaces == 3: nTriples += 1
        return nEnds, nTriples


N = 7
maze = Maze(N)
recordN = 0
recordMaze = None
while True:
    rate(20)
    maze = Maze(N)
    maze.setStart()
    newMaze = maze.exploreMazes()
    nEnds, nTriples = newMaze.getNEndsTriples()
    #print 'number of ends:', nEnds
    if nTriples > recordN:
        recordN = nTriples
        recordMaze = newMaze        
        drawMaze(recordMaze)
        drawLayers(recordMaze)        
        print 'number of triples is:', nTriples
        print 'new record!'


    

