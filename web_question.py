#! /usr/bin/env pyhton
# coding=utf-8

from flask import Flask

app = Flask(__name__)


@app.route('/deal/<nid>/<file_name>')
def deal_to_xlsx(nid, file_name):
    print("Hello")
    int_nid = int(nid)
    dealNaire = DealNaire()
    infor = dealNaire.deal_data(int_nid, file_name)
    return infor


import pymysql
import pandas.io.sql  as pdsql
import json
import pandas as pd
import os


class DealNaire:
    def clear_str(self, s):
        s = s.replace('[', '')
        s = s.replace(']', '')
        s = s.replace("'", '')
        s = s.replace('"', '')
        return s

    def get_connect(self):#chenghuan!@#
        return pymysql.connect(host='localhost', port=3306, user='root', passwd='root',
                               db='ccnutou', charset='utf8', cursorclass=pymysql.cursors.DictCursor)

    def get_data(self, nid):
        sql_data = 'select ' \
                   'cq.title as question,cr.answer as answer,cr.character as characte ' \
                   'from ch_result cr ' \
                   'LEFT JOIN ch_question cq ' \
                   'ON  cr.qid = cq.id where ' \
                   'cq.nid = %s ' % nid

        conn = self.get_connect()
        df_data = pdsql.read_sql_query(sql_data, conn)
        sql_city = 'select *  from ch_city '
        df_city = pdsql.read_sql_query(sql_city, conn)
        sql_city_answer = 'select' \
                          ' cr.character characte,cr.qid question,cr.answer answer ' \
                          'from ch_result cr WHERE qid=0'
        df_city_answer = pdsql.read_sql_query(sql_city_answer, conn)
        ch_naire_sql = 'select title from ch_narie where id = %s' % nid
        ch_naire_data = pdsql.read_sql_query(ch_naire_sql, conn)
        return df_data, df_city, df_city_answer, ch_naire_data

    def deal_data(self, nid, file_name):
        CITY = '城市'
        ch_data, ch_city, ch_city_answer, ch_naire_s = self.get_data(nid)
        if ch_data is None:
            return "没有对应的数据"
        # 将城市的回答转换成字典
        city_answer_dict = {}
        for i in range(0, ch_city_answer.shape[0]):
            inner = {}
            inner[ch_city_answer.ix[i][1]] = self.clear_str(ch_city_answer.ix[i][2])
            city_answer_dict[ch_city_answer.ix[i][0]] = inner
        # 将城市转化为字典
        city_dict = dict(zip(ch_city['id'], ch_city['city']))

        # 处理json
        df_answer = ch_data['answer']
        df_answer_list = []
        for value in df_answer.values:
            try:
                va = json.loads(value)
                va_clear = self.clear_str(str(va))
                df_answer_list.append(va_clear)
            except:
                va = self.clear_str(str(va))
                df_answer_list.append(va)
        ch_data['answer'] = df_answer_list
        # 转为二维表
        data = {}
        for name, group in ch_data.groupby('characte'):
            df_question_answer = group.drop('characte', axis=1)
            s = pd.Series(df_question_answer['answer'].values, index=df_question_answer['question'].values)
            s_dict = s.to_dict()
            if name in city_answer_dict.keys():  # 添加对应用户的城市回答
                qid_answer_dict = city_answer_dict[name]
                temp_dict = {CITY: qid_answer_dict[0]}
                s_dict.update(temp_dict)
            data[name] = s_dict
        df_last = pd.DataFrame(data).T
        city_s = df_last[CITY]
        # 处理城市
        city_list = []
        for city_value in city_s.values:
            try:
                if ',' in city_value:
                    city_value = city_value.split(',')[0]
                city_b = city_dict[int(city_value)]
                city_list.append(city_b)
            except:
                city_list.append(city_value)
        df_last[CITY] = city_list
        # ch_naire_dict = ch_naire_s.to_dict()
        # ch_naire_title = ch_naire_dict['title'][0]
        # time_name = self.time_to_filename(str(datetime.today()))
        # file_name = ch_naire_title + time_name
        pre_file_path = r'D:\\l'
        file_path = os.path.join(pre_file_path,file_name)
        df_last.to_excel(file_path+'.xlsx')
        return file_name


"""def time_to_filename(self, s):
     s = s.replace('-', '_')
     s = s.replace(' ', '_')
     s = s.replace(':', '_')
     s = s.split('.')[0]
     return s
"""

if __name__ == '__main__':
    app.run()
