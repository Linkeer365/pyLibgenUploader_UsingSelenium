import selenium
from selenium import webdriver
from selenium.webdriver.firefox.options import Options

from selenium.webdriver.support.ui import WebDriverWait

# 一出现就马上点，这个操作好啊！！！

# https://stackoverflow.com/questions/62868434/button-click-only-works-when-time-sleep-added-for-selenium-python
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

import os
import re
import time

import sys

firefox_path=r"C:\Program Files\Mozilla Firefox\geckodriver.exe"

options = Options()
# options.headless = True
options.headless=False

max_delay=15


# 这里是担心和主文件中的driver混起来，所以在这里也把driver也一并传进来了...

# def find_element_by_xpath2(driver,patt:str):
#     return WebDriverWait(driver,max_delay).until(EC.presence_of_element_located((By.XPATH, patt)))

def find_element_by_xpath2(driver,patt):
    try:
        res=WebDriverWait(driver,max_delay).until(EC.presence_of_element_located((By.XPATH, patt)))
    except selenium.common.exceptions.TimeoutException:
        res=""
    return res

def find_element_by_id2(driver,id:str):
    try:
        res=WebDriverWait(driver,max_delay).until(EC.presence_of_element_located((By.ID, id)))
    except selenium.common.exceptions.TimeoutException:
        res=""
    return res

def find_elements_by_xpath2(driver,patt:str):
    # 这句只是让他等待，它可以被赋值为第一个
    WebDriverWait (driver, max_delay).until (EC.presence_of_element_located ((By.XPATH, patt)))
    return driver.find_elements_by_xpath(patt)

def translate(new_str,old_str,new_dict,old_dict):
    try:
        new_dict[new_str]=old_dict[old_str]
    except KeyError:
        new_dict[new_str]=""


def info_formatter(names_vals:dict):
    new_dict={}

    # 统一书号（要显示在mywords和标题中）

    tongyishuhao_str=""

    if "统一书号" in names_vals.keys():
        tongyishuhao=names_vals["统一书号"]
        tongyishuhao_str=f"（统一书号：{tongyishuhao}）"


    # title

    if "副标题" in names_vals.keys():
        dabiaoti=names_vals["大标题"]
        fubiaoti=names_vals["副标题"]
        new_dict["title"]=f"{dabiaoti}：{fubiaoti}"
    elif "大标题" in names_vals.keys():
        new_dict["title"]=names_vals["大标题"]
    else:
        raise("ERROR: 无标题")

    new_dict["title"]=new_dict["title"]+tongyishuhao_str

    # authors

    if "译者" in names_vals.keys():
        if not "作者" in names_vals.keys():
            new_dict["authors"] = ""
        else:
            zuozhe=names_vals['作者'].replace("著","")
            yizhe=names_vals['译者'].replace("译","")
            new_dict["authors"]=f"{zuozhe} 著; {yizhe} 译"
    elif "作者" in names_vals.keys():
        zuozhe = names_vals['作者'].replace("著", "")
        new_dict["authors"]=zuozhe
    else:
        new_dict["authors"] = ""

    new_dict["authors"]=new_dict["authors"].strip()

    # year

    if "出版年" in names_vals.keys():
        publish_time:str=names_vals["出版年"]
        if publish_time[0:4].isdigit():
            new_dict["year"]=publish_time[0:4]
        else:
            print("Bad year format!")
            new_dict["year"]=""

    # description

    mywords = tongyishuhao_str+"\n\n书签已装载，\n书签制作方法请找 yjyouaremysunshine@163.com\n完全免费\n（若有印刷不清等问题也请发送相关邮件，会尽快更新的）\n\n"

    if "内容描述" in names_vals.keys():
        description=names_vals["内容描述"]
        new_dict["description"]=mywords+description
    else:
        description=""
        new_dict["description"]=mywords+description

    translate("publisher","出版社",new_dict,names_vals)
    translate("pages","页数",new_dict,names_vals)
    translate("series","丛书",new_dict,names_vals)
    translate("isbn","ISBN",new_dict,names_vals)

    new_dict["language"]="中文"


    return new_dict



    # try:
    #     new_dict["publisher"]=names_vals["出版社"]
    # except KeyError:
    #     new_dict["publisher"]=""
    # new_dict["pages"]=names_vals["页数"]
    # new_dict["series"]=names_vals["丛书"]
    # new_dict["isbn"]=names_vals["ISBN"]




def open_one_link(driver,isbn_or_db):

    # 注意末尾一定不能带/，不然...估计就会被解读为文件夹了...

    if len(isbn_or_db)==13:
        isbn=isbn_or_db
        douban_link=f"https://book.douban.com/isbn/{isbn}"
    elif isbn_or_db.isdigit():
        db=isbn_or_db
        douban_link=f"https://book.douban.com/subject/{db}"

    
    driver.get(douban_link)
    infoNode=find_element_by_id2(driver,"info")
    if infoNode=="":
        print(f"豆瓣未收录: {isbn_or_db}")
        return {}
    
    info="\n"+infoNode.text
    # 跟我玩这套，我直接用repr形式来对付你！

    qiangxinghouzhui="\\n'"

    repr_info=repr(info)[:-1]+qiangxinghouzhui

    print(repr_info)

    # 注意这里的匹配是4个\，我也不知道为什么，就是试出来的...

    name_patt = "\\\\n(.*?):"
    namefields=re.findall(name_patt,repr_info)
    val_patt=": (.*?)\\\\n"
    vals=re.findall(val_patt,repr_info)

    print(namefields)
    print(vals)

    assert isinstance(isbn_or_db,str)
    # vals.append(isbn_or_db)

    names_vals={namefield:val for namefield,val in zip(namefields,vals)}

    # description

    descriptionNode = find_element_by_xpath2(driver,"//div[@class='intro']")
    if descriptionNode!="":
        description = descriptionNode.text
    else:
        description=""

    names_vals["内容描述"] = description

    # title

    # douban_title_tail=" (豆瓣)"

    # title=find_element_by_xpath2(driver,"//title")
    # title=title.text.replace(douban_title_tail,"")

    titleNode=find_element_by_xpath2(driver,"//span[@property='v:itemreviewed']")

    if titleNode=="":
        print(f"豆瓣未收录: {isbn_or_db}")
        return {}

    title=titleNode.text

    names_vals["大标题"]=title

    print("names_values:",names_vals)

    new_dict = info_formatter(names_vals)

    return new_dict

