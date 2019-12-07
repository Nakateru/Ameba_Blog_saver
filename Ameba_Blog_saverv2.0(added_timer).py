from bs4 import BeautifulSoup
import requests
import os
import re
import json
import time

def entrysaverfun(url):
    piclist = []  # 图片列表
    i = 1

    data = requests.get(url).content
    soup = BeautifulSoup(data, 'html.parser')

    try:  # 获取日期时间主题标题
        date = re.findall(re.compile(r'datePublished":"(.*?)T'), soup.get_text())
        datetime = re.findall(re.compile(r'datePublished":"(.*?)","dateModified"'), soup.get_text())
        themename = re.findall(re.compile(r'theme_name":"(.*?)","user_id"'), soup.get_text())
        articletitle = re.findall(re.compile(r'entry_title":"(.*?)","entry_text"'), soup.get_text())
        entryid = re.findall(re.compile(r'-.*?(\d+).html'), url)
        path = date[0] + ' ' + articletitle[0]
        path = path.replace(r'\\', '')
        path=json.loads(f'"{path}"')
        path = re.sub('[\/:*?"<>|]', '', path)
        print('Blog entry URL : ' + url)
        print('Blog entry ID : ' + entryid[0])
        print('Theme name : ' + themename[0])
        print('Path : ' + path)
    except Exception:
        print('URL Error')
        exit()
    try:  # 创建文件夹 '''时间 标题'''
        if not os.path.exists(themename[0] + '/' + path):
            os.makedirs(themename[0] + '/' + path)
            print('Created folder ' + themename[0] + '/' + path + ' successfully')
        else:
            print('Folder' + ' existed')
    except Exception:
        print('Creating Folder Failed')
        print('Saving Blog Failed')
        exit()
    for s in soup.select('#entryBody'):  # '''获取正文文本'''选正文tag
        body = s.prettify()  # 排版换行
        bodytext = BeautifulSoup(body, 'html.parser')  # 去tag
        blogtext = bodytext.get_text()
    try:  # 判断有没正文
        blogtext
    except NameError:
        False
        print('Getting Text Failed\n')
        print('Saving Blog Failed')
        exit()
    else:
        True
        print('Got text successfully')
    # '''正文写入txt'''
    # '''
    # 标题 时间
    # 主题
    # 正文
    # '''
    try:
        textname = date[0] + ' ' + articletitle[0] + '.txt'
        textname = textname.replace(r'\\', '')
        textname=json.loads(f'"{textname}"')
        textname = re.sub('[\/:*?"<>|]', '', textname)
        articletitletext=json.loads(f'"{articletitle[0]}"')
        with open(themename[0] + '/' + path + '/' + textname, 'w', encoding='UTF-8') as f:
            f.write(articletitletext + ' ' + datetime[0] + '\n' + 'テーマ： ' + themename[0] + '\n' + blogtext)
        print('Saved blog text Successfully')
    except Exception:
        print('Saving Blog Text Failed')
    # '''获取图片URL'''
    try:
        links = [aurl.get('href') for aurl in soup.find_all('a')]  # 所有atag的url
        for piclink in [str for str in links if str not in ['', ' ', None]]:
            if piclink.startswith('https://stat.ameba.jp/user_images/'):  # 筛选博客图片url
                piclist.append(piclink)
            if piclink.startswith('http://stat.ameba.jp/user_images/'):
                piclist.append(piclink)
        # print(links)
        # print(piclist)
        piclen = len(piclist)
        print('Found ' + str(piclen) + ' picture(s) in this blog')
        if piclen == 0:
            print('Saved blog ' + date[0] + ' ' + articletitle[0] + ' Successfully')
    except Exception:
        print('Getting Pictures Failed')
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
                print('Saved picture ' + str(i - 1) + ' successfully')
                if i > piclen:
                    i = 1
                    print('Blog picture(s) saved')
                    print('Saved blog ' + date[0] + ' ' + articletitle[0] + ' Successfully')
        except Exception:
            print('Saving picture Failed')


def Searchentry(url, name):
    data = requests.get(url).content
    soup = BeautifulSoup(data, 'html.parser')
    links = [s.get('href') for s in soup.find_all('a')]
    for entrylink in [str for str in links if str not in ['', ' ', None]]:  # 去除None元素空元素
        if entrylink.startswith('/' + name + '/entry-'):
            entrylist.append(entrylink)


def Pagefun(Fristthemeurl):
    Fristthemenum = re.findall(re.compile(r'theme(.*?)-'), Fristthemeurl)
    themeid = re.findall(re.compile(r'-.*?(\d+).html'), Fristthemeurl)
    global entrylist
    entrylist = []
    themeurl = Fristthemeurl
    print('Blog theme URL : ' + themeurl)
    themeid = themeid[0]
    print('Blog theme ID : ' + themeid)

    # '''定义主题序号'''
    if Fristthemenum[0] == '':
        themenum = 1
        Original_theme_num = 1
    else:
        themenum = int(Fristthemenum[0])
        Original_theme_num = int(Fristthemenum[0])
        print('Searching entries in Page ' + str(themenum))

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
                    themeurl = 'https://ameblo.jp/' + blogname + '/theme' + str(
                        Original_theme_num - 1) + '-' + themeid + '.html'
                    themenum = Original_theme_num - 1
                    print('Searching entries in Page ' + str(themenum))
                    break
            else:  # 后翻
                themenum += 1
                print('Searching entries in Page ' + str(themenum))
                themeurl = 'https://ameblo.jp/' + blogname + '/theme' + str(themenum) + '-' + themeid + '.html'

        while True:  # 前翻页
            if Original_theme_num == 1:  # 只有一页或从第一页开始翻
                break
            elif themenum == 1:  # 翻到第一页
                Searchentry(themeurl, blogname)
                break
            else:  # 前翻
                Searchentry(themeurl, blogname)
                themenum -= 1
                print('Searching entries in Page ' + str(themenum))
                themeurl = 'https://ameblo.jp/' + blogname + '/theme' + str(themenum) + '-' + themeid + '.html'
    except Exception:
        print('Searching entries URL Failed')
    entrylist = list(set(entrylist))  # 去除重复元素
    print('This theme has ' + str(len(entrylist)) + ' entries(entry).')


print('Ameba Blog Saver v2.0')
print('Author  :  Nakateru (2019.11.16)')

'''输入阿米巴URL'''
Fristurl = input('Input Ameba Blog URL:')
st = time.time()
try:
    blogname = re.findall(re.compile(r'ameblo.jp/(.*?)/'), Fristurl)
    blogname = blogname[0]
    print('Blog name: ' + blogname)

    if Fristurl.startswith('https://ameblo.jp/' + blogname + '/entry'):
        print('This is an Ameba entry')
        entrysaverfun(Fristurl)
    elif Fristurl.startswith('https://ameblo.jp/' + blogname + '/theme'):
        print('This is an Ameba theme')
        Pagefun(Fristurl)
        for k in range(len(entrylist)):
            entryurl = 'https://ameblo.jp' + entrylist[k]
            entrysaverfun(entryurl)
        st1 = time.time()
        print('Saved All entries in this theme Successffully in','%.2f' % (st1-st),'s')
except Exception:
    print('Error URL')
    exit()
