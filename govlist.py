#!/usr/bin/python

import urllib2
import urllib
import re
from bs4 import BeautifulSoup
import json
import codecs


person_url = 'http://oid.nat.gov.tw/infobox1/personmain.jsp'
showdata_url = 'http://oid.nat.gov.tw/infobox1/showdata.jsp'


def main():
    showdata = collectShowdataParams()
    datas = collectShowData(showdata)
    saveToJson(datas)


def collectShowdataParams():
    """
    Collect all texts inside "javascript:showdata('<text>')".
    By using these texts, we can use these as parameters for HTTP Post method.
    And gets all the datas from the bad looking website.
    """

    datas = []

    try:
        ufile = urllib2.urlopen(person_url)
    except urllib2.HTTPError, e:
        print e.code
        return
    except urllib2.URLError, e:
        print e.code
        return

    showdata_re = re.compile(r'javascript:showdata\(\'(.*?)\'\)\">')
    for line in ufile:
        line = line.decode('big5')
        match = showdata_re.search(line)
        if match:
            datas.append(match.group(1))
    return datas


def collectShowData(params):
    """
    After collecting all the parameters in "collectShowdataParams()", we can use these parameters to HTTP POST and retrieve all the info.
    """

    assert isinstance(params, list)

    data_list = []

    for param in params:
        form = {'sSdn': param.encode('big5')}
        data = urllib.urlencode(form)

        try:
            request = urllib2.Request(showdata_url, data)
            content = urllib2.urlopen(request).read()
        except urllib2.HTTPError, e:
            print e.code
            return
        except urllib2.URLError, e:
            print e.code
            return
        content = content.decode('big5')
        soup = BeautifulSoup(content, 'lxml')

        item = {}
        for tr in soup.find_all('tr'):
            texts = [text for text in tr.stripped_strings]
            if len(texts) == 2:
                item[texts[0]] = texts[1]
            elif len(texts) == 1:
                item[texts[0]] = ''
        data_list.append(item)
    return data_list


def saveToJson(datas):
    """
    After retrieving all the datas from the bad looking website, then we can save these in Json format.
    Isn't it simple?
    """

    assert isinstance(datas, list)

    datas = json.dumps(datas, ensure_ascii=False, indent=4)
    with codecs.open('govlist.json', 'w', 'utf-8') as f:
        f.write(datas)


if __name__ == '__main__':
    main()
