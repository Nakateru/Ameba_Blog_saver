from bs4 import BeautifulSoup
import multiprocessing as mp
import requests
import os
import re
import json
import time


def entrysaverfun(url, fl=None):  # url,失败列表fl
    if fl is None:
        fl = [0]
    piclist = []  # 图片列表
    i = 1

    data = requests.get(url).content
    soup = BeautifulSoup(data, 'html.parser')

    try:  # 获取日期时间主题标题
        date = re.findall(r'datePublished":"(.*?)T', soup.get_text())
        datetime = re.findall(r'datePublished":"(.*?)","dateModified"', soup.get_text())
        themename = re.findall(r'theme_name":"(.*?)","user_id"', soup.get_text())
        articletitle = re.findall(r'entry_title":"(.*?)","entry_text"', soup.get_text())
        # entryid = re.findall(r'-.*?(\d+).html', url)
        path = date[0] + ' ' + articletitle[0]
        path = path.replace(r'\\', '')
        path = json.loads(f'"{path}"')
        path = re.sub('[\/:*?"<>|]', '', path)
        print('Saving blog entry, URL : ' + url)
        # print('Blog entry ID : ' + entryid[0])
        # print('Theme name : ' + themename[0])
        # print('Path : ' + path)
    except Exception:
        print('Error URL')
        fl.append(url)  # 加入失败列表

    try:  # 创建文件夹 '''时间 标题'''
        if not os.path.exists(themename[0] + '/' + path):
            os.makedirs(themename[0] + '/' + path)
            print('Created folder ' + themename[0] + '/' + path + ' successfully')
        else:
            print('Folder' + ' existed')
    except Exception:
        print('Failed to Creat Folder ')
        print('Failed to Save Blog:', url)
        fl.append(url)

    for s in soup.select('#entryBody'):  # '''获取正文文本'''选正文tag
        body = s.prettify()  # 排版换行
        bodytext = BeautifulSoup(body, 'html.parser')  # 去tag
        blogtext = bodytext.get_text()

    try:  # 判断有没正文
        blogtext
    except NameError:
        False
        print('Failed to Get Text,URL:', url)
        print('Failed to Save Blog,URL:', url)
        fl.append(url)
    else:
        True
        print('Got entry text successfully,URL:', url)

    # '''正文写入txt'''
    # '''
    # 标题 时间
    # 主题
    # 正文
    # '''
    try:
        textname = date[0] + ' ' + articletitle[0] + '.txt'
        textname = textname.replace(r'\\', '')
        textname = json.loads(f'"{textname}"')
        textname = re.sub('[\/:*?"<>|]', '', textname)
        articletitletext = json.loads(f'"{articletitle[0]}"')
        with open(themename[0] + '/' + path + '/' + textname, 'w', encoding='UTF-8') as f:
            f.write(articletitletext + ' ' + datetime[0] + '\n' + 'テーマ： ' + themename[0] + '\n' + blogtext)
        print('Saved blog ' + date[0] + ' ' + articletitle[0] + ' text')
    except Exception:
        print('Failed to Save Blog ' + date[0] + ' ' + articletitle[0] + ' Text')
        fl.append(url)

    # '''获取图片URL'''
    try:
        links = [aurl.get('href') for aurl in soup.find_all('a')]  # 所有atag的url
        for piclink in [str for str in links if str not in ['', ' ', None]]:
            if piclink.startswith('https://stat.ameba.jp/user_images/'):  # 筛选博客图片url
                piclist.append(piclink)
        # print(links)
        # print(piclist)
        piclen = len(piclist)
        print('Found ' + str(piclen) + ' picture(s) in blog ' + date[0] + ' ' + articletitle[0])
        if piclen == 0:
            print('Saved blog ' + date[0] + ' ' + articletitle[0] + ' Successfully')
    except Exception:
        print('Failed to Get ' + date[0] + ' ' + articletitle[0] + ' Pictures')
        fl.append(url)

    # '''写入图片'''
    for k in piclist:
        try:
            # print(k)
            r = requests.get(url=k)
            pictype = requests.head(k).headers.get('content-type')  # 判断图片格式
            if pictype == 'image/jpeg':
                picsavetype = 'jpg'
            elif pictype == 'image/gif':
                picsavetype = 'gif'
            elif pictype == 'image/png':
                picsavetype = 'png'
            picname = date[0] + ' ' + articletitle[0] + ' ' + str(i) + '.' + picsavetype
            picname = picname.replace(r'\\', '')
            picname = json.loads(f'"{picname}"')
            picname = re.sub('[\/:*?"<>|]', '', picname)
            with open(themename[0] + '/' + path + '/' + picname, 'wb') as f:
                f.write(r.content)
                i += 1
                # print('Saved picture ' + str(i - 1) + ' successfully')
                if i > piclen:
                    i = 1
                    print('Saved Blog ' + date[0] + ' ' + articletitle[0] + ' pictures')
                    print('Saved blog ' + date[0] + ' ' + articletitle[0] + ' Successfully')
        except Exception:
            print('Failed to Save pictures,URL:', url)
            fl.append(url)


def Searchentry(url, name):
    data = requests.get(url).content
    soup = BeautifulSoup(data, 'html.parser')
    links = [s.get('href') for s in soup.find_all('a')]
    for entrylink in [str for str in links if str not in ['', ' ', None]]:  # 去除None元素空元素
        if entrylink.startswith('/' + name + '/entry-'):
            entrylist.append(entrylink)


