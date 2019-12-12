import OthelloAction
import OthelloLogic

#sizeを変更することでテストプレイする盤面の大きさを変更できます。
#size = 4
#size = 6
size = 8
board = [[0 for i in range(size)] for j in range(size)]

board[int(size/2)-1][int(size/2)-1] = 1;
board[int(size/2)][int(size/2)-1]=-1;
board[int(size/2)-1][int(size/2)]=-1;
board[int(size/2)][int(size/2)]=1;

player = -1
moves = OthelloLogic.getMoves(board,player,size)
while(True):
	if(player == -1):
		action = OthelloAction.getAction(OthelloLogic.getReverseboard(board),moves)
	else:
		action = OthelloAction.getAction(board,moves)
	if(not (action in moves)):
		print(board)
		print('合法手ではない手が打たれました' + action)
		exit()
	board = OthelloLogic.execute(board,action,player,size)
	OthelloLogic.printBoard(board)
	print('現在の合法手一覧')
	print(moves)
	moves = OthelloLogic.getMoves(board,player*-1,size)
	if(len(moves) == 0):
		moves = OthelloLogic.getMoves(board,player,size)
		if(len(moves) == 0):
			break
	else:
		player = player * -1

print('正常に終了しました。')		
