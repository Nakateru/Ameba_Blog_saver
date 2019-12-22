from selenium import webdriver
from bs4 import BeautifulSoup
import multiprocessing as mp
import requests
import os
import re
import json
import time


def entrysaverfun(url, fl=None):
    if fl is None:
        fl = []
    piclist = []
    videolist = []
    i = 1

    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_experimental_option('excludeSwitches', ['enable-automation'])
    driver = webdriver.Chrome(chrome_options=options)
    driver.get(url)

    try:
        datetime = driver.find_element_by_xpath("//span[@class='articleTime']").text[:19]
    except Exception:
        try:
            datetime = driver.find_element_by_xpath("//time[@class='skin-textQuiet']").text[-19:]
        except Exception:
            print('Failed to Get Entry Time', url)
            fl.append(url)

    try:
        themename = driver.find_element_by_xpath("//span[@class='articleTheme']").text[4:]
    except Exception:
        try:
            themename = driver.find_element_by_xpath("//dl[@class='_3wmM1dM_ skin-entryThemes']").text[4:]
        except Exception:
            print('Failed to Get Theme Name', url)
            fl.append(url)

    date = datetime[:10]

    try:
        articletitle = driver.find_element_by_xpath("//a[@class='skinArticleTitle']").text
    except Exception:
        print('Failed to Get Article Title ', url)
        fl.append(url)

        # entryid = re.findall(r'-.*?(\d+).html', url)
    path = date + ' ' + articletitle
    path = path.replace(r'\\', '')
    path = json.loads(f'"{path}"')
    path = re.sub('[\/:*?"<>|]', '', path)
    print('Saving blog entry : ' + url)
    # print('Blog entry ID : ' + entryid[0])
    # print('Theme name : ' + themename)
    # print('Path : ' + path)

    try:  # 创建文件夹 '''时间 标题'''
        if not os.path.exists(themename + '/' + path):
            os.makedirs(themename + '/' + path)
            print('Created folder ' + themename + '/' + path + ' successfully')
        else:
            print('Folder' + ' existed')
    except Exception:
        print('Failed to Creat Folder ')
        print('Failed to Save Blog :', url)
        fl.append(url)
        driver.quit()

    try:
        blogtext = driver.find_element_by_id('entryBody').text
    except Exception:
        print('Failed to Get Entry Text:', url)
        fl.append(url)

    # '''正文写入txt'''
    # '''
    # 标题 时间
    # 主题
    # 正文
    # '''
    try:
        textname = path + '.txt'
        articletitletext = json.loads(f'"{articletitle}"')
        with open(themename + '/' + path + '/' + textname, 'w', encoding='UTF-8') as f:
            f.write(articletitletext + ' ' + datetime + '\n' + 'テーマ： ' + themename + '\n' + blogtext)
        print('Saved blog ' + path + ' text')
    except Exception:
        print('Failed to Save Blog ' + path + ' Text')
        fl.append(url)

    try:
        links = [aurl.get_attribute('src') for aurl in
                 driver.find_element_by_id('entryBody').find_elements_by_tag_name('img')]
        for piclink in links:
            if piclink.startswith('https://stat.ameba.jp/user_images/'):
                piclink = re.search(r"(.+)\?caw=(\d+)", piclink).group(1)
                piclist.append(piclink)
        # print(links)
        # print(piclist)
        piclen = len(piclist)
        if piclen == 0:
            print('No picture in in blog ' + path)

    except Exception:
        print('Failed to Get ' + path + ' Pictures')
        fl.append(url)

        try:
            if not piclen == 0:
                print('Found ' + str(piclen) + ' picture(s) in blog ' + path)
                for k in piclist:
                    # print(k)
                    r = requests.get(url=k)
                    pictype = requests.head(k).headers.get('content-type')  # 判断图片格式
                    if pictype == 'image/jpeg':
                        pictype = 'jpg'
                    elif pictype == 'image/gif':
                        pictype = 'gif'
                    elif pictype == 'image/png':
                        pictype = 'png'
                    picname = path + str(i) + '.' + pictype
                    with open(themename + '/' + path + '/' + picname, 'wb') as f:
                        f.write(r.content)
                    i += 1
                    if i > piclen:
                        i = 1
                        print('Saved Blog ' + path + ' pictures')
        except Exception:
            print('Failed to Save pictures,URL:', url)
            fl.append(url)

    try:
        iframes = driver.find_element_by_id('entryBody').find_elements_by_tag_name('iframe')
        # print(iframes)
        for iframe in iframes:
            driver.switch_to.frame(iframe)
            videolink = driver.find_element_by_tag_name('source').get_attribute('src')
            # print(videolink)
            videolist.append(videolink)
            driver.switch_to.default_content()

        videolistlen = len(videolist)
        if videolistlen == 0:
            print('Saved blog ' + path + ' Successfully')
    except Exception:
        print('Failed to Get ' + path + ' Videos URL')
        fl.append(url)
        driver.quit()


        try:
            if not videolistlen == 0:
                print('Found ' + str(videolistlen) + ' video(s) in blog ' + path)
                for k in videolist:
                    # print(k)
                    r = requests.get(k)
                    videotype = requests.head(k).headers.get('content-type')  # 判断图片格式
                    videotype = videotype[6:]
                    # print(videotype[6:])
                    videoname = path + ' ' + str(i) + '.' + videotype
                    with open(themename + '/' + path + '/' + videoname, 'wb') as f:
                        f.write(r.content)
                i += 1
                if i > videolistlen:
                    print('Saved Blog ' + path + ' videos')
                    print('Saved blog ' + path + ' Successfully')
        except Exception:
            print('Failed to Save videos,URL:', url)
            fl.append(url)
            driver.quit()

    driver.quit()


