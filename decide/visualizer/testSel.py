
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from base.tests import BaseTestCase
# Generated by Selenium IDE
from selenium.webdriver.common.by import By

class AdminTestCase(StaticLiveServerTestCase):
    #Test Selenium Vistas Login
    def setUp(self):    
        self.base=BaseTestCase()
        self.base.setUp()
        options = webdriver.ChromeOptions()
        options.headless = True
        self.driver=webdriver.Chrome(options=options)
        self.vars={}
        super().setUp()                 
    def tearDown(self):           
        super().tearDown()
        self.driver.quit()
        self.base.tearDown()
    def test_simpleCorrectLogin(self):                    
        self.driver.get(f'{self.live_server_url}/admin/')
        self.driver.find_element(By.ID,'id_username').send_keys("admin")
        self.driver.find_element(By.ID,'id_password').send_keys("qwerty",Keys.ENTER)
        print(self.driver.current_url)
        self.assertTrue(len(self.driver.find_elements(By.ID,'user-tools'))==1)
    #Test Selenium Login y paginacion pag siguiente
    def test_pagAnterior(self):
        self.driver.get(f'{self.live_server_url}/admin/')
        self.driver.find_element(By.ID,'id_username').send_keys("admin")
        self.driver.find_element(By.ID,'id_password').send_keys("qwerty",Keys.ENTER)
        self.driver.get(f'{self.live_server_url}/visualizer/')
        self.driver.set_window_size(1260, 1457)
        self.driver.execute_script("Pager()") 
        element=self.driver.find_element(By.CSS_SELECTOR, ".pg-normal:nth-child(1)").click()  
        if element:
            print("Elemento encontrado")
        else:
            print("Elemento no encontrado")