import requests
import json
import os

def auth_check(base_url):
	token_path = './.api_token'

	if(os.path.isfile(token_path)):
		with open('./.api_token') as f:
			s = f.read()
			token = s
	else:
		with open(token_path, mode='w') as f:
			print('APIトークンが見つかりませんでした。APIトークンを入力してください。')
			token = input()
			f.write(token)

	while(True):
		headers = {'Authorization':'Bearer ' + token}
		url = base_url + "whome"

		r = requests.get(url, headers=headers)
		if(r.status_code == 401):
			with open(token_path, mode='w') as f:
				print('APIトークンに誤りがあります。正しいAPIトークンを入力してください。')
				token = input()
				f.write(token)
		elif(r.status_code != requests.codes.ok):
			print('エラーが発生しました。')
			exit()
		elif(r.status_code == 200):
			user = r.json()
			print('ようこそ!' + user['user'] + 'さん')
			return headers