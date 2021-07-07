# driver 在夜间不动的时候容易假死，记得用咖啡因！
# '''
# This example demonstrates a simple use of pycallgraph.
# '''
# from pycallgraph import PyCallGraph
# from pycallgraph.output import GraphvizOutput

import selenium
import re

from selenium import webdriver
from selenium.webdriver.firefox.options import Options


# 解决点不动的问题
# https://stackoverflow.com/questions/21350605/python-selenium-click-on-button

from selenium.webdriver.support.ui import WebDriverWait

# 一出现就马上点，这个操作好啊！！！

# https://stackoverflow.com/questions/62868434/button-click-only-works-when-time-sleep-added-for-selenium-python
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

import os
import sys

import time

from yals import open_one_link
from yals import fill_in_blanks

book_dir=r"D:\AllDowns\newbooks"

already_path=r"D:\AllDowns\upload_results\uploadYet.txt"

fail_path=r"D:\AllDowns\upload_results\uploadFailYet.txt"

if not os.path.exists(already_path):
    open(already_path,"w").close()


firefox_path=r"C:\Program Files\Mozilla Firefox\geckodriver.exe"
options = Options()
# options.headless = True
options.headless=False



# proxy="127.0.0.1:10086"
# proxy="120.232.193.208:10087"

# 注意：你用http的时候要开启http全局代理（v2rayN红色图标）！！

proxy="127.0.0.1:10087"

options.add_argument(f"--proxy-server=http:{proxy}")

driver=webdriver.Firefox(options=options,executable_path=firefox_path)

# proxies = {
#     'https': 'https://127.0.0.1:64708',  # 查找到你的vpn在本机使用的https代理端口
#     'http': 'http://127.0.0.1:64708',  # 查找到vpn在本机使用的http代理端口
# }

# 换用chrome好了，还是更喜欢chrome一些些...

# driver=webdriver.Chrome(executable_path=r"C:\Users\linsi\AppData\Local\CentBrowser\Application\chromedriver.exe")

# chrome_path=


max_delay=10

cnt=0

def cap_num(some_num):
    # 注意，这里我们只预留到十，也就是说，十一以上的全部都得给我用阿拉伯数字！！！
    caps=["零","一","二","三","四","五","六","七","八","九","十"]
    for num,cap in enumerate(caps):
        if num==some_num:
            return cap

def find_element_by_xpath2(patt):
    try:
        res=WebDriverWait(driver,max_delay).until(EC.presence_of_element_located((By.XPATH, patt)))
    except selenium.common.exceptions.TimeoutException:
        res=""
    return res

