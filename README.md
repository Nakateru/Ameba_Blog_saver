# Ameba_Blog_saver
V1

只能保存单篇文章


V2.0

保存主题中的记事(theme)或单篇记事(entry)

自动识别是主题还是文章

自动保存不同图片格式



V2.1

加入失败列表

修改部分print

加入multiprocessing，双进程同时保存,节省一半时间(理论上)

可以保存某个月的主题中的记事(archive)


V2.2.1

使用selenium保存内容

更改消耗时间格式 00:00:00

可以保存视频

加入过滤器，可以选择保存标题或正文中包含关键词的记事：

1）输入O进入设置模式
2）输入1（标题）或2（正文）
3）输入要包含的关键词
4）输入记事或主题url


V2.2.2

1）输入https://ameblo.jp/+ 用户名+/entrylist.html保存整个账号的记事
2）输入y


V2.2.3

bug fixes

失败列表保存到failed_list.txt

可以按行读取txt里的记事url后单进程保存记事
1）输入O进入设置模式
2）输入3
4）输入txt文件名,如failed_list.txt或theme_list.txt等

V2.2.4

修复部分记事的搜图问题，已经验证保存整个账号的记事的功能

以下记事保存不了：
会员限定记事，直接跳过



# Ameba_entry_list_printer

输入主题url后打印出主题的记事url+时间+题目，并保存到theme_list.txt

*使用selenium搜索记事(比较慢)(saver使用requests+Beautifulsoup搜索记事url）
