import random
import numpy as np
import copy
import string

c = copy.deepcopy
#Capitalized if it is indexed; lowercase if not.
#--[[   Functions for getting information to and from the database   ]]--#

Characters = string.digits + string.ascii_letters + string.punctuation

def pack(number):
    String = ""
    print number
    n = int(number)
    L = len(Characters)
    while n:
        r = n%L
        n = n//L
        String = Characters[r] + String
    return String

def unPack(String):
    n = 0
    L = len(Characters)
    for a in range(len(String)):
        char = String[-a - 1]
        n += string.find(Characters, char)*L**a
    return n

def toString(Matrix):
    String = ""
    for Row in Matrix:
        for n in Row:
            String += str(int(n))
    return pack(String)

def toMatrix(String):
    Matrix = np.zeros((6,7))
    String = str(unPack(String))
    for i in range(6):
        for j in range(7):
            Matrix[i][j] = int(String[0])
            String = String[1:]
    return Matrix

#--[[   These functions are all related to the actual playing of the game.  ]]--#

def findi(j, Matrix):
    for a in range(6):
        if Matrix[5 - a][j] == 0:
            return 5 - a
    return -1

def check(i, j, Matrix):
    try:
        return Matrix[i][j]
    except IndexError:
        return -1

def checkForEnd(i, j, turn, Matrix): #Compressed checkForEnd function.
    for Direction in [(1,1), (1,0), (0,1), (-1, 1)]:
        consecutive = 0
        a, b = Direction
        for m in range(-3,4):
            I = a*m + i
            J = b*m + j
            if check(I, J, Matrix) == turn and I >= 0 and J >= 0:
                consecutive += 1
                if consecutive == 4:
                    return 1
            else:
                consecutive = 0
    return 0

def appraise(i, j, turn, Matrix): #Gets the value of a board.
    Matrix2 = c(Matrix)
    Matrix2[i][j] = turn
    if checkForEnd(i, j, turn, Matrix2):
        return 2
    return 1

#--[[   The game.  ]]--#

while True:
    Matrix = np.zeros((6,7))
    History = []
    turn = 2
    Done = 0
    while True:
        turn = 3 - turn
        highest = -1
        value = -1
        for j in range(7):
            i = findi(j, Matrix)
            value = appraise(i, j, turn, Matrix)
            if value == 2:
                Matrix[i][j] = turn
                Done = 1
                highest = 2
                break
            if value > highest:
                ties = [j]
                highest = value
            elif value == highest:
                ties.append(j)
        if Done:
            print History
            break
        if highest == -1: #This means there is a tie. Not sure what I am going to do about those.
            break
        j = random.choice(ties)
        i = findi(j, Matrix)
        Matrix[i][j] = turn
        History.append(toString(Matrix))
    break
