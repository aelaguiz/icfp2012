import sys

ROBOT = 'R'
ROCK = '*'
EMPTY = ' '
LAMBDA = '\\'
OPEN_LIFT='O'
CLOSED_LIFT='L'
EARTH = '.'

MOVE_LEFT='L'
MOVE_RIGHT='R'
MOVE_UP='U'
MOVE_DOWN='D'
MOVE_WAIT='W'
MOVE_ABORT='A'

class Map:
    def __init__(self):
        self.width = -1
        self.height = 0
        self.lams = 0
        self.map = []
        self.died = False
        self.done = False
        self.changed = False
        self.robot_pos = None
        self.exit_pos = None
        self.lam_pos = []

    def copy(self, old):
        self.width = old.width
        self.height = old.height
        self.lams = old.lams

        self.map = []
        for old_row in old.map:
            new_row = list(old_row)
            self.map.append(new_row)

        self.done = old.done
        self.changed = old.changed
        self.robot_pos = old.robot_pos
        self.exit_pos = old.exit_pos
        self.lam_pos = list(old.lam_pos)

    def addLine(self, line):
        # Assumes no trailing newline

        if self.width != -1 and len(line) < self.width:
            while(len(line)<self.width):
                line += EMPTY

        elif self.width != -1 and len(line) > self.width:
            self.width = len(line)

            for row in self.map:
                while(len(row)<self.width):
                    row.append(EMPTY)
        else:
            self.width = len(line)

        row = list(line)
        self.map.insert(0, row)
        self.height += 1

    def init(self):
        for (y,row) in enumerate(self.map):
            for (x,cell) in enumerate(row):
                if cell == ROBOT:
                    self.robot_pos = (x,y)
                    break
                    #print "Found robot at", self.robot_pos

        for (y, row) in enumerate(self.map):
            for (x, cell) in enumerate(row):
                if cell == LAMBDA:
                    self.lam_pos.append((x,y))

        self.find_exit()

        #print self.lam_pos
        #print self
        #sys.exit(1)

    def __repr__(self):
        res = ""

        for y in reversed(range(0,self.height)):
            row = self.map[y]
            for (x,cell) in enumerate(row):
                if y == self.robot_pos[1] and x ==\
                    self.robot_pos[0]:
                    res += 'H'
                #elif cell == 'R':
                    ##print "Got robot at ",x,y,"coords are",self.robot_pos
                    #res += str(cell)
                else:
                    res += str(cell)
            res += "\n"
        
        return res

    def valid(self, x,y):
        if x>= 0 and x < self.width and\
            y >= 0 and y < self.height:
                return True

        #print x,y,"not valid within",self.width,self.height
        return False

    def get(self, x,y):
        return self.map[y][x]

    def set(self,x,y, value):
        self.map[y][x] = value

    def empty(self,x,y):
        return self.valid(x,y) and self.get(x,y) == EMPTY

    def not_empty(self,x,y):
        return self.valid(x,y) and self.get(x,y) != EMPTY

    def rock(self,x,y):
        return self.valid(x,y) and self.get(x,y) == ROCK

    def earth(self,x,y):
        return self.valid(x,y) and self.get(x,y) == EARTH

    def lam(self,x,y):
        return self.valid(x,y) and self.get(x,y) == LAMBDA

    def robot(self,x,y):
        return self.valid(x,y) and self.get(x,y) == ROBOT

    def lift(self,x,y):
        return self.valid(x,y) and (self.get(x,y) == CLOSED_LIFT or
                self.get(x,y)==OPEN_LIFT)

    def find_exit(self):
        for (y,row) in enumerate(self.map):
            for (x,cell) in enumerate(row):
                if cell == CLOSED_LIFT or\
                    cell == OPEN_LIFT:
                    self.exit_pos = (x,y)
                    print "Exit at ", self.exit_pos
                    break

    def is_doable(self):
        possible = [(1, 0), (-1, 0), (0, 1), (0, -1)]

        visited = []

        required = [self.exit_pos] + self.lam_pos

        pos_list = [self.robot_pos]

        while len(pos_list) > 0:
            pos = pos_list.pop(0)
            visited.append(pos)

            for delta in possible:
                x = pos[0] + delta[0]
                y = pos[1] + delta[1]

                new_pos = (x,y)

                if self.empty(x,y) or self.earth(x,y) or self.lam(x,y) or\
                    self.lift(x,y):
                    if new_pos in required:
                        idx = required.index(new_pos)
                        required.pop(idx)

                        if len(required) == 0:
                            return True

                    if new_pos not in visited:
                        pos_list.append(new_pos)

        return False

    def is_reachable(self, test_pos):
        possible = [(1, 0), (-1, 0), (0, 1), (0, -1)]

        visited = []

        pos_list = [test_pos]

        while len(pos_list) > 0:
            pos = pos_list.pop(0)
            visited.append(pos)

            for delta in possible:
                x = pos[0] + delta[0]
                y = pos[1] + delta[1]

                new_pos = (x,y)

                if self.empty(x,y) or self.earth(x,y) or self.lam(x,y):
                    if new_pos not in visited:
                        pos_list.append(new_pos)
                if self.robot(x,y):
                    return True

        return False

    def is_finishable(self):
        if not self.is_reachable(self.exit_pos):
            return False

        for pos in self.lam_pos:
            if not self.is_reachable(pos):
                #print "Map unfinishable due to lambda being blocked off"
                #print self
                return False

        return True

    def lam_count(self):
        cnt = 0
        for row in self.map:
            for cell in row:
                if cell == LAMBDA:
                    cnt += 1

        return cnt

    def valid_move(self, move):
        if move == MOVE_WAIT:
            return True

        def valid(x,y):
            return self.valid(x,y)

        def empty(x,y):
            return self.empty(x,y)

        def rock(x,y):
            return self.rock(x,y)

        new_pos = self.robot_pos

        if(move == MOVE_LEFT):
            new_pos = (new_pos[0]-1, new_pos[1])
        elif (move == MOVE_RIGHT):
            new_pos = (new_pos[0]+1, new_pos[1])
        elif(move == MOVE_UP):
            new_pos = (new_pos[0], new_pos[1]+1)
        elif(move == MOVE_DOWN):
            new_pos = (new_pos[0], new_pos[1]-1)

        if not valid(new_pos[0], new_pos[1]):
            return False

        new_cell = self.get(new_pos[0], new_pos[1])

        ##print "New cell is",new_cell, " at ", new_pos
        #(x', y' ) is Empty, Earth, Lambda or Open Lambda Lift.
        #   - If it is a Lambda, that Lambda is collected.
        #   - If it is an Open Lambda Lift, the mine is completed
        if new_cell == EMPTY or new_cell == EARTH:
            return True

        elif new_cell == LAMBDA:
            return True

        elif new_cell == OPEN_LIFT:
            return True

        # If x' = x + 1 and y' = y (i.e. the Robot moves right), (x'
        # ,y') is a Rock, and (x + 2; y) is Empty. 
        elif new_cell == ROCK and move == MOVE_RIGHT and \
            empty(self.robot_pos[0]+2,self.robot_pos[1]):
            return True

        # If x' = x - 1 and y' = y (i.e. the Robot moves left), (x'
        # y') is a Rock, and (x -  2; y) is Empty.  
        elif new_cell == ROCK and move == MOVE_LEFT and\
            empty(self.robot_pos[0]-2,self.robot_pos[1]):
            return True

        return False

    def move(self, move):
        # We reset the change flag each tick so it can be used to determine
        # if the player action caused the map to be change (rocks fall, etc)
        self.changed = False

        # A wait move just means tick the map and return
        if(move == MOVE_WAIT):
            #print "Waiting at", self.robot_pos
            self.update()
            return True

        def valid(x,y):
            return self.valid(x,y)

        def empty(x,y):
            return self.empty(x,y)

        def rock(x,y):
            return self.rock(x,y)

        new_pos = self.robot_pos

        #print "Attempting move",move,"from", new_pos

        #Move left, L, moving the Robot from (x; y) to (x  1; y).
        #Move right, R, moving the Robot from (x; y) to (x + 1; y).
        #Move up, U, moving the Robot from (x; y) to (x; y + 1).
        #Move down, D, moving the Robot from (x; y) to (x; y  1).
        if(move == MOVE_LEFT):
            new_pos = (new_pos[0]-1, new_pos[1])
        elif (move == MOVE_RIGHT):
            new_pos = (new_pos[0]+1, new_pos[1])
        elif(move == MOVE_UP):
            new_pos = (new_pos[0], new_pos[1]+1)
        elif(move == MOVE_DOWN):
            new_pos = (new_pos[0], new_pos[1]-1)

        # Invalid destination, just fail
        if not valid(new_pos[0], new_pos[1]):
            #print "New position not valid", new_pos
            return False

        new_cell = self.get(new_pos[0], new_pos[1])

        ##print "New cell is",new_cell, " at ", new_pos
        #(x', y' ) is Empty, Earth, Lambda or Open Lambda Lift.
        #   - If it is a Lambda, that Lambda is collected.
        #   - If it is an Open Lambda Lift, the mine is completed
        if new_cell == EMPTY or new_cell == EARTH:
            #print "Movement",move,"valid into empty or earthen cell"
            # Allow default movement
            pass

        elif new_cell == LAMBDA:
            self.lams += 1

            #print "Movement",move,"valid into lambda"

            #print "Collected lambda, now have", self.lams, "out of",\
                #self.lam_count()

            #print self.lam_pos
            #print self

            idx = self.lam_pos.index((new_pos[0], new_pos[1]))
            self.lam_pos.pop(idx)

            #print "After removal", self.lam_pos

            self.changed = True

        elif new_cell == OPEN_LIFT:
            #print "Mine complete!"
            self.done = True

        # If x' = x + 1 and y' = y (i.e. the Robot moves right), (x'
        # ,y') is a Rock, and (x + 2; y) is Empty. 
        elif new_cell == ROCK and move == MOVE_RIGHT and \
            empty(self.robot_pos[0]+2,self.robot_pos[1]):
            # Additionally, the Rock moves to (x + 2; y).
            self.set(self.robot_pos[0]+2, self.robot_pos[1], ROCK)
            #print "Movement",move,"valid valid pushing rock right"
            self.changed = True

        # If x' = x - 1 and y' = y (i.e. the Robot moves left), (x'
        # y') is a Rock, and (x -  2; y) is Empty.  
        elif new_cell == ROCK and move == MOVE_LEFT and\
            empty(self.robot_pos[0]-2,self.robot_pos[1]):
            # Additionally, the Rock moves to (x - 2; y).
            self.set(self.robot_pos[0]-2, self.robot_pos[1], ROCK)
            #print "Movement",move,"valid valid pushing rock left"
            self.changed = True

        else:
            # This is an invalid move, so we just return
            # which prevents the move from actually being taken
            # and instead the robot "waits"
            #print "Movement",move,"invalid - just waiting at",self.robot_pos
            self.update()
            #print "After update for wait",self.robot_pos
            return True

        self.set(self.robot_pos[0], self.robot_pos[1], EMPTY)
        self.set(new_pos[0], new_pos[1], ROBOT)

        oldpos = self.robot_pos
        self.robot_pos = new_pos

        self.update()
        #print "Took move",move,"from",oldpos,"to",new_pos
        return True

    def update(self):
        newMap = [list(r) for r in self.map]

        def valid(x,y):
            return self.valid_coord(x,y)

        def get(x,y):
            return self.get(x,y)

        def set(x,y, value):
            self.changed = True
            newMap[y][x] = value

        # Not safe to simply say "not empty" because that may indicate it is an
        # invalid cell, not that it is actually unoccupied, must use not_empty
        def empty(x,y):
            return self.empty(x,y)

        def not_empty(x,y):
            return self.not_empty(x,y)

        def rock(x,y):
            return self.rock(x,y)

        def lam(x,y):
            return self.lam(x,y)

        def robot(x,y):
            return self.robot(x,y)

        def lam_count():
            return self.lam_count()
    
        lams = lam_count()

        for (y,row) in enumerate(self.map):
            for (x,cell) in enumerate(row):
                # If (x; y) contains a Rock, and (x; y - 1) is Empty:
                if cell == ROCK and empty(x,y-1):
                    # (x; y) is updated to Empty, (x; y - 1) is updated to Rock
                    #print "Rock at",x,y,"fell"
                    set(x,y, EMPTY)
                    set(x,y-1, ROCK)

                    if robot(x,y-2):
                        #print "Killed the robot!"
                        self.died = True

                #If (x; y) contains a Rock, (x; y  - 1) contains a Rock, (x +
                #            1; y) is Empty and (x + 1; y - 1) is Empty:
                if cell == ROCK and rock(x,y-1) and empty(x+1,y) and\
                    empty(x+1,y-1):
                    #(x; y) is updated to Empty, (x + 1; y -  1) is updated to
                    #Rock
                    #print "Rock at",x,y,"slid to the right and down"
                    set(x,y, EMPTY)
                    set(x+1,y-1, ROCK)

                    if robot(x+1,y-2):
                        #print "Killed the robot!"
                        self.died = True

                #If (x; y) contains a Rock, (x; y - 1) contains a Rock, either (x
                #        + 1; y) is not Empty or (x + 1; y -  1) is not Empty,
                #        (x - 1; y) is Empty and (x - 1; y - 1) is Empty
                if cell == ROCK and rock(x,y-1) and (not_empty(x+1,y) or\
                    not_empty(x+1,y-1)) and empty(x-1,y) and empty(x-1,y-1):
                    # (x; y) is updated to Empty, (x - 1; y - 1) is updated to
                    # Rock.) 
                    #print "Rock at",x,y,"slid to the left and down"
                    set(x,y, EMPTY)
                    set(x-1,y-1,ROCK)

                    if robot(x-1,y-2):
                        #print "Killed the robot!"
                        self.died = True

                #If (x; y) contains a Rock, (x; y -  1) contains a Lambda, (x + 1; y) 
                # is Empty and (x + 1; y - 1) is Empty:
                if cell == ROCK and lam(x,y-1) and empty(x+1,y) and\
                    empty(x+1,y-1):
                    #(x; y) is updated to Empty, (x + 1; y - 1) is updated to Rock.
                    #print "Rock at ",x,y,"fell down the right side of lambda"
                    set(x,y,EMPTY)
                    set(x+1,y-1,ROCK)

                    if robot(x+1,y-2):
                        #print "Killed the robot!"
                        self.died = True

                # If (x; y) contains a Closed Lambda Lift, and there are no
                # Lambdas remaining:
                if cell == CLOSED_LIFT and lams == 0:
                    # (x; y) is updated to Open Lambda Lift.
                    set(x,y,OPEN_LIFT)

        self.map = newMap
