#! /usr/bin/env pyhton
# coding=utf-8

import  requests
from bs4 import BeautifulSoup
import pymysql

class Book:

    def get_connect(self):
            return pymysql.connect(host='localhost', port=3306, user='root', passwd='root',
                                   db='ccnutou', charset='utf8', cursorclass=pymysql.cursors.DictCursor)

    def get_html(self,url):
        print(url)
        sour_html = requests.get(url).text
        soup = BeautifulSoup(sour_html,'lxml')
        self.parse_html(soup)

    def parse_html(self,soup):
        li_list = soup.find('ul',{'class':'subject-list'}).find_all('li')
        for li in li_list:
            name = li.find('h2').find('a').get_text().strip()
            url = li.find('h2').find('a')['href']
            other = li.find('div', {'class': 'pub'}).get_text().strip()
            try:
                abstract = li.find('div', {'class': 'info'}).find('p').get_text().strip()
            except AttributeError:
                abstract = '无'
            self.insert_database(name,url,other,abstract)

    def insert_database(self,word_name,word_url,word_other,word_abstract):
        db = self.get_connect()
        cursor = db.cursor()
        sql = "insert into b_book  (name,url,other,abstracts)  VALUES ('%s','%s','%s','%s')" % (word_name,word_url,word_other,word_abstract)
        try:
            cursor.execute(sql)
            db.commit()
            print('抓取%s'%word_name)
            print('url:',word_url)
        except :
            print('失败')
            db.rollback()
        db.close()

    def pinjie_url(self):
        print('拼接字符串')
        url_list = []
        pre = 'https://book.douban.com/tag/小说?start='
        tail = '&type=T'
        for i in range(0,1260,20):
            url = pre+str(i)+tail
            url_list.append(url)
        return url_list

    def execut(self):
        url_list = self.pinjie_url()
        for url in url_list:
            self.get_html(url)

book = Book()
book.execut()




# text = requests.get('https://book.douban.com/tag/小说?start=0&type=T').text
# soup = BeautifulSoup(text,'lxml')
# li_list = soup.find('ul',{'class':'subject-list'}).find_all('li')
#
# for li in li_list[:1]:
#     name = li.find('h2').find('a').get_text()
#     other = li.find('div', {'class': 'pub'}).get_text()
#     abstract = li.find('div', {'class': 'info'}).find('p').get_text()
#     print(name)
#     print(other)
#     print(abstract)