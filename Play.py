import requests
import json
import OthelloAction
import AuthCheck

base_url = "http://ec2-13-231-106-93.ap-northeast-1.compute.amazonaws.com/api/"
headers = AuthCheck.auth_check(base_url)

r = requests.post(base_url + "where", headers=headers)

if(r.status_code == 422):
	message = r.json()
	print(message['message'])
	exit()
if(r.status_code != requests.codes.ok):
	print('エラーが発生しました。')
	exit()

data = r.json()
roomid = data['id']
player = data['player']
board = []
payload = {}

if(player == 1):
	payload = {'player':player}
	r = requests.post(base_url + "wait_for_player/" + roomid, data=payload,headers=headers)
	data = r.json()
	board = json.loads(data['board'])
	moves = json.loads(data['moves'])
else:
	rev_board = json.loads(data['board'])
	board = json.loads(data['board'])
	for x in range(len(rev_board)):
		for y in range(len(rev_board)):
			board[x][y] = rev_board[x][y] * -1
	moves = json.loads(data['moves'])

action = json.dumps(OthelloAction.getAction(board,moves))
payload = {'action' : action,'player':player}

while(True):
	r = requests.post(base_url + "room/" + roomid, data=payload,headers=headers)
	if(r.status_code == 401):
		print('認証エラーが起きました。')
		exit()
	if(r.status_code != requests.codes.ok):
		print('エラーが発生しました。')
		exit()
	data = r.json()
	if(data['finish_flag']):
		print('処理が終了しました。')
		exit()
	if(player == -1):	
		rev_board = json.loads(data['board'])
		board = json.loads(data['board'])
		for x in range(len(rev_board)):
			for y in range(len(rev_board)):
				board[x][y] = rev_board[x][y] * -1
	else:
		board = json.loads(data['board'])
	moves = json.loads(data['moves'])
	action = json.dumps(OthelloAction.getAction(board,moves))
	print("打った場所は" + action);
	payload = {'action' : action,'player':player}