def Searchentry(url, name):
    data = requests.get(url).content
    soup = BeautifulSoup(data, 'html.parser')
    links = [s.get('href') for s in soup.find_all('a')]
    for entrylink in [str for str in links if str not in ['', ' ', None]]:
        if entrylink.startswith('/' + name + '/entry-'):
            entrylist.append(entrylink)


def Pagefun(urlflag, Fristthemeurl):  # urlflag,0:theme,1:archive,2:entrylist
    global entrylist
    entrylist = []
    themeurl = Fristthemeurl
    if urlflag == 0:
        Fristthemenum = re.findall(r'theme(.*?)-', Fristthemeurl)
        themeid = re.findall(r'-.*?(\d+).html', Fristthemeurl)
        print('Blog theme URL :', themeurl)
        themeid = themeid[0]
        print('Blog theme ID :', themeid)
    elif urlflag==1:
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
            Searchentry(themeurl, blogname)
            data = requests.get(themeurl).content
            soup = BeautifulSoup(data, 'html.parser')
            NextP1 = soup.find('a', class_='skinSimpleBtn pagingNext')
            NextP2 = soup.find('a', class_='skin-paginationNext skin-btnIndex js-paginationNext')
            if (NextP1 == None and NextP2 == None):  # 无下一页
                if themenum == 1:  # 只有一页
                    print('This theme only has 1 Page')
                    break
                elif Original_theme_num == 1:  # 本来就是从第一页开始翻的
                    break
                else:  # 翻回最初的前一页
                    if urlflag == 0:
                        themeurl = 'https://ameblo.jp/' + blogname + '/theme' + str(Original_theme_num - 1) + '-' + themeid + '.html'
                    elif urlflag == 1:
                        themeurl = 'https://ameblo.jp/' + blogname + '/archive' + str(Original_theme_num - 1) + '-' + themeid + '.html'
                    else:
                        themeurl = 'https://ameblo.jp/' + blogname + '/entrylist-' + str(Original_theme_num - 1) + '.html'
                    themenum = Original_theme_num - 1
                    print('Searching entries on Page ' + str(themenum))
                    break

            else:  # 后翻
                themenum += 1
                print('Searching entries on Page ' + str(themenum))
                if urlflag == 0:
                    themeurl = 'https://ameblo.jp/' + blogname + '/theme' + str(themenum) + '-' + themeid + '.html'
                elif urlflag == 0:
                    themeurl = 'https://ameblo.jp/' + blogname + '/archive' + str(themenum) + '-' + themeid + '.html'
                else:
                    themeurl = 'https://ameblo.jp/' + blogname + '/entrylist-' + str(themenum) + '.html'

        while True:  # 前翻页
            if Original_theme_num == 1:  # 只有一页或从第一页开始翻
                break
            elif themenum == 1:  # 翻到第一页
                Searchentry(themeurl, blogname)
                break
            else:  # 前翻
                Searchentry(themeurl, blogname)
                themenum -= 1
                print('Searching entries on Page ' + str(themenum))
                if urlflag == 0:
                    themeurl = 'https://ameblo.jp/' + blogname + '/theme' + str(themenum) + '-' + themeid + '.html'
                elif urlflag == 0:
                    themeurl = 'https://ameblo.jp/' + blogname + '/archive' + str(themenum) + '-' + themeid + '.html'
                else:
                    themeurl = 'https://ameblo.jp/' + blogname + '/entrylist-' + str(themenum) + '.html'

    except Exception:
        print(' Failed to search entries URL')
        exit()

    entrylist = list(set(entrylist))  # 去除重复元素
    # print(entrylist)

    if urlflag == 0:
        print('This1theme has ' + str(len(entrylist)) + ' entries(entry).')
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


