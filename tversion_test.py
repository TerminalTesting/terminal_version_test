#! /usr/bin/python
# -*- coding: utf-8 -*-
import unittest
import sys
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from models import *
import time



class TerminalTest(unittest.TestCase):

    os.system('find -iname \*.png -delete')
        
    def setUp(self):
        """Инициализация переменных для всех тестов"""
        self.profile = webdriver.FirefoxProfile()
        self.profile.set_preference("general.useragent.override", os.getenv('USERAGENT'))
        self.stat = 0
        self.cat_url = os.getenv('CATINNER').split(',')#создаем список из aliasов которые будем просматривать
        HOST = os.getenv('HOST')
        PORT = os.getenv('PORT')
        SCHEMA = os.getenv('SCHEMA')
        USER = os.getenv('USER')
        PSWD = os.getenv('PSWD')
        DOMAIN = (os.getenv('DOMAIN')).decode('utf-8', 'ignore')
        self.CITY = (os.getenv('CITY')).decode('utf-8', 'ignore')
        self.ADRESS = 'http://%s.%s/' % (self.CITY, DOMAIN)
        CONNECT_STRING = 'mysql://%s:%s@%s:%s/%s?charset=utf8' %(USER, PSWD, HOST, PORT, SCHEMA)
        engine = create_engine(CONNECT_STRING, echo=False) #Значение False параметра echo убирает отладочную информацию(запросы)
        metadata = MetaData(engine)
        self.session = create_session(bind = engine)

    def tearDown(self):
        """Удаление переменных для всех тестов. Остановка приложения"""
        if sys.exc_info()[0]:   
            print sys.exc_info()[0]

    def common_signs(self, driver):
        """ общие для всех страниц признаки """
  
        driver.maximize_window()
        
        print driver.current_url
        try: # проверяем наличие кнопки назад
            driver.find_element_by_link_text('Назад')
        except:
            self.stat += 1
            print 'Отсутствует кнопка назад'
            
        try: # проверяем наличие ссылок на соц. сети в футере
            driver.find_element_by_class_name('social')
        except:
            pass
        else:
            self.stat += 1
            print 'Есть ссылки на соц. сети в футере'

        try: # проверяем наличие ссылки "вакансии" в нижнем меню
            driver.find_element_by_partial_link_text('Вакансии')
        except:
            pass
        else:
            self.stat += 1
            print 'В нижнем меню есть ссылка "Вакансии"'

        try: # проверяем наличие ссылки "обратная связь" в нижнем меню
            driver.find_element_by_partial_link_text('Обратная связь')
        except:
            pass
        else:
            self.stat += 1
            print 'В нижнем меню есть ссылка "Обратная связь"'

        try: # проверяем наличие ссылки "ВКонтакте" в нижнем правом углу страницы
            driver.find_element_by_class_name('vk')
        except:
            pass
        else:
            self.stat += 1
            print 'В нижнем правом углу страницы есть ссылка на "ВКонтакте"'

    

    def test_tv_0(self):
        """ тестирование главной страницы """
        self.stat = 0

        driver = webdriver.Firefox(self.profile)

        driver.get(self.ADRESS)
        self.common_signs(driver)
        driver.close()
        
        assert self.stat==0, (u'Errors:%d')%(self.stat)

    def test_tv_1(self):
        """ тестирование каталожной """
        self.stat = 0
        
        driver = webdriver.Firefox(self.profile)
                
        for url in self.cat_url:
            driver.get('%scatalog/%s/?perPage=60' % (self.ADRESS, url))
            
            self.common_signs(driver)
            
            try:
                f_text = driver.find_element_by_class_name('part').find_element_by_tag_name('label').text
                if f_text != u'В наличии в этом магазине':
                    self.stat += 1
                    print 'На каталожной %s нет фильтра "В наличии в этом магазине"' % url
            except:
                self.stat += 1
                print 'Страница %s окрылась некорректно, либо фильтра на странице нет' % url

            try:
                status =[x.text for x in driver.find_elements_by_class_name('stWareHouse')]
                if u'в других магазинах' not in status:
                    self.stat += 1
                    print 'На странице %s нет товаров со статусом "В других магазинах"' % url
            except:
                self.stat += 1
                print 'Невозможно получить статус товара'

            print '-'*80
                
        driver.close()
        
        assert self.stat==0, (u'Errors:%d')%(self.stat)

    def test_tv_2(self):
        """ тестирование карточки товара """
        self.stat = 0
        
        item = self.session.query(Goods.alias).\
               join(Goods_stat, Goods.id == Goods_stat.goods_id).\
               join(Region, Goods_stat.city_id == Region.id).\
               join(Goods_block, Goods.block_id == Goods_block.id).\
               filter(Region.domain == self.CITY).\
               filter(Goods_stat.status == 1).\
               first()
        
        driver = webdriver.Firefox(self.profile)
   
        driver.get('%sproduct/%s/' % (self.ADRESS, item[0]))
        self.common_signs(driver)
        try:
            driver.find_element_by_class_name('sharing')
        except:
            pass
        else:
            self.stat += 1
            print 'Присутствует "Поделиться" от Яндекс на странице товара', item[0]

        
        driver.close()

        assert self.stat==0, (u'Errors:%d')%(self.stat)

    def test_tv_3(self):
        """ тестирование страницы новостей """
        self.stat = 0

        driver = webdriver.Firefox(self.profile)
             
        driver.get('%snews/' % self.ADRESS)
        driver.find_element_by_class_name('bookmark').click()
        self.common_signs(driver)
        
        try:
            driver.find_element_by_class_name('sharing')
        except:
            pass
        else:
            self.stat += 1
            print 'На странице новости есть "Поделиться" от Яндекс'
                    
        driver.close()

        assert self.stat==0, (u'Errors:%d')%(self.stat)

    def test_tv_4(self):
        """ Тестирование страницы после заказа и сообщения на ней """
        self.stat = 0

        store_shop = self.session.query(Shops.db_sort_field).\
                        join(Region, Shops.city_id == Region.id).\
                        filter(Shops.active == 1).\
                        filter(Shops.flag_store_shop_kbt == 1).\
                        filter(Region.domain == self.CITY).\
                        first()
        if store_shop != None:
            store_shop = store_shop[0]
        else:
            store_shop = self.session.query(Shops.db_sort_field).\
                         filter(Shops.id == self.session.query(Region.supplier_id).filter(Region.domain == self.CITY).first()[0]).\
                         first()[0]
      
              
        item = self.session.query(Goods.alias).\
               join(Goods_stat, Goods.id == Goods_stat.goods_id).\
               join(Region, Goods_stat.city_id == Region.id).\
               join(Goods_block, Goods.block_id == Goods_block.id).\
               join(Goods_price, Goods.id == Goods_price.goods_id ).\
               join(Remains, Remains.goods_id == Goods.id).\
               filter(Region.domain == self.CITY).\
               filter(Goods_stat.status == 1).\
               filter(Goods.overall_type == 0).\
               filter(Goods_block.delivery_type == 1).\
               filter(Goods_price.price_type_guid == Region.price_type_guid).\
               filter(Goods_price.price > 2000).\
               filter('t_goods_remains.%s > 0' % store_shop).\
               first()

        driver = webdriver.Firefox(self.profile)

        driver.get('%slogin/' % self.ADRESS)
        driver.find_element_by_id('username').send_keys(os.getenv('AUTH'))
        driver.find_element_by_id('password').send_keys(os.getenv('AUTHPASS'))
        driver.find_element_by_class_name('btn-primary').click()
        time.sleep(5)

        driver.get('%sproduct/%s/' % (self.ADRESS, item[0]))#ссылка на карточку товара, который будет добавлен в корзину
        driver.find_element_by_link_text('Купить').click()
        time.sleep(5)
        driver.get('%sbasket/' % self.ADRESS)
        time.sleep(5)
  
        try:# проверка на то, есть ли ссылка на дополнение адреса из профиля Яндекс
            driver.find_element_by_css_selector("div.dcityContainer > span.radio").click()
            driver.find_element_by_class_name('control-group_address').find_element_by_tag_name('a')
            self.stat += 1
            print 'В корзине присутствует ссылка на дополнение адреса из профиля Яндекс'
        except:
            pass
                
        driver.find_element_by_id('personal_order_form_comment').send_keys('AutoTEST ORDER - TerminalVersion signs script')
        driver.find_element_by_class_name('btn-primary').click() #Покупаем товар
        
        try:
            driver.find_element_by_class_name('order-details')
        except:
            print 'Ошибка оформления заказа'
            driver.get_screenshot_as_file('screen.png')
            self.stat += 1

        print driver.current_url
        try: # проверяем наличие ссылок на соц. сети в футере
            driver.find_element_by_class_name('social')
        except:
            pass
        else:
            self.stat += 1
            print 'Есть ссылки на соц. сети в футере'

        try: # проверяем наличие ссылки "вакансии" в нижнем меню
            driver.find_element_by_partial_link_text('Вакансии')
        except:
            pass
        else:
            self.stat += 1
            print 'В нижнем меню есть ссылка "Вакансии"'

        try: # проверяем наличие ссылки "обратная связь" в нижнем меню
            driver.find_element_by_partial_link_text('Обратная связь')
        except:
            pass
        else:
            self.stat += 1
            print 'В нижнем меню есть ссылка "Обратная связь"'

        try: # проверяем наличие ссылки "ВКонтакте" в нижнем правом углу страницы
            driver.find_element_by_class_name('vk')
        except:
            pass
        else:
            self.stat += 1
            print 'В нижнем правом углу страницы есть ссылка на "ВКонтакте"'

        try: # проверяем наличие виджета "ВКонтакте" справа от информации о заказе
            driver.find_element_by_id('vk_groups')
        except:
            pass
        else:
            self.stat += 1
            print 'Cправа от информации о заказе есть виджет "ВКонтакте"'
        
        
        try:
            WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.ID, 'logout'))) # Ждем когда сообщение появится
            driver.get_screenshot_as_file('logout.png')
                
        except: 
            print 'Отсутствует сообщение об автовыходе'
            self.stat += 1
            
        
        driver.get('%slogout' % self.ADRESS) ######## DO NOT FORGET TO PRESS LOGOUT ########
        driver.close()

        assert self.stat==0, (u'Errors:%d')%(self.stat)




