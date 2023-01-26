#!/usr/bin/env python
# coding: utf-8

# In[1]:
import pandas as pd
import numpy as np
from math import *

# In[5]:
#read the user rating file and create the data dict for the program 
#读取data_final用户评论数据库
data_final = 'dataset/data_final.csv'
datacontent=pd.read_csv(data_final,encoding='utf-8')
data={}
for i in range(len(datacontent)):
    if not datacontent.iloc[i,1] in data.keys():
        data[datacontent.iloc[i,1]]={datacontent.iloc[i,4]:datacontent.iloc[i,3]}
    else:
        data[datacontent.iloc[i,1]][datacontent.iloc[i,4]]=datacontent.iloc[i,3]
# In[6]:
#define the euclidean distance which will be used to calculate the distance between users 
def euclidean(userx,usery):
    userx_data=userx
    usery_data=data[usery]
    distance=0
    for key in userx_data.keys():
        if key in usery_data.keys():
            distance += pow(float(userx_data[key])-float(usery_data[key]),2)
    return 1/(1+sqrt(distance))
# In[7]:
#define the function which will find the 10 best simliar users
def top10_simliar(userID):
    res=[]
    for userid in data.keys():
        if not userid == userID:
            simliar = euclidean(userID,userid)
            res.append((userid,simliar))
    res.sort(key=lambda val:val[1])
    return res[:10]
#define the function which will find the x best simliar users
def topx_simliar(userID,x):
    res=[]
    for userid in data.keys():
        if not userid == userID:
            simliar = euclidean(userID,userid)
            res.append((userid,simliar))
    res.sort(key=lambda val:val[1])
    return res[:x]
# In[14]:
moviedata5 = 'dataset/moviedata5.tsv'
pddata=pd.read_csv(moviedata5,sep='\t',encoding='utf-8')#读取简易电影库数据。数据库包括imdb编号、标题、平均分、评分人数。
# In[23]:
#define the function to get the the average rating of the movie.
#if there are more than one product having same name in one year, we decided to pick the rating with most number of votes.
def getavrating(x):#取回同年同名电影中评价人数最多的电影的IMDB均分（浮点格式）。如果电影不存在则返回"\N"
    avrat=0
    avr=pddata[pddata.title==x]
    if len(avr)==0:#there's no such movie in the dataset
        avrat=r"\N"
    elif len(avr)==1:#there's one movie in the dataset
        try:
            avrat=float(avr.averageRating)
        except:#nobody gives rating for this movie in the dataset
            avrat=0
    else:
        numvot=0
        for m in range(len(avr)):#there are more than one movie having same name in one year
            if avr.iloc[m,2] !=r'\N' and avr.iloc[m,2] !=r'\\N' and float(avr.iloc[m,3]) > float(numvot):
                numvot=avr.iloc[m,3]
                avrat=avr.iloc[m,2]
    return avrat
# In[17]:
def getallimdbid(x):#取回所有名称相同、同年发布的电影的imdb编码列表。如果不存在则返回空集。
    allid=[]
    ids=pddata[pddata.title==x]
    if len(ids)!=0:
        for i in range(len(ids)):
            allid.append(ids.iloc[i,0])
    return allid
# In[20]:
def get1imdbid(x):#取回同名同年电影中评价人数最多的一部（流传最广的一部）。如果不存在则返回"\N"
    movieid=r"\N"
    ids=pddata[pddata.title==x]
    if len(ids)==0:
        movieid=r"\N"
    elif len(ids)==1:
            movieid=str(ids.iloc[0][0])
    else:
        numvot=0
        for m in range(len(ids)):#there are more than one movie having same name in one year
            if ids.iloc[m,2] !=r'\N' and ids.iloc[m,2] !=r'\\N' and float(ids.iloc[m,3]) > float(numvot):
                numvot=ids.iloc[m,3]
                movieid=ids.iloc[m,0]
    return movieid
# In[10]:
#based on best 10 simliar users, we pick 2 best movies thay've voted from everyone and put them in the list. 
def recommend_based_on_10(user):
    topuserlist = top10_simliar(user)
    totalusertlist = []
    for i in topuserlist:
        test_dupli=[]
        for m in totalusertlist:
            test_dupli.append(m[0])
        oneuserlst=data[i[0]]
        t_lst=[]
        for item in oneuserlst.keys():
            if item not in user.keys():
                if item not in test_dupli:
                    t_lst.append((item,oneuserlst[item]))
        t_lst.sort(key=lambda val:val[1],reverse=True)
        totalusertlist.extend(t_lst[:2])
#based on the recommended movie, we get the ratings from IMDB and recommend top10 IMDB rating movies.
    tlst=[]
    for x in totalusertlist:
        tlst.append((x[0],float(getavrating(x[0]))))
    tlst.sort(key=lambda val:val[1],reverse=True)
    return tlst[:10]
                     
#same to recommend_based_on_10, we just make some parameter changable in order to find the best parameters.  
#这个函数里的user是一个含有多个二元元组(看过的电影、评分为一个元组)的列表。x、y、z、o分别代表选择的最接近样本数、每个最接近样本数选择的电影数量、生成推荐列表的展示开始位置（从0开始）、生成推荐列表的展示结束位置
#输出结果是一个含有元组的列表
def recommend_ppl_hme(user,x,y,z,o):
    topuserlist = topx_simliar(user,x)
    totalusertlist = []
    for i in topuserlist:
        test_dupli=[]
        for m in totalusertlist:
            test_dupli.append(m[0])
        oneuserlst=data[i[0]]
        t_lst=[]
        for item in oneuserlst.keys():
            if item not in user.keys():
                if item not in test_dupli:
                    t_lst.append((item,oneuserlst[item]))
        t_lst.sort(key=lambda val:val[1],reverse=True)
        totalusertlist.extend(t_lst[:y])

    tlst=[]
    for x in totalusertlist:
        tlst.append((x[0],float(getavrating(x[0]))))
    tlst.sort(key=lambda val:val[1],reverse=True)
    return tlst[int(z):int(o):1]


# In[158]:
#user_input=pd.read_csv(input('please input the location and name of your file:'),encoding='utf-8')
#userinput={}
#for i in range(len(user_input)):
#    userinput[user_input.iloc[i,0]]=user_input.iloc[i,1]
#print(userinput)
#print(top10_simliar(userinput))
#print(f'based on {len(user_input)} movies you have watched, we give you the recommendatoins as below:')
#recommend_based_on_10(userinput)
# In[11]:
#user_input=pd.read_csv(input('please input the location and name of your file:'),encoding='utf-8')
#userinput={}
#x=int(input("how many ppl you'd like to pick into final pool?"))
#y=int(input("how many films you'd like to pick movies from each ppl?"))
#z=input("list position from?")
#o=input("list position to?")
#for i in range(len(user_input)):
#    userinput[user_input.iloc[i,0]]=user_input.iloc[i,1]
##print(userinput)
#print(f'based on {len(user_input)} movies you have watched, we give you the recommendatoins as below:')
#recommend_ppl_hme(userinput,x,y,z,o)
# In[31]:
def rd_rec(location,x,y,z,o):#读取文件，输入参数，输出结果，同样为含有元组的列表。五个参数分别为：文件位置、样本池数量、每个样本选择的电影数量、生成推荐列表开始位置、生成推荐列表结束位置。
    user_input=pd.read_csv(location,encoding='utf-8')
    userinput={}
    for i in range(len(user_input)):
        userinput[user_input.iloc[i,0]]=user_input.iloc[i,1]
    result=recommend_ppl_hme(userinput,x,y,z,o)
    return result
# In[ ]: