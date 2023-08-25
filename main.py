from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

from flask import Flask, render_template, request, jsonify
from flask_cors import CORS, cross_origin
import pandas as pd
import pymongo
import time
import sys
import csv

import logging
logging.basicConfig(filename='YTWebScrapper.log',level=logging.DEBUG,format= '%(asctime)s - %(name)s - %(levelname)s - %(message)s')


app = Flask(__name__)

# Route to display the Home Page

@app.route("/", methods= ['GET','POST'])
@cross_origin()
def homepage():
    logging.info('Successfully Landed on Home Page')
    return render_template('index.html')




@app.route("/ytdata",methods = ['GET','POST'])
@cross_origin()
def yt_data():
    if request.method == 'POST':
        
        url = request.form['content']
        f = f"https://www.youtube.com/@{url}/videos"
        df = selenium_method(f)
        
        
        return render_template('result.html', tables = [df.to_html()], titles =[''])
    
    
def selenium_method(url):
    PATH = Service(executable_path='./chromedriver.exe')
    driver = webdriver.Chrome(service=PATH)
    driver.get(url)
    driver.maximize_window()
    time.sleep(4)
    
    
    video_urls = []
    img_links = []
    title_text = []
    views_exact = []
    dates = []
    
    
    
    # Getting Vedio URL
    video_link = driver.find_elements(By.XPATH ,"//*[@id='video-title-link']")
    links = video_link[0:5]
    for i in links:
        link = i.get_attribute('href')
        video_urls.append(link)
    
    
    # Getting Thumbnails Links
    driver.execute_script("window.scrollTo(0,200)")
    time.sleep(2)
    images = driver.find_elements(By.XPATH,"//*[@class='yt-core-image--fill-parent-height yt-core-image--fill-parent-width yt-core-image yt-core-image--content-mode-scale-aspect-fill yt-core-image--loaded']")
    for i in images:
        image = i.get_attribute('src')
        img_links.append(image)
    top5thumbnails = img_links[0:5]
    
    
    # Getting Titles Text
    titles = driver.find_elements(By.XPATH, "//*[@id='video-title']")
    for i in titles:
        title_text.append(i.text)
    top5titles = title_text[0:5]
    
    
    for i in video_urls:
        new_url = i
        driver.execute_script('window.open('');')
        
        driver.switch_to.window(driver.window_handles[1])
        driver.get(new_url)
        time.sleep(2)
        
        show_more = driver.find_element(By.ID,"expand")
        show_more.click()
        
        all_views = driver.find_element(By.XPATH,"/html/body/ytd-app/div[1]/ytd-page-manager/ytd-watch-flexy/div[5]/div[1]/div/div[2]/ytd-watch-metadata/div/div[4]/div[1]/div/div[1]/yt-formatted-string/span[1]")
        views = all_views.text
        views_exact.append(views)
        
        
        post_date = driver.find_element(By.XPATH,"/html/body/ytd-app/div[1]/ytd-page-manager/ytd-watch-flexy/div[5]/div[1]/div/div[2]/ytd-watch-metadata/div/div[4]/div[1]/div/div[1]/yt-formatted-string/span[3]")
        video_date =post_date.text
        dates.append(video_date)
        
        driver.close()
        driver.switch_to.window(driver.window_handles[0])

    driver.get(url)
    
    
    
    
    dct_final = {'URL': video_urls, 'Title':top5titles, 'Thumbnails': top5thumbnails,'Views':views_exact, 'Dates': dates}
    
    df_final = pd.DataFrame(dct_final)
    
    
    
    return(df_final)


if __name__ == '__main__':
    app.run(host = '127.0.0.1', port=8000, debug=True)