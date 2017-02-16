#! /usr/bin/env pyhton
# coding=utf-8

import requests
from bs4 import BeautifulSoup
import pymysql
import re

class Book:
    def get_connect(self):
        return pymysql.connect(host='localhost', port=3306, user='root', passwd='root',
                               db='ccnutou', charset='utf8', cursorclass=pymysql.cursors.DictCursor)

    def get_html(self, url):
        print(url)
        sour_html = requests.get(url).text
        soup = BeautifulSoup(sour_html, 'lxml')
        self.parse_html(soup)

    def parse_html(self, soup):
        tr_list = soup.find_all('tr', {'class': 'item'})
        for tr in tr_list:
            name = tr.find('a', {'class': 'nbg'})['title']
            url = tr.find('a', {'class': 'nbg'})['href']
            image_url = tr.find('a', {'class': 'nbg'}).find('img')['src']
            image_name = re.split(r'/',image_url)[-1]
            image_content = requests.get(image_url).content
            with open('images/'+image_name,'ab') as fw:
                fw.write(image_content)
            other = tr.find('p', {'class': 'pl'}).get_text().strip()
            try:
                abstracts = BeautifulSoup(requests.get(url).text, 'lxml').find('div', {'id': 'link-report'}).find(
                    'span', {
                        'property': 'v:summary'}).get_text().strip()
            except AttributeError:
                abstracts = '无'
            self.insert_database(name,other, abstracts,url,image_name)

    def insert_database(self, m_name, m_other, m_abstract, m_url, m_image):
        db = self.get_connect()
        cursor = db.cursor()
        sql = "insert into a_movie (name,other,abstracts,url,image)  VALUES ('%s','%s','%s','%s','%s')" % (
        m_name, m_other, m_abstract, m_url, m_image)
        try:
            cursor.execute(sql)
            db.commit()
            print('抓取%s'%m_name)
        except :
            print('失败')
            db.rollback()

    def pinjie_url(self):
        print('拼接字符串')
        url_list = []
        pre = 'https://movie.douban.com/tag/爱情?start='
        tail = '&type=T'
        for i in range(0, 7840, 20):
            url = pre + str(i) + tail
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
