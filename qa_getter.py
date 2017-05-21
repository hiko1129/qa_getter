#!/usr/bin/env python
from bs4 import BeautifulSoup
from selenium import webdriver
import os
import sqlite3
import time


class Scraper:
    def __init__(self):
        self.base_url = 'https://ask.fm/'

    def get_qa(self, sleep_time):
        """質問と回答を取得."""
        soup = self.__get_soup(self.base_url)
        # トップ画面に表示されるユーザ名の取得.
        for link in soup.select('.faces > a'):
            username = link.get('href')
            self.__get_personal_qa(username)
            time.sleep(sleep_time)

    def __get_personal_qa(self, username):
        """個人の質問と回答を取得."""
        user_url = self.base_url + username
        soup = self.__get_soup(user_url)
        print('while getting.')
        for item in soup.select('.item-pager > .item'):
            text = ''
            for p_tag in item.select('.answerWrapper > .streamItemContent-answer'):
                text += p_tag.text
            self.__save_qa(
                item.select('.streamItemContent-question > h2')[0].text,
                text
            )
        self.__close_qa()

    def __get_soup(self, url):
        """bsオブジェクトを取得."""
        driver = webdriver.PhantomJS(service_log_path=os.path.devnull)
        driver.get(url)
        html = driver.page_source.encode('utf-8')
        return BeautifulSoup(html, 'html.parser')

    def __save_qa(self, q, a):
        self.db_manager = DBManager('qa.db')
        self.db_manager.save_qa(q, a)

    def __close_qa(self):
        self.db_manager.close()


class DBManager:
    """DBの管理を行う."""
    def __init__(self, db_name):
        if os.path.exists(db_name):
            self.__enable(db_name)
        else:
            # ファイルの作成が同時に行われる.
            self.__enable(db_name)
            self.c.execute('''
            CREATE TABLE qa (
                qa_id INTEGER PRIMARY KEY AUTOINCREMENT,
                question TEXT,
                answer TEXT,
                UNIQUE (question, answer)
            )
            ''')

    def __enable(self, db_name):
        """使用可能な状態にする."""
        self.conn = sqlite3.connect(db_name)
        self.c = self.conn.cursor()

    def save_qa(self, q, a):
        try:
            self.c.execute('''
            INSERT INTO qa (question, answer)
            VALUES (?, ?)
            ''', (q, a))
            self.conn.commit()
        except sqlite3.IntegrityError:
            print('skip qa.')

    def close(self):
        self.conn.close()


if __name__ == '__main__':
    scraper = Scraper()
    # QA取得の間隔（秒）を設定.
    for i in range(0, 100):
        scraper.get_qa(3)
        print('--Wait 10 minutes--')
        time.sleep(600)
