#!/usr/bin/env python
# coding: utf-8

# In[3]:


import requests
import re
from PIL import Image
from io import BytesIO
import os


# In[15]:


def getpng(ids):#输入IMDB电影编号，将爬取到的IMDB官网封面图放入pic folder文件夹。只有官网有图片并且pic folder文件夹没有这个封面的时候程序会将爬取到的图片放如pic folder文件夹中。
    #输入imdb电影编号
    imdbpng=ids+".png"
    #访问图片缓存文件夹
    filenames=os.listdir(r'pic folder')
    #如果输入的电影对应编号在缓存文件夹中有对应图片，则不继续执行    
    #如果本地没有图片，则通过requests爬虫爬取imdb官网获取这部电影的封面
    if imdbpng not in filenames:
        headers={
            'User-Agent':"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Safari/537.36 Edg/96.0.1054.29"
        }
        url=f'https://www.imdb.com/title/{ids}'
        response= requests.get(url=url,headers=headers)
        page_text=response.text
        img_src="0"
        #通过正则表达式提取封面对应url
        obj=re.compile(r'srcSet="(?P<img>(http|ftp|https):\/\/[\w\-_]+(\.[\w\-_]+)+([\w\-\.,@?^=%&:/~\+#]*[\w\-\@?^=%&/~\+#])?) 190w')
        x=obj.finditer(page_text)
        for i in x:
            img_src=i.group("img")
        if img_src != "0":
            response = requests.get(img_src)
            image = Image.open(BytesIO(response.content))
            image.save(f'pic folder/{ids}.png')

