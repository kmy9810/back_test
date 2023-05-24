from slacker import Slacker		# slacker 모듈을 import
import json				# json파일을 읽어들일 것이므로, 해당 모듈도 import
import os

def slack_notify(text=None, channel='#프로젝트', username="책화점_알리미",attachments=None):
    token = os.environ.get('TOKEN')		# token을 불러온다
    slack = Slacker(token)
    slack.chat.post_message(
        text=text,			# 메세지 내용
        channel=channel,		# 메세지를 전송할 channel
        username=username,		# 사용자 이름
        attachments=attachments)	# 부가 옵션