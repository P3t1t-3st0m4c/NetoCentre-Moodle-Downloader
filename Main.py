from html.parser import HTMLParser
from urllib.parse import urlparse, unquote_plus
import requests as req
import argparse
import re
import os

url_to_match = 'https://lycees.netocentre.fr/moodle/course/view.php?id='
url_to_find = 'https://lycees.netocentre.fr/moodle/mod/resource/view.php?id='
length_of_url_to_find = len(url_to_find)
liste_ids = []
liste_sizes = ['o','ko','mo','go','to']
full_size = total = 0

class MyHTMLParser(HTMLParser):
    def handle_starttag(self, tag, attrs):
        for attr in attrs:
            if attr[0] == 'href' and attr[1].startswith(url_to_find):
                print(f"Found id ! : {attr[1][length_of_url_to_find:]}")
                liste_ids.append(attr[1][length_of_url_to_find:])
            if attr[0] == 'href' and attr[1].startswith("https://lycees.netocentre.fr/moodle/pluginfile.php/"):
                self.downloadUrl = attr[1]

def parseAndGetTheIds(url, cookies, link, save = False):
    data = ''
    parser = MyHTMLParser()
    request = req.get(url, cookies = cookies)
    parser.feed(request.text)
    
    if save:
        for i in liste_ids:
            data += i+'\n'
        
        with open(link+'ids.txt', 'w', encoding='utf-8') as handler:
            handler.write(data)
            handler.close()

    downloadWithTheIds(liste = liste_ids)

def downloadWithTheIds(**kwargs):
    parser = MyHTMLParser()
    if 'liste' in kwargs:
        for i in kwargs['liste']:
            downloadWithLink(i,parser)
    elif 'string' in kwargs:
        downloadWithLink(kwargs['string'],parser)
    else:
        print('Error : no argument given \nquitting ...')
        exit(0)

def downloadWithLink(id_for_url, parser, **kwargs):
    global full_size, total
    link = './'
    size = 0
    if 'link' in kwargs:
        link = kwargs['link']
    url = url_to_find + id_for_url
    r = req.get(url, allow_redirects=False, cookies = cookies)
    parser.feed(r.text)
    parsed = urlparse(parser.downloadUrl)
    
    new_url = parsed[0]+'://'+parsed[1]+parsed[2]
    r = req.get(new_url, allow_redirects=False, cookies = cookies)
    filename = unquote_plus(parsed[2].split('/')[-1])
    size = size_convert(len(r.content))
    full_size += len(r.content)
    total += 1
    print(f'Downloading :\n{filename}\n    Size : {size[0]} {size[1]}')
    with open(link+filename, 'wb') as handler:
        handler.write(r.content)
        handler.close()

def cookie(string):
    if bool(re.fullmatch('(?:[0-9a-fA-F]){32}',string)):
        return string
    raise TypeError

def liste(string):
    if string.startswith(url_to_match):
        return string
    elif int(string):
        return url_to_match+string
    raise TypeError

def size_convert(integer):
    base = 1
    for i in liste_sizes:
        if integer >= base * 1000:
            base *= 1000
        else:
            return (round(integer/base,2),i)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog = 'NetoCentre Moodle Downloader', allow_abbrev=False)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("-s", "--String",metavar = 'Id', nargs = 1, help = "Download the document with the provided id", type=int)
    group.add_argument("-l", "--List", metavar = 'Url/Id', nargs = 1, help = "Download all the documents of a provided url or id", type=liste)
    parser.add_argument("-c", "--Cookie", required=True, nargs = 1, help = "Token to connect to netocentre (MoodleSessionMDLPROD)",type=cookie)
    parser.add_argument("-f", "--File", nargs = 1, help = f"Path to save the files ({sys.argv[0]} if not given)", type=open)
    parser.add_argument("-i", "--Ids", action='store_true', help = "Return all the ids found in a txt")
    parser.add_argument('--version', action='version', version='%(prog)s 1.0')
    args = parser.parse_args()

    cookies = {"MoodleSessionMDLPROD" : args.Cookie[0]}
    path = './'
    if args.File:
        path = args.File

    if args.String:
        downloadWithTheIds(string = args.String[0])
    else:
        parseAndGetTheIds(args.List[0], cookies, path, args.Ids)

    conv = size_convert(full_size)
    os.system('cls')
    print(f'Downloaded {total} files with a total of {conv[0]} {conv[1]} !')
    print('Closing ...')