# -*- coding: utf-8 -*-

url = "http://www.qidian.com/Book/2952453.aspx"
selector = "#readV > div.title"
selector_chapter_name = "h3 > a > font > strong"
selector_update_date = "h3 > span > span[itemprop='dateModified']"
delay = 600
hook_token = None
hook_site_url = None
current_chapter = None