def fill_in_blanks(driver,new_dict,upload_new_url):


    driver.get(upload_new_url)

    inputBoxs=find_elements_by_xpath2(driver,"//input[@type='text']")
    descriptionBox=find_element_by_xpath2(driver,"//textarea[@name='description']")
    inputBoxs.append(descriptionBox)

    for eachBox in inputBoxs:
        namefield=eachBox.get_attribute("name")
        if namefield in new_dict.keys():
            val=new_dict[namefield]
            eachBox.send_keys(val)

    print("filled out.Press me!")

def main():
    driver=webdriver.Firefox(options=options,executable_path=firefox_path)
    # isbn = "9787540705336"
    isbn="9787544762281"
    new_dict=open_one_link(driver,isbn)
    print("final pack:",new_dict)
    # sys.exit(0)
    auth_str="genesis:upload"
    upload_new_url=f"https://{auth_str}@library.bz/main/uploads/new/3A12D5C60C0EF21E48A196D98EF909E3"
    fill_in_blanks(driver,new_dict,upload_new_url)
    time.sleep(15)
    driver.quit()

def waibao222():
    driver=webdriver.Firefox(options=options,executable_path=firefox_path)
    isbn="9787100065153"
    new_dict=open_one_link(driver,isbn)
    print("final pack of isbn:",new_dict)
    db="3239624"
    new_dict2=open_one_link(driver,db)
    print("final pack of db:",new_dict2)

def waibao2():
    driver=webdriver.Firefox(options=options,executable_path=firefox_path)
    isbn_or_db="10554308"
    new_dict=open_one_link(driver,isbn_or_db)
    print("final pack:",new_dict)

def waibao1():
    driver=webdriver.Firefox(options=options,executable_path=firefox_path)
    missing_author_path=r"D:\checkifuploaded\missing_authors.txt"
    changed_author_path=r"D:\OneDrive - CUHK-Shenzhen\Linkeer365BookReview\source\_posts\【长期更新】每日传书计划.md"
    changing_author_path=r"D:\checkifuploaded\changing_authors.txt"
    changing_format_path=r"D:\checkifuploaded\changing_format.txt"

    format_lines=[]

    with open(missing_author_path,"r",encoding="utf-8") as f:
        rawlines=[each for each in f.readlines() if each!="\n"]
    
    with open(changed_author_path,"r",encoding="utf-8") as f:
        booklines=f.readlines()
    
    new_lines=[]
    for rawline in rawlines:
        # print(rawline)
        idx,line=rawline.split("===>")
        isbn=line.split(" | ")[2]
        link_head_str="http://libgen.rs/book/index.php?md5="
        link_len=len(link_head_str)+32
        link_head=line.find(link_head_str)
        link=line[link_head:link_head+link_len]
        if "," in isbn:
            splitAt=isbn.find("9787")
            isbn=isbn[splitAt:]
        new_dict=open_one_link(driver,isbn)
        if new_dict=={}:
            new_line=line
        else:    
            author=new_dict["authors"]
            if author=="":
                new_line=line
            else:
                new_line=line.replace("NIL",author)
                format_line=f"{link}\n[Author(s) -> \"{author}\"]\n\n"
                format_lines.append(format_line)
                booklines[int(idx)]=new_line
                print("new line:",new_line)

        new_lines.append(new_line)

    new_lines_s="".join(new_lines)
    format_lines_s="".join(format_lines)
    booklines_s="".join(booklines)

    with open(changing_author_path,"w",encoding="utf-8") as f:
        f.write(new_lines_s)
    with open(changing_format_path,"w",encoding="utf-8") as f:
        f.write(format_lines_s)
    with open(changed_author_path,"w",encoding="utf-8") as f:
        f.write(booklines_s)

    print("done.")

    
    # print(title)

if __name__ == '__main__':
    main()
    # waibao222()
    # waibao2()
    # namefields: ['作者', '出版社', '出品方', '译者', '出版年', '页数', '定价', '装帧', '丛书', 'ISBN'](10)
    # vals: ['[日] 东野圭吾', '南海出版公司', '新经典文化', '刘姿君', '2013-1-1', '538', '39.50元', '精装', '新经典文库·东野圭吾作品'](10)
    # 可以观察到，vals少了ISBN这个部分

    # print(namefields)
    # print(vals)





    # namefieldNodes=find_elements_by_xpath2("//span[@class='pl']")
    # namefields=[each.text for each in namefieldNodes]
    # print(namefields)

# db_link="https://book.douban.com/subject/10554308/"
