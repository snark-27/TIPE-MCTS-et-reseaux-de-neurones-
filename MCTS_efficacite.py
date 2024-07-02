import chess
import math
from time import time
from random import randint,choice
import sys
import numpy
sys.setrecursionlimit(32767)


def descente_blanc(b):
    if b.is_checkmate():
        if b.outcome().winner:
            return 1
        return -1
    return 0
    
    l=list(b.legal_moves)
    b.push_san(str(l[randint(0,len(l)-1)]))
    return descente(b)

def descente_noir(b):
    if b.is_checkmate():
        if b.outcome().winner:
            return -1
        return 1
    return 0
    
    l=list(b.legal_moves)
    b.push_san(str(l[randint(0,len(l)-1)]))
    return descente(b)

def MCTS_noir(b,d):
    def aux(n,b,c,dic):
        if dic[c][2]=={}:
            for i in b.legal_moves:
                dic[c][2][str(i)]=[0,0,{}]
            if dic[c][2]=={}:
                if b.is_checkmate():
                    if b.outcome().winner:
                        dic[c][1]=-float('inf')
                        return -1
                    dic[c][1]=float('inf')
                    return 1
                return 0
            fils=choice(list(dic[c][2].keys()))
            bc=b.copy()
            bc.push_san(fils)
            dic[c][2][fils]=[2,descente_noir(bc),{}]
            return dic[c][2][fils][1]
        
        else:
            m=-float('inf')
            for i in dic[c][2]:
                if dic[c][2][i][0]==0:
                    fils=i
                else:
                    k=dic[c][2][i][1]/dic[c][2][i][0]+math.sqrt(2*math.log(n)/dic[c][2][i][0])
                    if k>m:
                        fils=i
                        m=k
            bc=b.copy()
            bc.push_san(fils)
            v=aux(dic[c][2][fils][0],bc,fils,dic[c][2])
            dic[c][2][fils][1]+=v
            dic[c][2][fils][0]+=1
            return v
        
    d[''][1]+=aux(d[''][0],b,'',d)
    d[''][0]+=1
    return d

def MCTS_blanc(b,d):
    def aux(n,b,c,dic):
        if dic[c][2]=={}:
            for i in b.legal_moves:
                dic[c][2][str(i)]=[1,0,{}]
            if dic[c][2]=={}:
                if b.is_checkmate():
                    if b.outcome().winner:
                        dic[c][1]=float('inf')
                        return 1
                    dic[c][1]=-float('inf')
                    return -1
                return 0
            fils=choice(list(dic[c][2].keys()))
            bc=b.copy()
            bc.push_san(fils)
            dic[c][2][fils]=[2,descente_blanc(bc),{}]
            return dic[c][2][fils][1]
        
        else:
            m=-float('inf')
            for i in dic[c][2]:
                if dic[c][2][i][0]==0:
                    fils=i
                else:
                    k=dic[c][2][i][1]/dic[c][2][i][0]+math.sqrt(2*math.log(n)/dic[c][2][i][0])
                    if k>m:
                        fils=i
                        m=k
            bc=b.copy()
            bc.push_san(fils)
            v=aux(dic[c][2][fils][0],bc,fils,dic[c][2])
            dic[c][2][fils][1]+=v
            dic[c][2][fils][0]+=1
            return v
        
    d[''][1]+=aux(d[''][0],b,'',d)
    d[''][0]+=1
    return d

def MCTS_duree(tmax,b):
    d={'':[1,0,{}]}
    t=time()
    i=0
    while time()-t<tmax:
        i+=1
        MCTS(b,d)
    return i

    


def MCTS_cnn(b,d):
    def aux(n,b,c,dic):
        if dic[c][2]=={}:
            for i in b.legal_moves:
                dic[c][2][str(i)]=[0,0,{},max(.5,min(1.5,f_cook(board_vers_plateau(b),motif_cook2)[0][0]/2+1))]
            if dic[c][2]=={}:
                if b.is_checkmate():
                    if b.outcome().winner:
                        dic[c][1]=float('inf')
                        return 1
                    dic[c][1]=-float('inf')
                    return -1
                return 0
            fils=choice(list(dic[c][2].keys()))
            bc=b.copy()
            bc.push_san(fils)
            dic[c][2][fils][0]=2
            dic[c][2][fils][1]=descente_blanc(bc)
            return dic[c][2][fils][1]
        
        else:
            m=-float('inf')
            for i in dic[c][2]:
                if dic[c][2][i][0]==0:
                    fils=i
                else:
                    k=dic[c][2][i][1]/dic[c][2][i][0]+(math.sqrt(2*math.log(n)/dic[c][2][i][0]))*dic[c][2][i][3]
                                                                                                                            
                    if k>m:
                        fils=i
                        m=k
            bc=b.copy()
            bc.push_san(fils)
            v=aux(dic[c][2][fils][0],bc,fils,dic[c][2])
            dic[c][2][fils][1]+=v
            dic[c][2][fils][0]+=1
            return v
        
    d[''][1]+=aux(d[''][0],b,'',d)
    d[''][0]+=1
    return d



