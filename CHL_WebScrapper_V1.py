#!/usr/bin/python
# -*- coding: utf-8 -*-

# loading the libraries
from lib2to3.pgen2 import driver
from turtle import title
import requests
from datetime import  datetime,timedelta
from bs4 import BeautifulSoup
from dateparser import parse
import pandas as pd
import json
import configparser
import time
import re
import pandas as pd

import os,time,sys
#Custom Modules
from constants.arg_constants import IDENS, DOMAIN, SITE_NAME
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium import webdriver
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.firefox.service import Service
from helpers.exceptions import DriverInitiliazeError
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from helpers.DTranslatorV3 import sendlist, set_driver
from helpers.dateHandler import parseDate
from googletrans import Translator
from nltk import tokenize
import datetime
from PIL import Image
import pytesseract 


#Logging
import logging
logging.basicConfig(handlers=[logging.StreamHandler(sys.stdout)],level=logging.INFO)
logger=logging.getLogger("arg")


class Arg:
    def __init__(self) -> None:
        self.config = configparser.ConfigParser()
        self.config.read('config.ini')
        self.scrape_options = self.config['SCRAPE_OPTIONS']
        self.base_config = self.config['BASE_CONFIG']
        self.driver_path = self.base_config['GECKODRIVER_PATH']
        self.headless = eval(self.base_config['HEADLESS'])
        self.outputPath = self.base_config['EXPORT_DIR']
        # self.pytesseract_path=self.base_config['pytesseract_path']
        # print('pytesseract_path :-',self.pytesseract_path)
        ###############################################
        self.__fetch_delay=5

    def scrape(self):
        """
        Begin overall scraping process
        """
        try:

            self.driver = self.initialize_driver()
