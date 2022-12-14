import os
import re
import time
import queue
import pyfiglet

from threading import Thread

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import (
    StaleElementReferenceException,
    JavascriptException
)

from modules.buildings import Buildings

class King(object):
    def __init__(self, save_path: str = "") -> None:
        # Constructor variables
        self.save = save_path
        
        # Queues
        self.clicker_queue = queue.Queue()
        
        # Driver
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service)         
        self.driver.get('http://orteil.dashnet.org/cookieclicker/')
        os.system('cls' if os.name=='nt' else 'clear')
        print(pyfiglet.figlet_format("Cookie Clicker Automation SEX"))        
        
        # Select language
        try:        
            lang = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, '//div[@class="langSelectButton title"]'))
            )

        except:
            self.driver.quit()
            
        lang.click()

        # Load save
        if self.save:
            with open(self.save, 'r+') as file:
                self.save = file.read()
                
            self.__load_save()
        
        self.buildings = Buildings(self.driver, self.clicker_queue)
        self.__start_worker_clicker()
        self.__thread_save_data()

    def __load_save(self):
        cond = self.driver.execute_script('return Game.bakeryName ')
        while True:
            try:
                self.driver.execute_script(f'Game.ImportSaveCode("{self.save}")')
                break
        
            except JavascriptException: 
                print("Can't load save, trying again in 0.5s")
            
            time.sleep(0.5)
    
    def __start_worker_clicker(self):
        def cookie_clicker_worker():
            while True:
                if self.clicker_queue.empty():
                    try:
                        self.driver.execute_script('Game.ClickCookie()')
                    except JavascriptException:
                        print("Error - Cookie not found")
                        
                else:
                    work = self.clicker_queue.get()
                    self.driver.execute_script(f'Game.{work}.buy()')
                    
                    # except:
                    #     print(f"ATTENTION: Couldn't click {work}")
                        
                    self.clicker_queue.task_done()
                    
                time.sleep(0.01)

        thread = Thread(target=cookie_clicker_worker, args=(), daemon=True)
        thread.start() 

    def __thread_save_data(self):
        def save_data():
            while True:
                save = self.driver.execute_script('return Game.WriteSave(1)')
                file_path = os.path.join('.', 'local_save.txt')
                with open(file_path, 'w+') as file:
                    file.write(save)
                
                time.sleep(60)

        thread = Thread(target=save_data, args=(), daemon=True)
        thread.start() 
        
    def kill(self):
        self.driver.quit()
    
    def buildings(self):
        return self.buildings
     