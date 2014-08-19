import random
import numpy as np
import copy
import string
import mysql.connector
import types

cnx = mysql.connector.connect(user = 'username', password = 'password', host = '127.0.0.1', database = 'connectfour')
cursor = cnx.cursor()

c = copy.deepcopy

#This just grabs the amount of games played.
Games = 0
cursor.execute("SELECT SUM(p1gwin) FROM history;")
Games += cursor.fetchone()[0]
cursor.execute("SELECT SUM(p2gwin) FROM history;")
Games += cursor.fetchone()[0]
print Games

#Capitalized if it is indexed; lowercase if not.

#--[[   Functions for communicating with the SQL datumsbase    ]]--#

def grabRecord(stateid):
    cursor.execute("SELECT * FROM history WHERE stateid = '{}';".format(stateid))
    for a in cursor: #Treat as if it is just cursor[0]
        return a
    return -1

def createRecord(stateid, p1wins, p2wins, p1gwin, p2gwin):
    cursor.execute("INSERT INTO history VALUES ('{}', {}, {}, {}, {});".format(stateid, p1wins, p2wins, p1gwin, p2gwin))
    cnx.commit()
    
def updateRecord(stateid, field, value):
    cursor.execute("UPDATE history SET {} = {} WHERE stateid = '{}';".format(field, value, stateid))
    cnx.commit()

#--[[   Functions for converting information from datumsbase to game.   ]]--#

Characters = string.digits + string.ascii_letters + "`~!@#$%^&*()_+-=<>:"
def pack(Matrix):
    String = "00"
    for i in range(6):
        for j in range(7):
            String += str(int(Matrix[i][j]))
    stateid = ""
    for repeat in range(11):
        n = 0
        for a in range(4):
            n += int(String[a])*3**(3 - a)
        stateid += Characters[n]
        String = String[4:]
    return stateid

def unpack(stateid): #This of course, is not actually used. But it is nice for debugging and just to have.
    String = ""
    for a in stateid:
        n = Characters.find(a)
        NewString = ""
        for b in range(4):
            r = n%3
            n = n//3
            NewString = str(r) + NewString
        String += NewString
    String = String[2:]
    Matrix = np.zeros((6,7))
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
    Record = grabRecord(pack(Matrix2))
    if Record == -1:
        return 1
    if Record[turn + 2]:
        Field = ["p1gwin", "p2gwin"]
        updateRecord(pack(Matrix), Field[turn - 1], 1) #Unfortunately the way this is set up right now it will constantly be setting this to 1 even though it is often already at 1.
        return 1.5
    if Record[5 - turn]:
        return 0
    wins = Record[turn] + 1.0 # +1 is more or less to avoid /0
    losses = Record[3 - turn]
    return wins/(wins + losses)

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
                createRecord(pack(Matrix), turn == 1, turn == 2, turn == 1, turn == 2)
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
            for stateid in History:
                Record = grabRecord(stateid)
                if Record == -1:
                   createRecord(stateid, turn == 1, turn == 2, 0, 0)
                else:
                   Field = ["p1wins", "p2wins"]
                   updateRecord(stateid, Field[turn - 1], str(Record[turn] + 1))
            break
        if highest == -1: #This means there is a tie. Not sure what I am going to do about those.
            break
        if highest == 0: #This means that no matter where the bot plays they will lose eventually. (Against itself)
            Field = ["p1gwin", "p2gwin"]
            updateRecord(pack(Matrix), Field[2 - turn], 1)
            print("First sign of intelligent life detected.")
            for a in Matrix:
                print a
        j = random.choice(ties)
        i = findi(j, Matrix)
        Matrix[i][j] = turn
        History.append(pack(Matrix))
    Games += 1
    if Games%10 == 0:
        print Games