def savejob1(job1list, l):
    for i in job1list:
        entryurl = 'https://ameblo.jp' + i
        entrysaverfun(entryurl, l)


def savejob2(job2list, l):
    for i in job2list:
        entryurl = 'https://ameblo.jp' + i
        entrysaverfun(entryurl, l)


def failedlistfun(fl):
    t = st1 - st
    h = t / 3600
    m = t % 3600 / 60
    s = t % 60
    fl = list(set(fl))
    llen = len(fl)
    if llen == 0:
        print('Saved All Blog Entries Media in', '%02d:%02d:%02d' % (int(h), int(m), int(s)))
    else:
        print('Saved Part of Blog Entries Media in', '%02d:%02d:%02d' % (int(h), int(m), int(s)))
        print('----------Failed to save URL list-----------')
        for i in fl:
            print(i)


def multicore(list1, list2, fl):
    list1len = len(list1)
    # print(list1len)
    if list1len == 0:
        print('No entry in this theme')
    elif list1len == 1:
        entryurl = 'https://ameblo.jp' + list1[0]
        entrysaverfun(entryurl)
    else:
        for i in list1:  # divide list1 into 2 lists
            list2.append(i)
            list1.remove(i)
        # print(list1)
        # print(list2)
        # print(len(list1))
        # print(len(list2))
        p1 = mp.Process(target=savejob1, args=(list1, fl))
        p2 = mp.Process(target=savejob2, args=(list2, fl))
        p1.start()
        p2.start()
        p1.join()
        p2.join()


def is_kw_contain(url, keyword, title_or_text=0):
    flag = True
    data = requests.get(url).content
    soup = BeautifulSoup(data, 'html.parser')
    if title_or_text == 0:
        articletitle = re.findall(r'entry_title":"(.*?)","entry_text"', soup.get_text())
        if keyword in articletitle[0]:
            return flag
        else:
            flag = False
            return flag
    else:
        bodytext = soup.select('#entryBody')
        entrytext = bodytext[0]
        if keyword in entrytext.text:
            return flag
        else:
            flag = False
            return flag


