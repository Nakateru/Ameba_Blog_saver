from selenium import webdriver
import re

def Searchentry(url):
    driver.get(url)
    try:
        ele=driver.find_element_by_xpath("//ul[@class='contentsList skinBorderList']")
        title = ele.find_elements_by_class_name('contentTitle')
        time = ele.find_elements_by_tag_name('time')
        for i in title:
            titlelist.append(i.text)
            entrylist.append(i.get_attribute('href'))
        for i in time:
            timelist.append(i.text)
    except:
        ele = driver.find_elements_by_class_name('skin-borderQuiet')
        for i in ele:
            title = i.find_element_by_tag_name('h2')
            datetime = i.find_element_by_tag_name('p')
            titlelist.append(title.text)
            entrylist.append(title.find_element_by_tag_name('a').get_attribute('href'))
            timelist.append(datetime.text[-19:])

def is_NextPage():
    flag = False
    try:
        driver.find_element_by_xpath("//a[@class='skin-paginationNext skin-btnIndex js-paginationNext']")
        return flag
    except:
        flag = True
        return flag

def Pagefun(urlflag, Fristthemeurl):  # urlflag,0:theme,1:archive,2:entrylist
    global entrylist
    entrylist = []
    themeid='123'
    themeurl = Fristthemeurl
    if urlflag == 0:
        Fristthemenum = re.findall(r'theme(.*?)-', Fristthemeurl)
        themeid = re.findall(r'-.*?(\d+).html', Fristthemeurl)
        print('Blog theme URL :', themeurl)
        themeid = themeid[0]
        print('Blog theme ID :', themeid)
    elif urlflag == 1:
        Fristthemenum = re.findall(r'archive(.*?)-', Fristthemeurl)
        achiveid = re.findall(r'-.*?(\d+).html', Fristthemeurl)
        print('Blog archive URL :', themeurl)
        themeid = achiveid[0]
        print('Blog archive ID :', themeid)
    else:
        Fristthemenum = re.findall(r'entrylist(.*?)', Fristthemeurl)

    if Fristthemenum[0] == '':
        themenum = 1
        Original_theme_num = 1
        print('Searching entries on Page', themenum)
    else:
        themenum = int(Fristthemenum[0])
        Original_theme_num = int(Fristthemenum[0])
        print('Searching entries on Page', themenum)

    # '''翻页'''
    # '''1)themeFristPage ： themenum=1  后翻(1)None→break[Only one Page] (2)themenum+=1 前翻→themenum==1 →break
    #    2)themeX： themenum=X  后翻 themenum+=1 前翻 themenum-=1
    #    3)lastPage： themenum=lastPage 后翻None→break 前翻→themenum-=1→→→→1
    # '''
    try:
        while True:  # 后翻页
            Searchentry(themeurl)
            if is_NextPage():  # 无下一页
                if themenum == 1:  # 只有一页
                    print('This theme only has 1 Page')
                    break
                elif Original_theme_num == 1:  # 本来就是从第一页开始翻的
                    break
                else:  # 翻回最初的前一页
                    if urlflag == 0:
                        themeurl = 'https://ameblo.jp/' + blogname + '/theme' + str(
                            Original_theme_num - 1) + '-' + themeid + '.html'
                    elif urlflag == 1:
                        themeurl = 'https://ameblo.jp/' + blogname + '/archive' + str(
                            Original_theme_num - 1) + '-' + themeid + '.html'
                    else:
                        themeurl = 'https://ameblo.jp/' + blogname + '/entrylist-' + str(
                            Original_theme_num - 1) + '.html'
                    themenum = Original_theme_num - 1
                    print('Searching entries on Page ' + str(themenum))
                    break

            else:  # 后翻
                themenum += 1
                print('Searching entries on Page ' + str(themenum))
                if urlflag == 0:
                    themeurl = 'https://ameblo.jp/' + blogname + '/theme' + str(themenum) + '-' + themeid + '.html'
                elif urlflag == 1:
                    themeurl = 'https://ameblo.jp/' + blogname + '/archive' + str(themenum) + '-' + themeid + '.html'
                else:
                    themeurl = 'https://ameblo.jp/' + blogname + '/entrylist-' + str(themenum) + '.html'

        while True:  # 前翻页
            if Original_theme_num == 1:  # 只有一页或从第一页开始翻
                break
            elif themenum == 1:  # 翻到第一页
                Searchentry(themeurl)
                break
            else:  # 前翻
                Searchentry(themeurl)
                themenum -= 1
                print('Searching entries on Page ' + str(themenum))
                if urlflag == 0:
                    themeurl = 'https://ameblo.jp/' + blogname + '/theme' + str(themenum) + '-' + themeid + '.html'
                elif urlflag == 1:
                    themeurl = 'https://ameblo.jp/' + blogname + '/archive' + str(themenum) + '-' + themeid + '.html'
                else:
                    themeurl = 'https://ameblo.jp/' + blogname + '/entrylist-' + str(themenum) + '.html'

    except Exception:
        print(' Failed to search entries URL')
        exit()

    if urlflag == 0:
        print('This theme has ' + str(len(entrylist)) + ' entries(entry).')
    elif urlflag == 1:
        print('This archive has ' + str(len(entrylist)) + ' entries(entry).')
    else:
        print('This account has ' + str(len(entrylist)) + ' entries(entry).')

def is_amebaurl(url):
    flag = 0
    if url.startswith('https://ameblo.jp/' + blogname + '/entrylist'):
        flag = 3
        return flag
    elif url.startswith('https://ameblo.jp/' + blogname + '/entry'):
        return flag
    elif url.startswith('https://ameblo.jp/' + blogname + '/theme'):
        flag = 1
        return flag
    elif url.startswith('https://ameblo.jp/' + blogname + '/archive'):
        flag = 2
        return flag
    else:
        flag = 4
        return flag


if __name__ == '__main__':
    titlelist = []
    timelist = []
    x = 0
    print('Ameba entry list printer')
    print('Author  :  Nakateru (2019.12.25)')
    Fristurl = input('Input Ameba URL:')
    blogname = re.findall(r'ameblo.jp/(.*?)/', Fristurl)
    blogname = blogname[0]

    # Searchentry(Fristurl)
    # print(titlelist)
    # print(timelist)
    # print(entrylist)

    if is_amebaurl(Fristurl)==0:
        print('This is an Ameba entry URL')
        exit()

    elif is_amebaurl(Fristurl) == 1:
        print('This is an Ameba theme URL')
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')
        options.add_experimental_option('excludeSwitches', ['enable-automation'])
        driver = webdriver.Chrome(chrome_options=options)
        Pagefun(0, Fristurl)
        driver.quit()

    elif is_amebaurl(Fristurl) == 2:
        print('This is an Ameba theme URL classified by months')
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')
        options.add_experimental_option('excludeSwitches', ['enable-automation'])
        driver = webdriver.Chrome(chrome_options=options)
        Pagefun(1, Fristurl)
        driver.quit()

    elif is_amebaurl(Fristurl) == 3:
        print('This is an Ameba accout URL')
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')
        options.add_experimental_option('excludeSwitches', ['enable-automation'])
        driver = webdriver.Chrome(chrome_options=options)
        Pagefun(2, Fristurl)
        driver.quit()
    else:
        print('Error URL')
        exit()

    lenentrylist = len(entrylist)

    while x < lenentrylist:
        with open('theme_list.txt', 'a', encoding='UTF-8') as f:
            print(entrylist[x], timelist[x], titlelist[x])
            f.write(entrylist[x] + ' '+ timelist[x] + ' ' + titlelist[x] + '\n')
        x += 1
