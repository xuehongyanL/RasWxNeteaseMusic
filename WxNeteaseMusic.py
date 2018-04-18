# coding=utf-8
import json
import itchat
import threading
import time
from NeteaseMusicApi import *
import pygame


class Player:
    def __init__(self):
        with open('settings.json')as f:
            self.uid=json.load(f)['uid']
        if self.uid:
            self.login()
        self.playLock = False
        self.help_msg = \
            u"H: 帮助信息\n" \
            u"M: 播放列表\n" \
            u"N: 下一曲\n"\
            u"U: 用户歌单\n"\
            u"R: 正在播放\n"\
            u"T: 热门单曲\n"\
            u"E: 退出\n"
        self.con = threading.Condition()
        self.playlist = getPlaylist(3778678)
        self.mp3 = self.playlist[0]
        self.track = pygame.mixer
        self.track.init()
        t = threading.Thread(target=self.play)
        t.start()

    def login(self):
        pass

    def msg_handler(self, args):
        arg_list = args.split(" ")  # 参数以空格为分割符
        if len(arg_list) == 1:  # 如果接收长度为1
            arg = arg_list[0]
            res = ""
            if arg == u'H':  # 帮助信息
                res = self.help_msg
            elif arg == u'N':  # 下一曲
                if len(self.playlist) > 0:
                    if self.con.acquire():
                        self.con.notifyAll()
                        self.con.release()
                    res = u'切换成功，正在播放: ' + self.playlist[0][0]
                else:
                    res = u'当前播放列表为空'
            elif arg == u'U':  # 用户歌单
                user_playlist = getLists(self.uid)
                if user_playlist == []:
                    res = u"用户播放列表为空"
                else:
                    index = 0
                    for data in user_playlist:
                        res += str(index) + ". " + data[0] + "\n"
                        index += 1
                    res += u"\n 回复 (U 序号) 切换歌单"
            elif arg == u'M':  # 当前歌单播放列表
                if len(self.playlist) == 0:
                    res = u"当前播放列表为空，回复 (U) 选择播放列表"
                i = 0
                for song in self.playlist:
                    res += str(i) + ". " + song[0] + "\n"
                    i += 1
                res += u'\n回复 (N) 播放下一曲， 回复 (N 序号)播放对应歌曲'
            elif arg == u'R':  # 当前正在播放的歌曲信息
                pass
                '''
                song_info = self.playlist[-1]
                artist = song_info.get("artist")
                song_name = song_info.get("song_name")
                album_name = song_info.get("album_name")
                res = u"歌曲：" + song_name + u"\n歌手：" + artist + u"\n专辑：" + album_name
                '''
            elif arg == u'T':  # 热门单曲
                self.playlist = getPlaylist(3778678)
                if len(self.playlist) == 0:
                    res = u"当前播放列表为空，请回复 (U) 选择播放列表"
                i = 0
                for song in self.playlist:
                    res += str(i) + ". " + song[0] + "\n"
                    i += 1
                res += u'\n回复 (N) 播放下一曲， 回复 (N 序号)播放对应歌曲'
            elif arg == u'E':  # 关闭音乐
                if self.con.acquire():
                    self.track.music.pause()
                    res = u'播放已停止'
            else:
                try:
                    index = int(arg)
                    if index > len(self.playlist) - 1:
                        res = u"输入不正确"
                    else:
                        if self.con.acquire():
                            self.con.notifyAll()
                            self.con.release()
                except:
                    res = u'输入不正确'
        elif len(arg_list) == 2:  # 接收信息长度为2
            arg1 = arg_list[0]
            arg2 = arg_list[1]
            if arg1 == u"U":
                user_playlist = getLists(self.uid)
                if user_playlist == []:
                    res = u"用户播放列表为空"
                else:
                    try:
                        index = int(arg2)
                        data = user_playlist[index]
                        playlist_id = data[1]  # 歌单序号
                        self.playlist = getPlaylist(playlist_id)
                        res = u"用户歌单切换成功，回复 (M) 可查看当前播放列表"
                        if self.con.acquire():
                            self.con.notifyAll()
                            self.con.release()
                    except:
                        res = u"输入有误"
            elif arg1 == u'N':  # 播放第X首歌曲
                index = int(arg2)
                tmp_song = self.playlist[index]
                self.playlist.insert(0, tmp_song)
                if self.con.acquire():
                    self.con.notifyAll()
                    self.con.release()
                res = u'切换成功，正在播放: ' + self.playlist[0][0]
                time.sleep(.5)
                del self.playlist[-1]
        else:
            res = u"输入有误"
        return res

    def play(self):
        while True:
            if self.con.acquire() and self.playLock:
                if len(self.playlist) != 0:
                    # 循环播放，取出第一首歌曲，放在最后的位置，类似一个循环队列
                    self.mp3 = self.playlist[0]
                    self.playlist.remove(self.mp3)
                    self.playlist.append(self.mp3)
                    mid = self.mp3[1]
                    try:
                        getMp3(mid)
                        temp = self.track.music.load(
                            './temp/{0}.mp3'.format(mid))
                        self.track.music.play()
                        print(self.mp3[0])
                        self.con.notifyAll()
                        self.con.wait(self.mp3[2]/1000)
                        self.con.notifyAll()
                        self.con.release()
                    except:
                        print('歌曲 {0} 无法播放'.format(self.mp3[0]))
                else:
                    try:
                        self.track.music.stop()
                        self.con.notifyAll()
                        self.con.wait()
                    except:
                        pass
