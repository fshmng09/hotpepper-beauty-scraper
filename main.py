import os
import time
import random
import pandas as pd
import numpy as np
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)

class HotpepperBeautyScraper():
  
  def __init__(self):
    self.pageLimit = 20
    self.colLimit = 20
    self.place="harajuku"
    self.baseUrl="https://beauty.hotpepper.jp/svcSA/stc0570060/PN"
  
  def setup_method(self, method):
    self.driver = webdriver.Chrome()
    self.vars = {}
  
  def click(self, element):
    element.click()
    time.sleep(random.randint(1, 2) / 2.)
  
  def back(self):
    self.driver.back()
    time.sleep(random.randint(1,2) / 2.)
  
  def teardown_method(self, method) -> None:
    self.driver.quit()
  
  def get_store_name(self, colNum) -> str:
    return self.driver.find_element(By.CSS_SELECTOR, f"li:nth-child({colNum}) .slnName > a").text
    
  def jump_to_store_page(self, colNum: int):
    self.vars["StoreName"] = self.get_store_name(colNum)
    self.click(self.driver.find_element(By.LINK_TEXT, self.vars["StoreName"]))

  def get_store_info(self, colNum: int) -> str:
    self.jump_to_store_page(colNum)
    self.vars["url"]=self.driver.current_url
    self.click(self.driver.find_element(By.LINK_TEXT, "番号を表示"))
    self.vars["PhoneNumber"] = self.driver.find_element(By.CSS_SELECTOR, ".fs16").text
    
    self.back()
    self.back()

    return self.vars["PhoneNumber"]

  def run(self):
    result_df = pd.DataFrame([],
                    columns=['StoreName', 'PhoneNumber', 'url'],
                    index=[])
    temp_pickle = f"./{self.place}_tmp.pickle"
    if os.path.exists(temp_pickle):
      result_df = pd.read_pickle(temp_pickle)

    self.driver.get(f"{self.baseUrl}1.html")
    for pageNum in range(self.pageLimit):
      self.driver.set_window_size(1200, 950)
      for colNum in range(self.colLimit):

        # 中断した場合、途中から再開
        if pageNum * self.pageLimit + colNum + 1 < len(result_df):
          continue;
        
        print(f"{pageNum}-{colNum}") #進捗確認
        self.get_store_info(colNum + 1)
        result_df = result_df.append({**self.vars}, ignore_index=True)
        result_df.to_pickle(temp_pickle)
      self.driver.get(f"{self.baseUrl}{pageNum + 2}.html")
      time.sleep(random.randint(1, 2) / 2.)
    result_df.drop_duplicates.to_csv(f"./{self.place}_summary.csv")

if __name__ == "__main__":
  scraper = HotpepperBeautyScraper()
  scraper.setup_method(())
  scraper.run()