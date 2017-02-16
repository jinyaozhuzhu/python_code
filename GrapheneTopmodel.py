# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""
from gensim import corpora,models
import pandas as pd
import logging
import re
import numpy as np
from nltk.stem import SnowballStemmer
import os
from numpy import linalg as la

logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)
FILE_PATH = 'F:\patent\graphene\data\Graphene.xls'
YEAR_INTERVAL = [1992,2008,2010,2011,2012,2013,2014,2017]
OUT_PATH = 'F:\patent\graphene\code\model_topic\csv'
FILE_TYPE = 'csv'

class GraphModel():
    
    def getInformation(self,file_name):
        gra_data  = pd.read_excel(file_name,na_values='NA')
        abstract_array = gra_data['abstract']
        abstract_list = abstract_array.tolist()
        
        application_date_array = gra_data['application date']
        application_date_list = application_date_array.tolist()
        return application_date_list,abstract_list
        
    def  disposeTime(self,application_date_list):
        str_time = map(str,application_date_list)
        year_time = map(lambda x:x[:4],str_time)
        return year_time
        
    def disposeAbstract(self,abstract_list):
        docs_list = [0]*len(abstract_list)
        for i,value in enumerate(abstract_list):
            values = re.split(r'[-()\s\n\t.,]+',value)
            docs_list[i] = map(str.lower,map(str,values))
        
        with open(r'F:\patent\graphene\code\topic_model\stopwords.sw') as f:
            stop_word = f.read()
        stop_words = (re.split(r'[-\s\n]+',stop_word))
        stop_words  = tuple(stop_words)
        a = ''   
        docs_list = [[word for word in doc if word not in stop_words or not word==a] for doc in docs_list]
        
        snowball_stemmer = SnowballStemmer('english') 
        new_docs_list = [[snowball_stemmer.stem(word) for word in doc] for doc in docs_list]    
        docs_list = [[word for word in doc if word not in stop_words] for doc in new_docs_list]
        
        return [doc[1:len(doc)-1] for doc in docs_list]
    
    def getDictionary(self,docs_list):
       dictionary = corpora.Dictionary(docs_list)
       dictionary.filter_extremes(no_below=1,no_above=1,keep_n=None)
       return dictionary
        
    def aggreTimeAndAbstract(self,year_time,docs_list):
        int_year = list(map(int,year_time))
        cats = pd.cut(int_year,YEAR_INTERVAL,labels=YEAR_INTERVAL[:-1],right=False)
        year_list = cats.get_values().tolist()
        year_list = list(map(str,year_list))
        
        mapping = {}
        year_set = set(year_list)
        for x in year_set:
            mapping[x] = [] 

        for year,abstr in zip(year_list,docs_list):
            mapping[year].append(abstr)
        return mapping 
        
    def buildLda(self,mapping,dictionary):
       lda_mapping = {}
       for year in mapping:
           abstract = mapping[year]
           corpus = [dictionary.doc2bow(text) for text in abstract]
           tfidfModel = models.TfidfModel(corpus)
           tfidfVectors = tfidfModel[corpus]
           lda = models.LdaModel(tfidfVectors, id2word=dictionary, num_topics=10)
           lda_mapping[year] = lda
       return lda_mapping
    
    def cosSim(inA,inB):
        num=float(inA.T*inB)
        denom = la.norm(inA)*la.norm(inB)
        return 0.5+0.5*(num/denom)
       
    def distanceModel(self,ldax,lday,file_name):
        xindex = []
        for i in range(10):
            xi=''
            for j in range(5):
                xi = xi+' '+ldax.show_topic(i,5)[j][0]
            xindex.append(xi)
        
        ycolumns = []
        for i in range(10):
            yc = ''
            for j in range(5):
                yc = yc+' '+lday.show_topic(i,5)[j][0]
            ycolumns.append(yc)
        df = pd.DataFrame(index=xindex,columns=ycolumns)
        
        column_df = ['word','weight'] 
        for m in range(10):
            for n in range(10):
                dfx=pd.DataFrame(ldax.show_topic(m,5341),columns=column_df)
#                x_word = dfx['word'].tolist()
                
                dfy=pd.DataFrame(lday.show_topic(n,5341),columns=column_df)
#                y_word = dfy['word'].tolist()
                
#                x_word.extend(y_word)
#                word_set = set(x_word)
#                word_list = [word for word in word_set]
#                word_list_df = pd.DataFrame(word_list,columns=['word'])
#                
#                dfx_merge = pd.merge(word_list_df,dfx,how='left',on='word')
#                dfy_merge = pd.merge(word_list_df,dfy,how='left',on='word')
#                
#                dfx_sort = dfx_merge.fillna(0).sort_index(by='word')  
#                dfy_sort = dfy_merge.fillna(0).sort_index(by='word')                  
#
                dfx_sort = dfx.sort_index(by='word')  
                dfy_sort = dfy.sort_index(by='word')
                dfx_val = dfx_sort['weight'].values
                dfy_val = dfy_sort['weight'].values
                df.ix[m][n] = self.cosSim(np.mat(dfx_val).T,np.mat(dfy_val).T)
#                df.ix[m][n] = np.sqrt(np.sum((dfx_val-dfy_val)**2))
                PATH = os.path.join(OUT_PATH,file_name)
                PATH_TYPE = '.'.join([PATH,FILE_TYPE])
                df.to_csv(PATH_TYPE)

'''运行'''                
graphModel = GraphModel()
'''1.获取日期时间和摘要
'''    
application_date_list,abstract_list = graphModel.getInformation(FILE_PATH)
'''2.标准化时间和文本
'''
year_time  = graphModel.disposeTime(application_date_list)
docs_list = graphModel.disposeAbstract(abstract_list)

'''3.获取字典并对时间分片,构建了一个巨大的字典（与前面说的字典不是同一个）
''' 
dictionary = graphModel.getDictionary(docs_list)
mapping = graphModel.aggreTimeAndAbstract(year_time,docs_list)    

'''4.获取lda模型的列表集
'''    
lda_mapping = graphModel.buildLda(mapping,dictionary)
    
'''5.生成模型相似度矩阵(pandas.DataFrame),并保存至文件
'''    
#year_interval = map(str,YEAR_INTERVAL[:len(YEAR_INTERVAL)-1])
#for i in range(len(year_interval)-1):
#    ldax = lda_mapping[year_interval[i]]
#    lday = lda_mapping[year_interval[i+1]]
#    file_name = '_'.join([year_interval[i],year_interval[i+1]])  
#    graphModel.distanceModel(ldax,lday,file_name)
    
    
    
  #http://python.jobbole.com/81397/  
    
    
   