def MCTS_duree_cnn(tmax,b):
    d={'':[1,0,{},0]}
    t=time()
    i=0
    while time()-t<tmax:
        i+=1
        MCTS_cnn(b,d)
    return i



def randomboard(n):
    board = chess.Board()
    i = 0
    coup = 0
    l = []
    turn = 1
    while board.outcome() is None and i<n:
        i += 1
        turn *=-1
        coup = choice(tuple(board.legal_moves))
        board.push(coup)
    #affichage(board)
    return board,turn

def f_cook(plateau,lpoids):
    for i in lpoids:
        plateau=f_cooked(plateau,i)
    return plateau

def board_vers_plateau(b):
    conversion={'r':-4,'n':-2,'b':-3,'q':-5,'k':-6,'p':-1,'R':4,'N':2,'B':3,'Q':5,'K':6,'P':1,'.':0}
    plateau=[i.split() for i in str(b).split('\n')]
    for i in range(8):
        for j in range(8):
            plateau[i][j]=conversion[plateau[i][j]]
    return plateau

def f_cooked(plateau,poids):
    d=len(plateau)
    n=int(math.sqrt(len(poids)))
    conv=[]
    for i in range(d-n+1):
        conv.append([])
        for j in range(d-n+1):
            conv[i].append(0)
            
            for k in range(n):
                for l in range(n):
                    conv[i][j]+=poids[n*k+l]*(plateau[i+k][j+l])
                    
    return conv




motif_cook2=[[-8.146844277724078, 4.868872566699451, 6.889380840538129, -7.484648660767502], [0.001471325378639907, -0.36075048178784763, -0.0633851519885265, -0.011909848811884373], [-1.7763103562176146, 3.2517654407367966, 2.909219678522701, 0.1560854405658486], [0.00018683626457750705, -2.6915285530291026e-05, 0.0002995509277516483, 0.00021120859425436165], [0.3308575413168811, 0.19656770952264122, 0.13847789609558078, 0.30230809581167756], [-7.894287265622284, -4.6577433119657705, -1.0631367584076101, 6.1649369103688], [-1.4222722050881256, 5.040621584052883, -0.6022041423631874, 3.0653340216443348]]


    
def partie(algo_blanc,algo_noir,tmax):
    b=chess.Board()
    d_blanc={'':[1,0,{}]}
    d_noir={'':[1,0,{}]}
    k=0
    while not b.is_game_over():
        if k%2==0:
            t=time()
            while time()-t<tmax:
                d=algo_blanc(b,d_blanc)
            c=''
            t=-float('inf')
            for i in d_blanc[''][2]:
                a=d[''][2][i][0]
                if a>t:
                    t=a
                    c=i
            d_blanc['']=d_blanc[''][2][c]
            if k>1:
                d_noir['']=d_noir[''][2][c]
            b.push_san(c)
            
        else:
            t=time()
            while time()-t<tmax:
                d=algo_noir(b,d_noir)
            c=''
            t=-float('inf')
            for i in d_noir[''][2]:
                a=d[''][2][i][0]
                if a>t:
                    t=a
                    c=i
            d_noir['']=d_noir[''][2][c]
            d_blanc['']=d_blanc[''][2][c]
            b.push_san(c)
        k+=1
        
    return b

temps=      [ 1, 5,10,20,30,45]
nb_partie=  [20,20,20,10,10,10]
nb_win=     [2, 4, 3, 6, 2, 2]
nb_draw=    [4, 0, 0, 0, 1, 0]
nb_lost=    [14, 13, 17, 4, 7, 8]

"""
for i in range(7):
    for j in range(nb_partie[i]):
        r=partie(MCTS_cnn,MCTS_noir,temps[i]).outcome().winner
        print(r)
        if r:nb_win[i]+=1
        elif r==None:nb_draw[i]+=1
        else:nb_lost[i]+=1
    print(nb_win)
    print(nb_draw)
    print(nb_lost)
    print()
"""