if __name__ == '__main__':
    job2list = []
    containkwlist = []
    failedlist = mp.Manager().list()
    print('Ameba Blog Saver v2.2.1')
    print('Author  :  Nakateru (2019.12.23)')
    firstinput = input("Input Ameba Blog URL or 'O' to set keywords filter:")
    if firstinput == 'O' or firstinput == 'o':
        print('[1]Filter keywords from entry title [2]Filter keywords from entries text [3]Exit')
        secondinput = input('Select number:')
        if secondinput == '1':
            kw = input("Input keywords in entries title:")
            if not kw == '':
                Fristurl = input("Input Ameba Blog URL to the filter:")
                try:
                    blogname = re.findall(r'ameblo.jp/(.*?)/', Fristurl)
                    blogname = blogname[0]
                    print('Blog username: ' + blogname)
                except Exception:
                    print('Error URL')
                    exit()

                if is_amebaurl(Fristurl) == 0:
                    print('This is an Ameba entry URL')
                    if is_kw_contain(Fristurl, kw, 0):
                        entrysaverfun(Fristurl, failedlist)
                        st1 = time.time()
                        failedlistfun(failedlist)
                    else:
                        print('Entry title does not contain keywords')
                        exit()

                elif is_amebaurl(Fristurl) == 1:
                    print('This is an Ameba theme URL')
                    st = time.time()
                    Pagefun(0, Fristurl)
                    entrylistlen = len(entrylist)
                    if entrylistlen == 0:
                        print('No entry in this theme')
                        exit()
                    elif entrylistlen == 1:
                        print('Only 1 entry in this theme')
                        entryurl = 'https://ameblo.jp' + entrylist[0]
                        if is_kw_contain(entryurl, kw, 0):
                            print('Entry title contains keywords')
                            entrysaverfun(entryurl, failedlist)
                            st1 = time.time()
                            failedlistfun(failedlist)
                        else:
                            print('Entry title does not contain keywords')
                            exit()

                    else:
                        print('Searching keywords in all entries text of this theme...')
                        for i in entrylist:
                            entryurl = 'https://ameblo.jp' + i
                            if is_kw_contain(entryurl, kw, 0):
                                containkwlist.append(i)
                            else:
                                pass
                        containkwlistlen = len(containkwlist)
                        print(containkwlistlen, 'entries title contain keywords')
                        multicore(containkwlist, job2list, failedlist)
                        st1 = time.time()
                        failedlistfun(failedlist)

                elif is_amebaurl(Fristurl) == 2:
                    print('This is an Ameba theme URL classified by months')
                    st = time.time()
                    Pagefun(1, Fristurl)
                    entrylistlen = len(entrylist)
                    if entrylistlen == 0:
                        print('No entry in this theme')
                        exit()
                    elif entrylistlen == 1:
                        print('Only 1 entry in this theme')
                        entryurl = 'https://ameblo.jp' + entrylist[0]
                        if is_kw_contain(entryurl, kw, 0):
                            print('Entry title contains keywords')
                            entrysaverfun(entryurl, failedlist)
                            st1 = time.time()
                            failedlistfun(failedlist)
                        else:
                            print('Entry title does not contain keywords')
                            exit()

                    else:
                        print('Searching keywords in all entries text of this theme...')
                        for i in entrylist:
                            entryurl = 'https://ameblo.jp' + i
                            if is_kw_contain(entryurl, kw, 0):
                                containkwlist.append(i)
                            else:
                                pass

                        containkwlistlen = len(containkwlist)
                        print(containkwlistlen, 'entries title contain keywords')
                        multicore(containkwlist, job2list, failedlist)
                        st1 = time.time()
                        failedlistfun(failedlist)

                elif is_amebaurl(Fristurl) == 3:
                    print('This is an Ameba accout URL')
                    saveall = input('Do you want to save entries which contain keywords in this account?[y/n]')
                    if saveall == 'y':
                        Pagefun(2, Fristurl)
                        entrylistlen = len(entrylist)
                        if entrylistlen == 0:
                            print('No entry in this account')
                            exit()
                        elif entrylistlen == 1:
                            print('Only 1 entry in this account')
                            entryurl = 'https://ameblo.jp' + entrylist[0]
                            if is_kw_contain(entryurl, kw, 0):
                                print('Entry title contains keywords')
                                entrysaverfun(entryurl, failedlist)
                                st1 = time.time()
                                failedlistfun(failedlist)
                            else:
                                print('Entry title does not contain keywords')
                                exit()

                        else:
                            print('Searching keywords in all entries text in this account...')
                            for i in entrylist:
                                entryurl = 'https://ameblo.jp' + i
                                if is_kw_contain(entryurl, kw, 0):
                                    containkwlist.append(i)
                                else:
                                    pass

                            containkwlistlen = len(containkwlist)
                            print(containkwlistlen, 'entries title contain keywords')
                            multicore(containkwlist, job2list, failedlist)
                            st1 = time.time()
                            failedlistfun(failedlist)

                else:
                    print('Error URL')
                    exit()

            else:
                print('Error keywords')
                exit()

        elif secondinput == '2':
            kw = input("Input keywords in entries text:")
            if not kw == '':
                Fristurl = input("Input Ameba Blog URL to the filter:")
                try:
                    blogname = re.findall(r'ameblo.jp/(.*?)/', Fristurl)
                    blogname = blogname[0]
                    print('Blog username: ' + blogname)
                except Exception:
                    print('Error URL')
                    exit()

                if is_amebaurl(Fristurl) == 0:
                    print('This is an Ameba entry URL')
                    if is_kw_contain(Fristurl, kw, 1):
                        entrysaverfun(Fristurl, failedlist)
                        st1 = time.time()
                        failedlistfun(failedlist)
                    else:
                        print('Entry text does not contain keywords')
                        exit()

                elif is_amebaurl(Fristurl) == 1:
                    print('This is an Ameba theme URL')
                    st = time.time()
                    Pagefun(0, Fristurl)
                    entrylistlen = len(entrylist)
                    if entrylistlen == 0:
                        print('No entry in this theme')
                        exit()
                    elif entrylistlen == 1:
                        print('Only 1 entry in this theme')
                        entryurl = 'https://ameblo.jp' + entrylist[0]
                        if is_kw_contain(entryurl, kw, 1):
                            print('Entry title contains keywords')
                            entrysaverfun(entryurl, failedlist)
                            st1 = time.time()
                            failedlistfun(failedlist)
                        else:
                            print('Entry title does not contain keywords')
                            exit()

                    else:
                        print('Searching keywords in all entries text of this theme...')
                        for i in entrylist:
                            entryurl = 'https://ameblo.jp' + i
                            if is_kw_contain(entryurl, kw, 1):
                                containkwlist.append(i)
                            else:
                                pass
                        containkwlistlen = len(containkwlist)
                        print(containkwlistlen, 'entries title contain keywords')
                        multicore(containkwlist, job2list, failedlist)
                        st1 = time.time()
                        failedlistfun(failedlist)

                elif is_amebaurl(Fristurl) == 2:
                    print('This is an Ameba theme URL classified by months')
                    Pagefun(1, Fristurl)
                    entrylistlen = len(entrylist)
                    if entrylistlen == 0:
                        print('No entry in this theme')
                        exit()
                    elif entrylistlen == 1:
                        print('Only 1 entry in this theme')
                        entryurl = 'https://ameblo.jp' + entrylist[0]
                        if is_kw_contain(entryurl, kw, 1):
                            print('Entry text contains keywords')
                            entrysaverfun(entryurl, failedlist)
                            st1 = time.time()
                            failedlistfun(failedlist)
                        else:
                            print('Entry text does not contain keywords')
                            exit()

                    else:
                        print('Searching keywords in all entries text of this theme...')
                        for i in entrylist:
                            entryurl = 'https://ameblo.jp' + i
                            if is_kw_contain(entryurl, kw, 1):
                                containkwlist.append(i)
                            else:
                                pass
                        containkwlistlen = len(containkwlist)
                        print(containkwlistlen, 'entries text contain keywords')
                        multicore(containkwlist, job2list, failedlist)
                        st1 = time.time()
                        failedlistfun(failedlist)

                elif is_amebaurl(Fristurl)==3:
                    print('This is an Ameba accout URL')
                    saveall = input('Do you want to save entries which contain keywords in this account?[y/n]')
                    if saveall == 'y':
                        Pagefun(2, Fristurl)
                        entrylistlen = len(entrylist)
                        if entrylistlen == 0:
                            print('No entry in this account')
                            exit()
                        elif entrylistlen == 1:
                            print('Only 1 entry in this account')
                            entryurl = 'https://ameblo.jp' + entrylist[0]
                            if is_kw_contain(entryurl, kw, 1):
                                print('Entry title contains keywords')
                                entrysaverfun(entryurl, failedlist)
                                st1 = time.time()
                                failedlistfun(failedlist)
                            else:
                                print('Entry text does not contain keywords')
                                exit()

                        else:
                            print('Searching keywords in all entries text in this account...')
                            for i in entrylist:
                                entryurl = 'https://ameblo.jp' + i
                                if is_kw_contain(entryurl, kw, 1):
                                    containkwlist.append(i)
                                else:
                                    pass

                            containkwlistlen = len(containkwlist)
                            print(containkwlistlen, 'entries text contain keywords')
                            multicore(containkwlist, job2list, failedlist)
                            st1 = time.time()
                            failedlistfun(failedlist)

                else:
                    print('Error URL')
                    exit()

            else:
                print('Error keywords')
                exit()

        elif secondinput == '3':
            exit()
        else:
            print('Error input')
            exit()
    else:
        Fristurl = firstinput
        try:
            blogname = re.findall(r'ameblo.jp/(.*?)/', Fristurl)
            blogname = blogname[0]
            print('Blog username: ' + blogname)
        except Exception:
            print('Error URL')
            exit()

        st = time.time()

        if is_amebaurl(Fristurl) == 0:
            print('This is an Ameba entry URL')
            entrysaverfun(Fristurl, failedlist)
            st1 = time.time()
            failedlistfun(failedlist)

        elif is_amebaurl(Fristurl) == 1:
            print('This is an Ameba theme URL')
            Pagefun(0, Fristurl)
            entrylistlen = len(entrylist)
            if entrylistlen == 0:
                print('No entry in this theme')
                exit()
            elif entrylistlen == 1:
                print('Only 1 entry in this theme')
                entryurl = 'https://ameblo.jp' + entrylist[0]
                entrysaverfun(entryurl, failedlist)
                st1 = time.time()
                failedlistfun(failedlist)
            else:
                multicore(entrylist, job2list, failedlist)
                st1 = time.time()
                failedlistfun(failedlist)

        elif is_amebaurl(Fristurl) == 2:
            print('This is an Ameba theme URL classified by months')
            Pagefun(1, Fristurl)
            entrylistlen = len(entrylist)
            if entrylistlen == 0:
                print('No entry in this theme')
                exit()
            elif entrylistlen == 1:
                print('Only 1 entry in this theme')
                entryurl = 'https://ameblo.jp' + entrylist[0]
                entrysaverfun(entryurl, failedlist)
                st1 = time.time()
                failedlistfun(failedlist)
            else:
                multicore(entrylist, job2list, failedlist)
                st1 = time.time()
                failedlistfun(failedlist)

        elif is_amebaurl(Fristurl) == 3:
            print('This is an Ameba accout URL')
            saveall=input('Do you want to save all entries in this account?[y/n]')
            if saveall=='y':
                Pagefun(2, Fristurl)
                entrylistlen = len(entrylist)
                if entrylistlen == 0:
                    print('No entry in this account')
                    exit()
                elif entrylistlen == 1:
                    print('Only 1 entry in this account')
                    entryurl = 'https://ameblo.jp' + entrylist[0]
                    entrysaverfun(entryurl, failedlist)
                    st1 = time.time()
                    failedlistfun(failedlist)
                else:
                    multicore(entrylist, job2list, failedlist)
                    st1 = time.time()
                    failedlistfun(failedlist)

            else:
                exit()
        else:
            print('Error URL')
            exit()
