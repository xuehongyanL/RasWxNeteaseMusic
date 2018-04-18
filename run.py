#coding=utf-8
from WxNeteaseMusic import Player
import itchat

player=Player()
@itchat.msg_register(itchat.content.TEXT)
def mp3_player(msg):
    text=msg['Text']
    res=player.msg_handler(text)
    return res

itchat.auto_login()#可选enableCmdQR=True
player.playLock=True
itchat.run(debug=False)
exit()