def Pagefun(urlflag, Fristthemeurl):  # urlflag,0:theme,1:archive
    global entrylist
    entrylist = []
    themeurl = Fristthemeurl
    if urlflag == 0:
        Fristthemenum = re.findall(r'theme(.*?)-', Fristthemeurl)
        themeid = re.findall(r'-.*?(\d+).html', Fristthemeurl)
        print('Blog theme URL :', themeurl)
        themeid = themeid[0]
        print('Blog theme ID :', themeid)
    else:
        Fristthemenum = re.findall(r'archive(.*?)-', Fristthemeurl)
        achiveid = re.findall(r'-.*?(\d+).html', Fristthemeurl)
        print('Blog archive URL :', themeurl)
        themeid = achiveid[0]
        print('Blog archive ID :', themeid)

    # '''定义主题序号'''
    if Fristthemenum[0] == '':
        themenum = 1
        Original_theme_num = 1
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
                    print('This theme has only 1 Page')
                    break
                elif Original_theme_num == 1:  # 本来就是从第一页开始翻的
                    break
                else:  # 翻回最初的前一页
                    if urlflag == 0:
                        themeurl = 'https://ameblo.jp/' + blogname + '/theme' + str(
                            Original_theme_num - 1) + '-' + themeid + '.html'
                    else:
                        themeurl = 'https://ameblo.jp/' + blogname + '/archive' + str(
                            Original_theme_num - 1) + '-' + themeid + '.html'

                    themenum = Original_theme_num - 1
                    print('Searching entries on Page ' + str(themenum))
                    break

            else:  # 后翻
                themenum += 1
                print('Searching entries on Page ' + str(themenum))
                if urlflag == 0:
                    themeurl = 'https://ameblo.jp/' + blogname + '/theme' + str(themenum) + '-' + themeid + '.html'
                else:
                    themeurl = 'https://ameblo.jp/' + blogname + '/archive' + str(themenum) + '-' + themeid + '.html'

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
                else:
                    themeurl = 'https://ameblo.jp/' + blogname + '/archive' + str(themenum) + '-' + themeid + '.html'

    except Exception:
        print(' Failed to search entries URL')
        exit()

    entrylist = list(set(entrylist))  # 去除重复元素
    # print(entrylist)

    if urlflag == 0:
        print('This theme has ' + str(len(entrylist)) + ' entries(entry).')
    else:
        print('This archive has ' + str(len(entrylist)) + ' entries(entry).')


def is_amebaurl(url):
    flag = 0
    if url.startswith('https://ameblo.jp/' + blogname + '/entry'):
        return flag
    elif url.startswith('https://ameblo.jp/' + blogname + '/theme'):
        flag = 1
        return flag
    elif url.startswith('https://ameblo.jp/' + blogname + '/archive'):
        flag = 2
        return flag
    else:
        flag = 3
        return flag


def savejob1(entrylist, l):  # 失败列表参数l传入entrysaverfun
    for i in entrylist:
        entryurl = 'https://ameblo.jp' + i
        entrysaverfun(entryurl, l)


def savejob2(job2list, l):
    for i in job2list:
        entryurl = 'https://ameblo.jp' + i
        entrysaverfun(entryurl, l)


def failedlistfun(fl):
    fl = list(set(fl))
    l = len(fl)
    if l > 0:
        print('Saved Part of Blog Entries Media in', '%.2f' % (st1 - st), 's')
        print('----------Failed to save URL list-----------')
        for i in fl:
            print(i)
    else:
        print('Saved All Blog Entries Media in', '%.2f' % (st1 - st), 's')


def multicore():
    entrylistlen = len(entrylist)
    # print(entrylistlen)
    if entrylistlen == 0:
        print('No entry in this theme')
    elif entrylistlen == 1:
        entryurl = 'https://ameblo.jp' + entrylist[0]
        entrysaverfun(entryurl)
    else:
        for i in entrylist:  # 分两份给两个任务
            job2list.append(i)
            entrylist.remove(i)
        # print(job2list)
        # print(entrylist)
        # print(len(job2list))
        # print(len(entrylist))

        p1 = mp.Process(target=savejob1, args=(entrylist, failedlist))
        p2 = mp.Process(target=savejob2, args=(job2list, failedlist))
        p1.start()
        p2.start()
        p1.join()
        p2.join()


if __name__ == '__main__':
    job2list = []
    failedlist = mp.Manager().list()  # 共享失败列表
    print('Ameba Blog Saver v2.1')
    print('Author  :  Nakateru (2019.12.8)')

    '''输入阿米巴URL'''
    Fristurl = input('Input Ameba Blog URL:')
    st = time.time()

    try:
        blogname = re.findall(r'ameblo.jp/(.*?)/', Fristurl)
        blogname = blogname[0]
        print('Blog name: ' + blogname)
    except Exception:
        print('Error URL')
        exit()

    if is_amebaurl(Fristurl) == 0:
        print('This is an Ameba entry URL')
        entrysaverfun(Fristurl)
        st1 = time.time()

    elif is_amebaurl(Fristurl) == 1:
        print('This is an Ameba theme URL')
        Pagefun(0, Fristurl)
        multicore()
        st1 = time.time()
        failedlistfun(failedlist)

    elif is_amebaurl(Fristurl) == 2:
        print('This is an Ameba theme URL classified by months')
        Pagefun(1, Fristurl)
        multicore()
        st1 = time.time()
        failedlistfun(failedlist)

    else:
        print('Error URL')
        exit()
