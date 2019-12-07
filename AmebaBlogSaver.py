from bs4 import BeautifulSoup
import requests
import os
import re

'''输入阿米巴URL'''
url = input('Input Ameba Blog URL:')

'''定义'''
piclist = []  # 图片列表
i = 1

'''Requests'''
try:
    data = requests.get(url).content
    soup = BeautifulSoup(data, 'html.parser')
except Exception:
    print('URL Error')
    exit()

'''获取日期时间主题标题'''
try:
    date = re.findall(re.compile(r'datePublished":"(.*?)T'), soup.get_text())
    datetime = re.findall(re.compile(r'datePublished":"(.*?)","dateModified"'), soup.get_text())
    theme = re.findall(re.compile(r'theme_name":"(.*?)","user_id"'), soup.get_text())
    articletitle = re.findall(re.compile(r'entry_title":"(.*?)","entry_text"'), soup.get_text())
    path = date[0] + ' ' + articletitle[0]
    path = re.sub('[\/:*?"<>|]', '', path)
except Exception:
    print('URL Error')
    exit()

'''创建文件夹'''
'''时间 标题'''

try:
    if not os.path.exists(path):
        os.mkdir(path)
        print('Created folder successfully')
    else:
        print('Folder' + ' existed')
except Exception:
    print('Creating Folder Failed\n')
    print('Saving Blog Failed')
    exit()

'''获取正文文本'''
for s in soup.select('#entryBody'):  # 选正文tag
    body = s.prettify()  # 排版换行
    bodytext = BeautifulSoup(body, 'html.parser')  # 去tag
    blogtext = bodytext.get_text()

'''判断有没正文'''
try:
    blogtext
except NameError:
    False
    print('Getting Text Failed\n')
    print('Saving Blog Failed')
    exit()
else:
    True
    print('Got text successfully')

'''正文写入txt'''
'''
标题 时间
主题
正文
'''
try:
    textname = date[0] + ' ' + articletitle[0] + '.txt'
    textname = re.sub('[\/:*?"<>|]', '', textname)
    with open(path + '/' + textname, 'w', encoding='UTF-8') as f:
        f.write(articletitle[0] + ' ' + datetime[0] + '\n' +'テーマ： '+ theme[0] + '\n' + blogtext)
    print('Saved blog text Successfully')
except Exception:
    print('Saving Blog Text Failed')

'''获取图片URL'''
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

'''写入图片'''
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
        picname = re.sub('[\/:*?"<>|]', '', picname)
        with open(path + '/' + picname, 'wb') as f:
            f.write(r.content)
            i += 1
            print('Saved picture ' + str(i - 1) + ' successfully')
            if i > piclen:
                i = 1
                print('Blog picture(s) saved')
                print('Saved blog ' + date[0] + ' ' + articletitle[0] + ' Successfully')
    except Exception:
        print('Saving picture Failed')