def upload_one_book(book_path,book_isbn):
    # book_path=r"C:\Users\linsi\Desktop\Java Printing.pdf"

    # 恋姬无双，这个https://book.douban.com/subject/20434394/
    # book_isbn="9787511330963"

    auth_str="genesis:upload"
    main_upload_url=f"https://{auth_str}@library.bz/main/upload/"

    driver.get(main_upload_url)

    # 这个太好用了...
    # https://stackoverflow.com/questions/62868434/button-click-only-works-when-time-sleep-added-for-selenium-python

    xuanzewenjianBtn=find_element_by_xpath2("//input[@type='file']")

    # https://www.jianshu.com/p/fba37cc5d5e2
    # input标签是可以直接send_keys的...

    xuanzewenjianBtn.send_keys(book_path)

    uploadBtn=find_element_by_xpath2("//input[@type='submit']")
    uploadBtn.click()

    upload_new_checker="https://library.bz/main/uploads/new/"
    upload_new_checker2=f"https://{auth_str}@library.bz/main/uploads/new/"

    submit_checker="edit"


    while True:
        cur_url=driver.current_url
        # print(cur_url)
        # print(cur_url)
        if cur_url.startswith(upload_new_checker) or cur_url.startswith(upload_new_checker2):
            # print("good.")
            break
        if driver.find_elements_by_class_name("form_error"):
            print("already.")
            with open(already_path,"a",encoding="utf-8") as f:
                f.write(book_path+"\n")
            return 

    # # 新建一个不用代理的...

    # driver.quit()

    # options = Options()
    # options.headless = True
    # # # options.headless=False

    # # # proxy="root:G5q]3kDDuQxWN4xv@137.220.42.229:10086"

    # # # options.add_argument(f"--proxy-server=sock5:{proxy}")

    # driver=webdriver.Firefox(options=options,executable_path=firefox_path)

    # with auth
    upload_new_url=driver.current_url.replace("//library.bz",f"//{auth_str}@library.bz")
    print("upload new url",upload_new_url)

    new_dict=open_one_link(driver,book_isbn)
    print("final pack:", new_dict)
    if new_dict=={}:
        print(f"Failed:{book_path}")
        with open(fail_path,"a",encoding="utf-8") as f:
            f.write(book_path+"\n")
            f.write(upload_new_url+"\n\n")
        return 
    fill_in_blanks(driver,new_dict,upload_new_url)
    time.sleep(1)

    # if "第" in book_path and "卷" in book_path:
    #     formatted_bookpath=book_path.replace("")



    # 由于douban的fetch经常出问题（没fetch到作者等等问题...），
    
    # # 所以现在一律不使用douban-fetch的办法，自己爬豆瓣

    # selectBtn=find_element_by_xpath2("//select[@name='metadata_source']/option[@value='douban']")
    # selectBtn.click()

    # isbnInputBox=find_element_by_xpath2("//input[@name='metadata_query']")

    # if len(book_isbn)==13:
    #     isbnInputBox.send_keys(book_isbn)

    # fetchBtn=find_element_by_xpath2("//input[@value='Fetch']")
    # fetchBtn.click()

    # titleNode=find_element_by_xpath2("//input[@name='title']")
    # title=titleNode.get_attribute("value")

    

    # if title!="":

    #     langNode=find_element_by_xpath2("//input[@name='language']")
    #     myLang="中文"
    #     langNode.send_keys(myLang)

    #     ori_descriptionNode=find_element_by_xpath2("//textarea[@name='description']")
    #     ori_description=ori_descriptionNode.text
    #     mywords="\n\n书签已装载，\n书签制作方法请找 yjyouaremysunshine@163.com\n完全免费\n（若有印刷不清等问题也请发送相关邮件，会尽快更新的）\n\n"
    #     description=mywords+ori_description
    #     ori_descriptionNode.clear()
    #     ori_descriptionNode.send_keys(description)
    #     # time.sleep(1)
    # else:
    #     new_dict=open_one_link(driver,book_isbn)
    #     print("final pack:", new_dict)
    #     if new_dict=={}:
    #         print(f"Failed:{book_path}")
    #         with open(fail_path,"a",encoding="utf-8") as f:
    #             f.write(book_path+"\n")
    #             f.write(upload_new_url+"\n\n")
    #         return 
    #     fill_in_blanks(driver,new_dict,upload_new_url)
    #     time.sleep(1)

    # if "第" in book_path and "卷" in book_path:
    #     formatted_bookpath=book_path.replace("")

    volume_list=re.findall("第(\d{1,2})卷",book_path)
    if volume_list and volume_list[0].isdigit():
        volume=volume_list[0]
        print("has volume:",volume)
        volumeBox=find_element_by_xpath2("//input[@name='volume']")
        volumeBox.send_keys(volume)
        print("volume attached.")


    final_submitBtn=find_element_by_xpath2("//input[@value='SUBMIT!']")
    final_submitBtn.click()
    time.sleep(1)
    cur_url=driver.current_url

    if submit_checker in cur_url:
        print("one success.")

    with open(already_path,"a",encoding="utf-8") as f:
        f.write(book_path+"\n")

        # time.sleep(15)

def main():
    books=sorted(os.listdir(book_dir),key=lambda x: os.path.getmtime(os.path.join(book_dir, x)),reverse=True)
    books=[book for book in books if book.endswith(".pdf")]

    with open(already_path,"r",encoding="utf-8") as f:
        already_books=f.readlines()
    
    with open(fail_path,"r",encoding="utf-8") as f:
        already_books.extend(f.readlines())
    
    already_books=set(already_books)

    for each_book in books:
        if "isbnisbn" in each_book:
            each_bookname,each_isbn=each_book.split("isbnisbn")
        elif "dbdb" in each_book:
            each_bookname,each_isbn=each_book.split("dbdb")
        each_isbn=each_isbn.strip(".pdf")
        each_bookpath=f"{book_dir}{os.sep}{each_book}"
        # 防止你最后一行...
        if each_bookpath+"\n" in already_books or each_bookpath in already_books:
            print("already:",each_bookpath)
            continue
        startAt=time.time()
        upload_one_book(each_bookpath,each_isbn)
        endAt=time.time()
        print("Run time:",endAt-startAt)
        global cnt
        cnt+=1
        if cnt%250==0:
            global driver
            driver.quit()
            print("reflesh!")
            driver=webdriver.Firefox(options=options,executable_path=firefox_path)


    print("all done.")

    driver.quit()

if __name__ == '__main__':
    main()
    # graphviz = GraphvizOutput()
    # graphviz.output_file = r'D:\AllDowns\upload_results\basiccccc.png'
    # with PyCallGraph(output=graphviz):
    #     main()