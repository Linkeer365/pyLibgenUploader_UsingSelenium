import selenium

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

if not os.path.exists(already_path):
    open(already_path,"w").close()


firefox_path=r"C:\Program Files\Mozilla Firefox\geckodriver.exe"

options = Options()
# options.headless = True
options.headless=False

driver=webdriver.Firefox(options=options,executable_path=firefox_path)

max_delay=5

def upload_one_book(book_path,book_isbn):
    # book_path=r"C:\Users\linsi\Desktop\Java Printing.pdf"

    # 恋姬无双，这个https://book.douban.com/subject/20434394/
    # book_isbn="9787511330963"

    auth_str="genesis:upload"
    main_upload_url=f"https://{auth_str}@library.bz/main/upload/"

    def find_element_by_xpath2(patt):
        return WebDriverWait(driver,max_delay).until(EC.presence_of_element_located((By.XPATH, patt)))

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

    submit_checker="edit"


    while True:
        cur_url=driver.current_url
        if cur_url.startswith(upload_new_checker):
            break

    # with auth
    upload_new_url=driver.current_url.replace("//library.bz",f"//{auth_str}@library.bz")
    print("upload new url",upload_new_url)

    selectBtn=find_element_by_xpath2("//select[@name='metadata_source']/option[@value='douban']")
    selectBtn.click()

    isbnInputBox=find_element_by_xpath2("//input[@name='metadata_query']")
    isbnInputBox.send_keys(book_isbn)

    fetchBtn=find_element_by_xpath2("//input[@value='Fetch']")
    # fetchBtn.click()

    titleNode=find_element_by_xpath2("//input[@name='title']")
    title=titleNode.get_attribute("value")

    if title!="":

        langNode=find_element_by_xpath2("//input[@name='language']")
        myLang="中文"
        langNode.send_keys(myLang)

        ori_descriptionNode=find_element_by_xpath2("//textarea[@name='description']")
        ori_description=ori_descriptionNode.text
        mywords="\n\n书签已装载，\n书签制作方法请找 yjyouaremysunshine@163.com\n完全免费\n（若有印刷不清等问题也请发送相关邮件，会尽快更新的）\n\n"
        description=mywords+ori_description
        ori_descriptionNode.clear()
        ori_descriptionNode.send_keys(description)
        # time.sleep(1)
    else:
        new_dict=open_one_link(driver,book_isbn)
        print("final pack:", new_dict)
        fill_in_blanks(driver,new_dict,upload_new_url)
        time.sleep(2)

    final_submitBtn=find_element_by_xpath2("//input[@value='SUBMIT!']")
    final_submitBtn.click()
    time.sleep(5)
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
        already_books=set(f.readlines())

    for each_book in books:
        assert "isbnisbn" in each_book
        each_bookname,each_isbn=each_book.split("isbnisbn")
        each_bookpath=f"{book_dir}{os.sep}{each_bookname}"
        if each_bookpath+"\n" in already_books:
            print("already:",each_bookpath)
            continue
        upload_one_book(each_bookpath,each_isbn)

    print("all done.")

    driver.quit()

if __name__ == '__main__':
    main()