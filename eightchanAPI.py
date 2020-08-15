# -*- coding: utf-8 -*-
#!/usr/bin/python3
__title__ = 'eightchanAPI'
__version__ = '1.0'
__build__ = 0x020501
__author__ = 'Dan Mercurio, Bartlomiej Mika, Bearshire'
__license__ = 'LGPL'
__copyright__ = 'Copyright 2015 Dan Mercurio'

# 8chan url: make this a variable because unfortunately it changes
SCHEMA = 'https://'
DOMAIN = '8kun.top/'
MAIN_URL = SCHEMA + DOMAIN

import requests, json, time

class eightchan(object):
    def get_boards(self):
        boards = []
        url = requests.get(MAIN_URL + 'boards.json').text
        boards_json = json.loads(url)
        for board_json in boards_json:
            #Added to prevent missing JSON atribute
            if 'pph_average' not in board_json:
                board_json[u'pph_average'] = 0
            new_board = Board(board_json[u'uri'],
                              board_json[u'title'],
                              board_json[u'subtitle'],
                              board_json[u'indexed'],
                              board_json[u'sfw'],
                              board_json[u'posts_total'],
                              board_json[u'time'],
                              board_json[u'weight'],
                              board_json[u'locale'],
                              board_json[u'tags'],
                              board_json[u'max'],
                              board_json[u'active'],
                              board_json[u'pph'],
                              board_json[u'ppd'],
                              board_json[u'pph_average'])
            boards.append(new_board)
        return boards

    def get_board(self, uri):
        uri = uri.strip('/')
        boards = self.get_boards()
        for board in boards:
            if (uri == board.uri):
                return board
        return False

    def get_boards_count(self):
        boards_count = 0
        url = requests.get(MAIN_URL + 'boards.json').text
        boards_json = json.loads(url)
        for board_json in boards_json:
            boards_count += 1
        return boards_count

class Post(eightchan):
    def __init__(self, name, number, sub, capcode, com, posttime,
                 fsize, filename, ext, locked, sticky, extra_files,
                 tim, board, page):
        self.sub = sub
        self.name = name
        self.number = int(number)
        self.capcode = capcode
        self.comment = com
        self.posttime = int(posttime)
        if (fsize is not None):
            self.fsize = int(fsize)
        else:
            self.fsize = fsize
        self.filename = filename
        self.ext = ext
        self.board = board
        self.page = page
        if (locked == u'1'):
            self.locked = True
        if (locked == u'0'):
            self.locked = False
        if (sticky == u'1'):
            self.sticky = True
        if (sticky == u'0'):
            self.sticky = False
        self.extra_files = extra_files
        self.tim = tim

    def get_file_urls(self):
        if self.hasFile():
            urls = list()
            url = SCHEMA + 'media.'
            url += DOMAIN + self.board.uri + '/src/'
            url += self.tim + self.ext
            urls.append(url)
            if self.extra_files is not None:
                for i in self.extra_files:
                    url = SCHEMA + 'media.' + DOMAIN
                    url += self.board.uri + '/src/' + i[u'tim'] + i[u'ext']
                    urls.append(url)
            return urls
        else:
            return False

    def is_locked(self):
        return self.locked

    def is_anon(self):
        return self.name == u'Anonymous'

    def get_board(self):
        return self.board

    def get_page(self):
        return self.page

    def seconds_since_last_modified(self):
        return int(time.time()) - self.last_modified

    def is_sticky(self):
        return self.sticky

    def has_file(self):
        return self.filename is not None

    def has_multiple_files(self):
        return self.extra_files is not None

    def get_post_age(self):
        return int(time.time()) - self.posttime

    def check_dubs(self):
        return str(self.number)[-2:-1] == str(self.number)[-1:]

    def check_trips(self):
        left = str(self.number)[-3:-2]
        middle = str(self.number)[-2:-1]
        right = str(self.number)[-1:]
        return left == middle == right