#            self.driver2 = set_driver(self.driver_path)
            results_2 = self.fetch_data_1()
            df = self.export_df(results_2)
            self.export_csv(df,self.outputPath,"chl")
            self.export_json(results_2,self.outputPath,"chl")
            self.driver.close()
        finally:
            try:
                self.driver.close()
            except:
                pass

    def fetch_data_1(self):

        # Getting the data
        # self.driver.execute_script("window.scrollTo(0, 200)")
        # time.sleep(2)
        print('')
        from_date_value = parseDate(self.scrape_options['FROM_DATE']).date()
        from_date_value_1 = datetime.datetime.strptime(str(from_date_value),'%Y-%m-%d').strftime('%d/%m/%Y')
        print('From Date :- ',from_date_value_1)
        print('')
        from_date_1 = self.format_dateValue_3(from_date_value_1)

        time.sleep(20)

        # Switching to frame
        self.driver.switch_to.frame("form-iframe")
        time.sleep(2)
        
        WebDriverWait(self.driver, 30).until(EC.presence_of_element_located((By.XPATH,'''(//input[@class='checkbox'])[2]''')))
        popup_1_close=self.driver.find_element(By.XPATH,"(//input[@class='checkbox'])[2]")
        popup_1_close.click()
        time.sleep(4)

        # clicking to get data based on last published date
        WebDriverWait(self.driver, 30).until(EC.presence_of_element_located((By.XPATH,'''//select[@id='ordenarpor']''')))
        popup_2_close=self.driver.find_element(By.XPATH,"//select[@id='ordenarpor']")
        popup_2_close.click()
        time.sleep(4)
        WebDriverWait(self.driver, 30).until(EC.presence_of_element_located((By.XPATH,'''//*[contains(text(),'Últimas publicadas')]''')))
        popup_2_close=self.driver.find_element(By.XPATH,"//*[contains(text(),'Últimas publicadas')]")
        time.sleep(1)
        popup_2_close.click()
        time.sleep(4)
        
        Final_data=[]
        page_no=1
        scraping=True
        while True:
                
                soup = BeautifulSoup(self.driver.page_source, 'lxml')
                postings = soup.find_all('div',{'class':'responsive-resultado'})

                


                for post in postings:


                    try:
                        
                        # Publication_date = post.find_all('span',{'class':'highlight-text text-weight-light'})[1].text.strip()
                        Publication_date = post.find_all('div',{'class':'col-md-4'})[1].find('span').text.strip()
                        Published_date_1=self.format_dateValue_3(str(Publication_date))                    
                        print('From Date :-',from_date_value_1)
                        print('Published_date:-',Publication_date)

                        if Published_date_1 >= from_date_1:

                            try:
                                id = post.find('span',{'class':'clearfix'}).text.strip()
                            except:
                                id=''
                                
                            try:
                                Title = post.find('h2',{'class':'text-weight-light'}).text.strip()
                            except:
                                Title=''
                                
                            try:
                                Description = post.find('p',{'class':'text-weight-light'}).text.strip()
                            except:
                                Description=''
                                
                            try:
                                Description = post.find('p',{'class':'text-weight-light'}).text.strip()
                            except:
                                Description=''
                                
                            try:
                                Amount_available = post.find('div',{'class':'monto-dis col-md-4'}).find_all('span')
                                Amount_available_1 = [ i.text.strip()  for i in Amount_available]
                                Amount_available_2  = ' '.join(Amount_available_1)
                                if 'Entre' in Amount_available_2:
                                    Amount_available_2=self.translate_single_element(Amount_available_2)

                                else:
                                    pass

                            except:
                                Amount_available_2=''
                                
                            try:
                                Publication_date = post.find_all('div',{'class':'col-md-4'})[1].find('span').text.strip()
                            except:
                                Publication_date=''
                                
                            try:
                                Deadline= post.find_all('div',{'class':'col-md-4'})[2].find('span').text.strip()

                            except:
                                Deadline=''
                                
                            try:
                                Agency_name = post.find_all('div',{'class':'col-md-4'})[3].find('p').text.strip()

                            except:
                                Agency_name=''
                                
                            try:
                                Amount_of_purchases_made = post.find_all('div',{'class':'col-md-4'})[4].find('span').text.strip()

                            except:
                                Amount_of_purchases_made =''
                                
                            try:
                                Number_of_claims_for_non_timely_payment =  post.find_all('div',{'class':'col-md-4'})[5].find('span').text.strip()

                            except:
                                Number_of_claims_for_non_timely_payment=''
                                
                            try:
                                url = post.find('a').get('onclick')

                                url_1 = url.replace("$.Busqueda.verFicha('","")
                                url_2 = url_1.replace("')","")
                                
                            except:
                                url_2=''
                                
                                
                            data_dict={}
                            data_dict['ID']=id
                            data_dict['Title']=self.translate_single_element(Title)
                            data_dict['Description']=self.translate_single_element(Description)
                            data_dict['Publication Date']=Publication_date
                            data_dict['Deadline']=Deadline
                            data_dict['Agency Name']=self.translate_single_element(Agency_name)
                            data_dict['Amount Available']=Amount_available_2
                            data_dict['Amount of Purchases Made']=Amount_of_purchases_made
                            data_dict['Number of claims for non timely payment']=Number_of_claims_for_non_timely_payment
                            data_dict['Link']=url_2
                            



                            Final_data.append(data_dict)


                        else:
                            # print('Date not matched')
                            scraping=False
                            break

                    except Exception as e:
                        print('Error :-',e)
                        
                if scraping==False:
                    break



                try:

                    self.driver.switch_to.default_content()
                    time.sleep(2)
                    self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                    time.sleep(1)
                    self.driver.switch_to.frame("form-iframe")
                    time.sleep(2)
                    Next_Page=self.driver.find_element(By.XPATH,"//li[contains(text(),'>')]")
                    time.sleep(2)
                    Next_Page.click()
                    # print("")
                    # print("##############################")
                    print(f'We are on  page {page_no}')
                    # print("##############################")
                    # print("")
                    page_no+=1
                    time.sleep(4)                        

                except:
                    # scraping=False
                    time.sleep(2)
                    break
       
        print('')
        return(Final_data)



    

    def translate_list(self,data_new):
        translator = Translator()
        final_data = []
        for i in data_new:
                if len(i)==0:
                    final_data.append("")
                elif  len(i) >3000: 
                        final_text = []
                        final_text1= []
                        hj = tokenize.sent_tokenize(i)
                        for i in hj:
                                translated_text = translator.translate(i,src='es',dest='en')
                                final_text.append(translated_text.text)
                                final_text1 = ' '.join(final_text)
                        final_data.append(final_text1)
                else:
                    translated_text = translator.translate(i,src='es',dest='en')
                    final_data.append(translated_text.text) 
            

    def remove_esc_chars(self, text):
        """
        Remove all escape characters from text
        """
        return text.replace("\n", " ").replace("\t", " ").replace("\r", " ")


    


    
    def translate_single_element(self,single_element):
        translator = Translator()
        final_data = []
        if len(single_element)==0:
            final_data.append("")

        else:
            translated_text = translator.translate(single_element,src='es',dest='en') # change the src code according to your source data  language code
            final_data.append(translated_text.text) 


        return(final_data[0])


    def format_dateValue_3(self,date_str):
        """
        Set date in a given format
        """
        newdate1 = time.strptime(date_str, r"%d/%m/%Y")
        return newdate1


    def initialize_driver(self):
        """
        Initialize the driver with the given tender url
        """
        try:
            driver=self.driver_handler(driver_path=self.driver_path, headless=self.headless)
            driver.get(self.base_config['BASE_URL'])
            return driver
        except Exception as e:
            logger.error(e,stack_info=True,stacklevel=2)
            return None

    def export_df(self, output:list):
        """
        Convert the list of dictionaries into a dataframe
        """
        if len(output) != 0:
            try:
                df=pd.DataFrame(output)
                return df
            except:
                return pd.DataFrame()
        else:
            return pd.DataFrame()

    def export_csv(self, df:pd.DataFrame,outputPath:str,filename:str,sep:str='|'):
        """
        Convert the dataframe into a csv file
        """
        
        from datetime import datetime
        todaysdt=datetime.now().strftime(r'%d%m%y')
        filename=f'{filename}_{todaysdt}.csv'
        os.makedirs(outputPath,exist_ok=True)
        finalPath=f'{outputPath}/{filename}'
        if not df.empty:
            df.to_csv(finalPath,sep=sep, encoding="utf-8", index=False)
            logger.info(f'Exported to:{finalPath}')
        else:
            logger.info('No data to export as csv')

    def export_json(self, output:list,outputPath:str,filename:str):
        """
        Convert the list of dictionaries into a json file
        """
        from datetime import datetime
        todaysdt=datetime.now().strftime(r'%d%m%y')
        filename=f'{filename}_{todaysdt}.json'
        os.makedirs(outputPath,exist_ok=True)
        finalPath=f'{outputPath}/{filename}'
        if len(output) != 0:
            with open(finalPath,'w',encoding='utf-8') as f:
                json.dump(output,f,indent=4,ensure_ascii=False)
            logger.info(f'Exported to:{finalPath}')
        else:
            logger.info('No data to export as json')

    def parse_webpage_bs(self, search_url):
        """
        Parse webpage using requests and beautifulsoup
        """
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:90.0) Gecko/20100101 Firefox/90.0"}
        try:
            site_request = requests.get(search_url, headers=headers, timeout=40)
        except requests.exceptions.RequestException as e:
            print(e)
            site_request = None
        if site_request != None and site_request.status_code==200:
            site_soup = BeautifulSoup(site_request.content, "html.parser")
        else:
            site_soup = None
        return site_soup

    def driver_handler(self, driver_path:str=None,headless:bool=True):
        """
        Set all the driver preferences
        """
        if driver_path is None:
            raise DriverInitiliazeError('please add webdriver path')
        try:
            options=FirefoxOptions()
            options.set_preference("browser.download.folderList", 2)
            options.set_preference("browser.download.manager.showWhenStarting", False)
            options.set_preference("dom.push.enabled", False)
            options.set_preference('dom.webnotifications.enabled', False)
            options.headless=headless

            ffservice=Service(driver_path)
            driver=webdriver.Firefox(service=ffservice,options=options)
            driver.maximize_window()
            return driver
        except Exception as e:
            raise DriverInitiliazeError(e)





if __name__=="__main__":
    s=time.time()
    f=Arg()
    f.scrape()
    e=time.time()
    print(f'Took:{e-s}')

