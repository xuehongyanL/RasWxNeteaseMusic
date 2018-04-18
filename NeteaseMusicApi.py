#coding=utf-8
import requests
import os
import time
import re

path='./temp'

header={'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:58.0) Gecko/20100101 Firefox/58.0'}
#设置的请求头

def getLists(id,frm=0,max=100): #id为用户id frm为起始位置 max为最大返回个数
    if frm:
        frm=frm-1
    url='http://music.163.com/api/user/playlist/?offset={0}&limit={1}&uid={2}'.format(0,1000,id)
    res=requests.get(url,headers=header)
    j=res.json()
    #获取返回的json
    lists=[]
    for list in j['playlist']:
      lists.append((list['name'],list['id']))
    #生成歌单名和歌单id的列表
    return lists

def getPlaylist(id): #id为歌单id
    url='http://music.163.com/api/playlist/detail?id={0}&updateTime=-1'.format(id)
    res=requests.get(url,headers=header)
    j=res.json()
    #获取返回的json
    playlist=[]
    for song in j['result']['tracks']:
        playlist.append((song['artists'][0]['name']+' - '+song['name'],song['id'],song['duration']))
    #生成歌曲名和、歌曲id和歌曲时长的列表
    return playlist
    
def getMp3(id): #id为歌曲id path为临时文件路径，尽量使用绝对路径
    res=requests.get('http://music.163.com/song/media/outer/url?id={0}.mp3'.format(id),headers=header)
    code=res.status_code
    if code!=200:
        return code
    with open('{0}/{1}.mp3'.format(path,id),'wb')as f:
        f.write(res.content)
    return 200

def processLyrics(id):
    ans=[]
    with open('{0}/lyrics/{1}.lrc'.format(path,id))as f:
            pattern=re.compile(r'\[\d\d\:\d\d\.\d\d')
            lines=f.readlines()
            for line in lines:
                if re.search(pattern,line):
                    if line[10]==']':
                        line=line[:9]+line[10:]
                    ans.append(line)
    with open('{0}/lyrics/{1}.lrc'.format(path,id),'w')as f:
            f.write('')
    with open('{0}/lyrics/{1}.lrc'.format(path,id),'a')as f:
        for line in ans:
            f.write(line)

def showLyrics(id,duration): #id为歌曲id
    res=requests.get('http://music.163.com/api/song/lyric?os=pc&id={0}&lv=-1'.format(id))
    j=res.json()
    try:
        with open('{0}/lyrics/{1}.lrc'.format(path,id),'w')as f:
            f.write(j['lrc']['lyric'])
        processLyrics(id)
        f=open('{0}/lyrics/{1}.lrc'.format(path,id))
        now=(0,'')
        to=(0,'')
        while True:
            print(now[1])
            temp=f.readline()
            if temp=='':
                break
            to=(int(temp[1:3])*60+float(temp[4:8]),temp[10:][:-1])
            time.sleep(to[0]-now[0])
            now=to
        time.sleep(duration-now[0])
        f.close()
    except:
        print('无歌词或纯音乐，请欣赏')
        time.sleep(duration)    