class Thread:
    def __init__(self, number, page, last_modified, board):
        self.number = int(number)
        self.page = int(page)
        self.board = board
        self.last_modified = int(last_modified)
        self.posts = []

    def is_front_page(self):
        return self.page == 0

    def seconds_since_last_modified(self):
        return int(time.time()) - self.last_modified

    def get_posts(self):
        url = MAIN_URL + self.board.uri
        url += u'/res/' + str(self.number) + u'.json'
        url = requests.get(url).text
        postsJson = json.loads(url)
        for p in postsJson[u'posts']:
            try:
                name = p[u'name']
            except KeyError:
                name = None
            number = p[u'no']
            try:
                capcode = p[u'capcode']
            except KeyError:
                capcode = None
            try:
                com = p[u'com']
            except KeyError:
                com = None
            posttime = p[u'time']
            try:
                fsize = p[u'fsize']
            except KeyError:
                fsize = None
            try:
                filename = p[u'filename']
            except KeyError:
                filename = None
            try:
                ext = p[u'ext']
            except KeyError:
                ext = None
            locked = p[u'locked']
            sticky = p[u'sticky']
            try:
                extra_files = p['extra_files']
            except KeyError:
                extra_files = None
            try:
                sub = p[u'sub']
            except KeyError:
                sub = None
            try:
                tim = p[u'tim']
            except KeyError:
                tim = None

            post = Post(name=name,
                        number=number,
                        sub=sub,
                        capcode=capcode,
                        com=com,
                        posttime=posttime,
                        fsize=fsize,
                        filename=filename,
                        ext=ext,
                        locked=locked,
                        sticky=sticky,
                        extra_files=extra_files,
                        tim=tim,
                        board=self.board,
                        page=self.page)
            self.posts.append(post)
        return self.posts

    def number_of_posts(self):
        return len(self.posts)

    def first_post(self):
        if (len(self.posts) == 0):
            return self.get_posts()[0]
        else:
            return self.posts[0]

    def get_all_file_urls(self):
        urls = list()
        if len(self.posts) == 0:
            self.getPosts()

        for post in self.get_posts():
            urls.append(post.get_file_urls())
        return urls


class Board:
    def __init__(self, uri, title, subtitle, indexed,
                 sfw, posts_total, time, weight, locale, tags, max, active, pph, ppd,  pph_average):
        self.uri = uri
        self.title = title
        self.subtitle = subtitle
        if (indexed == u'0'):
            self.indexed = False
        if (indexed == u'1'):
            self.indexed = True
        if (sfw == u'0'):
            self.sfw = False
        if (sfw == u'1'):
            self.sfw = True
        self.posts_total = int(posts_total) 
        self.time = time
        if (weight == u'0'):
            self.weight = False
        if (weight == u'1'):
            self.weight = True
        self.locale = locale
        self.tags = tags
        self.max = max
        self.active = int(active)
        self.ppd = int(ppd)
        self.ppd = int(pph)
        self.ppd = float(pph_average)
        self.threads = []

    def __repr__(self):
        string = str("<8chan /" + self.uri + "/ board ")
        string += str(object.__repr__(self))[1:]
        return string

    def first_thread(self):
        if (len(self.threads) == 0):
            return self.get_threads()[0]
        else:
            return self.threads[0]

    def get_threads(self):
        url = requests.get(MAIN_URL + self.uri + '/threads.json').text
        threadsJson = json.loads(url)
        for page in threadsJson:
            currentPage = page[u'page']
            for thread_json in page[u'threads']:
                thread = Thread(thread_json[u'no'],
                                currentPage,
                                thread_json[u'last_modified'],
                                self)
                self.threads.append(thread)
        return self.threads

    def get_thread(self, thread_id):
        for thread in self.get_threads():
            if thread.number == int(thread_id):
                return thread
        return False


if __name__ == "__main__":
    api = eightchan()
    board = api.get_board('/vichan/')
    first_thread = board.first_thread()
    post = first_thread.first_post().comment
    BoardList = api.get_boards()
    for item in BoardList:
        print(item.uri)