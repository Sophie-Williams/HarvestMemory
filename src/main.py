from graphics import *
import parser
import player
import cpu
import os
import random


memorySize = 2**12
memory = [0] * memorySize
drawObjects = []
textObjects = []
columnCount = 8
columnHeight = len(memory) // columnCount
cellHeight = 1
initialSeeds = 20
decay = 0.7
fruit = set()


def initMemory():
    # Randomly pick some starting points
    seeds = []
    for i in range(initialSeeds):
        seeds.append(random.randrange(0, memorySize, 1))
    
    # Add fruit at the random points in memory.
    # Use a decay function, 0.75^x, to add more fruit nearby.
    for seed in seeds:
        memory[seed] = -100
        fruit.add(seed)
        chance = decay
        i = 1
        while chance > 0.01:
            # Move away from the seed in both directions.
            rLeft = random.random()
            rRight = random.random()
            if rLeft <= chance:
                if seed-i > 0:
                    memory[seed-i] = -100
                    fruit.add(seed-i)
            if rRight <= chance:
                if seed+i < len(memory)-1:
                    memory[seed+i] = -100
                    fruit.add(seed+i)
            i = i + 1
            chance = decay**i
    return memory

def drawColumns(win):
    xstart = 480
    ystart = 100
    width = 40
    height = 2
    offset = 0
    for j in range (0, columnCount):
        for i in range(0, columnHeight):
            r = Rectangle(Point(xstart+j*8+offset, ystart+i*cellHeight), Point(xstart+width+j*8+offset, ystart+height+i*cellHeight))
            r.setFill("black")
            r.setOutline("black")
            r.draw(win)
            drawObjects.append(r)
        offset = offset + 90


def drawPlayers(win, players):
    xstart = 100
    ystart = 130
    xoffset = 0
    yoffset = 0
    for p in range(1, len(players)+1):
        t = Text(Point(xstart+xoffset, ystart+yoffset), " ")
        t.setText(players[p-1].displayName + ": 3")
        t.setSize(22)
        t.draw(win)
        textObjects.append(t)

        yoffset = yoffset + 42
        if p % 15 == 0:
            xoffset = xoffset + 210
            yoffset = 0


def drawTitle(win):
    t1 = Text(Point(230, 45), "Harvest Miner")
    t1.setSize(36)
    t1.draw(win)
    t2 = Text(Point(220, 75), "by Austin Henley")
    t2.setSize(16)
    t2.draw(win)


def updateColumns():
    for i in range(0, len(memory), 1):
        if memory[i] == -100:
            drawObjects[i].setFill("red")
            drawObjects[i].setOutline("red")

def createPlayers():
    players = []
    path = os.path.join(os.getcwd(), 'scripts')
    if not os.path.isdir(path):
        print("Error: Scripts folder not found at {}".format(path))
        return None
    for fileName in os.listdir(path):
        try:
            with open(os.path.join(path, fileName), 'r') as f:
                code = f.read()
                p = parser.Parser(fileName, code)
                p.parse()
                players.append(player.Player(fileName.split('.')[0], p.instructions, p.labels))
        except Exception as e:
            print(e)

    random.shuffle(players)
    return players


def updateMemoryGraphics(vmFruit): 
    # Greatly optimize this by just using sets of recently added/removed fruit
    for i in range(0, len(drawObjects), 1):
        if i in vmFruit:
            if memory[i] == -100:
                drawObjects[i].setFill("red")
                drawObjects[i].setOutline("red")
        else:
            drawObjects[i].setFill("black")
            drawObjects[i].setOutline("black")
        

def updatePlayers(players):
    for i in range(0, len(players)):
        out = players[i].displayName + ": " + str(players[i].registers['rs'])
        textObjects[i].setText(out)


def main():
    initMemory()
    players = createPlayers()
    if players == None:
        return

    win = GraphWin("Harvest Memory", 1280, 800, autoflush=False)
    drawTitle(win)
    drawPlayers(win, players)
    drawColumns(win)
    updateColumns()

    vm = cpu.CPU(memory, fruit, players)
    timer = 0
    while True:
        for i in range(0, 100): # Speed it up!
            if vm.ticks < 10000:
                vm.execute()

        if timer % 4 == 0: # Only update periodically
            updatePlayers(players)
            updateMemoryGraphics(vm.fruit)
            print("Ticks: " + str(vm.ticks))

        timer = timer + 1
        update(5) # 5 frames per second 
    #win.close()   


main()
