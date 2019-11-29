def execute(board,action,player,size):

        dirs = [
            [-1,-1],
            [0,-1],
            [1,-1],
            [-1,0],
            [1,0],
            [-1,1],
            [0,1],
            [1,1]
        ]
        board[action[1]][action[0]] = player
        for dir in dirs:
            bool,flips = executeFlip(board,player,action[1],action[0],dir,size)
            if(bool):
                for flip in flips:
                    board[flip[0]][flip[1]] = player
        return board
    

def executeFlip(b,p,x,y,dir,size):
        if(x+dir[0]<0 or x+dir[0]>=size or y+dir[1]<0 or y+dir[1]>=size):
            return 0,None
        
        if(b[x+dir[0]][y+dir[1]] == (p*-1)):
            flips = []
            flips.append([x+dir[0],y+dir[1]])
            inc_dir=[dir[0],dir[1]]
            inc_dir[0] += dir[0]
            inc_dir[1] += dir[1]
            while(True):
                if(x+inc_dir[0]<0 or x+inc_dir[0]>=size or y+inc_dir[1]<0 or y+inc_dir[1]>=size):
                    return 0,None
                
                if(b[x+inc_dir[0]][y+inc_dir[1]] == p):
                    return 1,flips
                elif(b[x+inc_dir[0]][y+inc_dir[1]] == 0):
                    return 0,None
                
                flips.append([x+inc_dir[0],y+inc_dir[1]])
                inc_dir[0] += dir[0]
                inc_dir[1] += dir[1]
            
        
        return 0,None

def getMoves(board,player,size):
        dirs = [
            [-1,-1],
            [0,-1],
            [1,-1],
            [-1,0],
            [1,0],
            [-1,1],
            [0,1],
            [1,1]
        ]
        moves=[]
        for y in range(size):
            for x in range(size):
                if(board[x][y] == (player*-1)):
                    for dir in dirs: 
                        bool,legal_move = search(player, board, x, y,dir,size)
                        if(bool and not(legal_move in moves)):
                            moves.append(legal_move)
        return moves
    

def search(p,b,x,y,dir,size):
        if(x+dir[0]<0 or x+dir[0]>=size or y+dir[1]<0 or y+dir[1]>=size):
            return 0,None
        
        if(b[x+dir[0]][y+dir[1]] == 0):
            reverse_dir=[dir[0]*-1,dir[1]*-1]
            while(True):
                if(x+reverse_dir[0]<0 or x+reverse_dir[0]>=size or y+reverse_dir[1]<0 or y+reverse_dir[1]>=size):
                    return 0,None
                
                if(b[x+reverse_dir[0]][y+reverse_dir[1]] == p):
                    return 1,[y+dir[1],x+dir[0]]
                elif(b[x+reverse_dir[0]][y+reverse_dir[1]] == 0):
                    return 0,None
                
                reverse_dir[0] += dir[0]*-1
                reverse_dir[1] += dir[1]*-1
        
        return 0,None

def getReverseboard(board):
        rev_board = board
        for x in range(len(rev_board)):
            for y in range(len(rev_board)):
                board[x][y] = rev_board[x][y] * -1    
        return board

    