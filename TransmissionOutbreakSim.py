import random
import math
import json
import time as timefunctions

EVENTRATE = 0.7
MAXTIME = 10
SIMROUNDS = 50000


class TreeNode(object):
    def __init__(self, parent=None, time=0.0, leaf=False):
        global leaftimelist
        self.parent = parent
        self.children = []
        self.time = time
        if leaf:
            self.isLeaf = True
            leaftimelist.append(time)
            self.active = False
        else:
            self.isLeaf = False
            self.active = True
        self.undervalue = 0
        self.toDelete = False


    def tick(self):
        global isalive
        for child in self.children:
            child.tick()
        if self.active:
            isalive = True
            self.time += random.expovariate(EVENTRATE)
            if self.time > MAXTIME:
                self.active = False
            else:
                if random.random() < transchance:
                    self.children.append(TreeNode(parent = self, time = self.time))
                else:
                    self.active = False
                    if self.children:
                        self.children.append(TreeNode(parent = self, time = self.time, leaf = True))
                    else:
                        self.isLeaf = True
                        leaftimelist.append(self.time)


    def finalize(self):
        if not self.isLeaf:
            for child in self.children:
                child.finalize()
            tempchildren = [child for child in self.children if not child.toDelete]
            self.children = tempchildren 
            if len(self.children) <= 1:
                if self.parent:
                    self.parent.children += self.children
                    self.toDelete = True
                elif self.children:
                    self = self.children[0]
                    self.parent = None

            
    def calcMinTime(self):
        for child in self.children:
            child.calcMinTime()
        if self.isLeaf:
            self.minTime = self.time
        else:
            self.minTime = min([child.minTime for child in self.children] + [float('inf')])


    def calcDiscoveryTime(self, minimum = float('inf')):
        if self.isLeaf:
            self.discoveryTime = self.minTime
        else:
            timelist = [child.minTime for child in self.children]
            timelist.sort()
            if minimum <= self.minTime:
                alternative = self.minTime
            else:
                alternative = minimum
            if len(timelist) > 1:
                potential = timelist[1]
            else:
                potential = float('inf')
            self.discoveryTime = min(potential, alternative)
            for child in self.children:
                child.calcDiscoveryTime(self.discoveryTime)


    def seedUndervalue(self, time = float('inf')):
        for child in self.children:
            child.seedUndervalue(time)
        if self.isLeaf or self.discoveryTime > time:
            self.undervalue = 0
        else:
            undervalue = len([child for child in self.children if (child.isLeaf and child.discoveryTime <= time)])
            undervalue += max([child.undervalue for child in self.children])
            a = len([child for child in self.children if ((not child.isLeaf) and child.discoveryTime <= time)])
            if a > 0:
                undervalue += a - 1
            self.undervalue = undervalue
        return self.undervalue


    def calcMaxContrib(self, time = float('inf')):
        if self.discoveryTime > time:
            self.rootvalue = 0
        if self.isLeaf:
            self.rootvalue = 1
        else:
            rootvalue = len([child for child in self.children if (child.isLeaf and child.discoveryTime <= time)])
            underlist = [child.undervalue for child in self.children]
            underlist.sort(reverse=True)
            rootvalue += sum(underlist[0:2])
            a = len([child for child in self.children if ((not child.isLeaf) and child.discoveryTime <= time)])
            if a > 1:
                rootvalue += a - 2
            if self.parent:
                if self.parent.discoveryTime <= time:
                    rootvalue += 1
            self.rootvalue = rootvalue
        self.undervalue = 0
        return max([child.calcMaxContrib(time) for child in self.children] + [self.rootvalue])


    def flushUndervalue(self):
        self.undervalue = 0
        for child in self.children:
            child.flushUndervalue()


    def newickOutput(self, mode=None):
        if not self.parent:
            end = ';'           
        else:
            end = ''
        if self.isLeaf:
            if mode == 'time':
                return str(self.discoveryTime) + end
            elif mode == 'timeint':
                return str(leaftimelist.index(self.discoveryTime)) + end
            else:
                return 'x' + end
        else:
            if mode == 'undervalue':
                name = str(self.undervalue)
            elif mode == 'rootvalue':
                name = str(self.rootvalue)
            elif mode == 'test':
                name = 'x'
            elif mode == 'time':
                name = str(self.discoveryTime)
            elif mode == 'timeint':
                name = str(leaftimelist.index(self.discoveryTime))
            else:
                name = ''

            return '(' + ','.join([child.newickOutput(mode) for child in self.children if child.discoveryTime <= MAXTIME]) + ')' + name + end



def calcMinMaxContrib(n):
    if n == 1:
        return 1

    k = int(math.log2(n))  #n = 2**k + m
    lowbound = 2 ** k
    base = 2 * k
    if n - lowbound == 0:
        return base
    elif n - lowbound <= 2**(k-1):
        return base + 1
    else:
        return base + 2

maxlist = []

outfile = open('ratios.dat', 'w')

timerstart = timefunctions.clock()

for i in range(SIMROUNDS):
    transchance = random.random()
    if i % 100 == 0:
        print(i)
    leaftimelist = [0]

    root = TreeNode()
    isalive = True

    while isalive:
        isalive = False
        root.tick()

    root.calcMinTime()
    root.calcDiscoveryTime()

    leaftimelist.sort()

    maxcontriblist = []
    for time in (leaftimelist[6:]):
        root.seedUndervalue(time)
        maxcontriblist.append(root.calcMaxContrib(time))
    
    if maxcontriblist:
        if len(maxcontriblist) > len(maxlist):
            maxlist = list(range(6, len(leaftimelist)))
            minlist = [calcMinMaxContrib(n) for n in maxlist]
        ratiolist = [(maxcontriblist[i] - minlist[i])/(maxlist[i] - minlist[i]) for i in range(len(maxcontriblist))]

        json.dump(ratiolist, outfile)
        outfile.write('\n')

print(timefunctions.clock() - timerstart)

outfile.close()