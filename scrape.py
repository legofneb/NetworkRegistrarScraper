import http.cookiejar
import os
import urllib
import urllib.parse
import urllib.request
import csv
import configparser
from bs4 import BeautifulSoup

def removeNonAscii(s): return "".join(i for i in s if ord(i)<128)

config = configparser.ConfigParser()
config.read('config.ini')

username = config['User']['id']
password = config['User']['password']
rootUrl = config['Website']['rootUrl']

#store cookies and create opener to hold them
cj = http.cookiejar.CookieJar()
opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))

#Add our headers
opener.addheaders = [('User-agent', 'WebScrape')]

#install our opener (changes global opener)
urllib.request.install_opener(opener)

#The action/ target from the form
authentication_url = rootUrl + '/login.jsp'

payload = {
  'name': username,
  'pass': password,
  'cmd': 'Login'
  }
  
#use urllib to encode the payload
data = urllib.parse.urlencode(payload)

#Build our request object (supplying 'data' make it a POST)
req = urllib.request.Request(authentication_url, data.encode('utf-8'))

#Make the request and read the response
resp = urllib.request.urlopen(req)
contents = resp.read()

#Send 1 request
dchp_url = rootUrl + '/dhcp-admin/ListCNRScopes.jsp'

req = urllib.request.Request(dchp_url)
urllib.request.urlopen(req)

payload = {
    'searchValue': '',
    'pageSize': '1000',
    'Change Page Size': 'Change Page Size',
    'pageName': 'cnrscope-cursor_0_sort-by-name'
}

dhcp_url = rootUrl + '/dhcp-admin/ListCNRScopes.jsp?__vPage=dhcp-cnrscope-list&highlightValue=AP_611'
data = urllib.parse.urlencode(payload)

#Build our request object (supplying 'data' make it a POST)
req = urllib.request.Request(dhcp_url, data.encode('utf-8'))

#Make the request and read the response
resp = urllib.request.urlopen(req)
contents = resp.read()
#print contents
parsed_html = BeautifulSoup(contents)

print('\n')

links = []

for node in parsed_html.findAll('a'):
    if (len(''.join(node.findAll(text=True))) > 0 and
        len(''.join(node.findAll(text=True))) > 6 and
            (''.join(node.findAll(text=True)).startswith('Su') or # These are the first 2 letters of the links, used to filter main list to sublist you may need
             ''.join(node.findAll(text=True)).startswith('AU') or # as well as filter out the actual links from other links on the page
             ''.join(node.findAll(text=True)).startswith('ME') or
             ''.join(node.findAll(text=True)).startswith('TW'))):
        links.append(node['href'])

with open('report.csv', 'wb') as f:
    
    for link in links:
        subnet_url = rootUrl + link
        print(subnet_url)
        req = urllib.request.Request(subnet_url)
        urllib.request.urlopen(req)

        mac_addr = link[-23:]
        leases_url = rootUrl + '/dhcp-admin/ListCNRLeasesForScope.jsp?__vPage=dhcp-cnrscope-lease-list&cnrScopeOID=OID-' + mac_addr + '&refreshList=true'

        print(leases_url + '\n')
        
        req = urllib.request.Request(leases_url)
        urllib.request.urlopen(req)

        leases_url = rootUrl + '/dhcp-admin/ListCNRLeasesForScope.jsp?__vPage=dhcp-cnrscope-lease-list'
        
        payload = {
            'searchValue': '',
            'pageSize': '1000',
            'Change Page Size': 'Change Page Size',
            'pageName': 'cnrlease-for-scope-by-address-cursor'
        }

        

        data = urllib.parse.urlencode(payload)

        req = urllib.request.Request(leases_url, data.encode('utf-8'))

        #Make the request and read the response
        resp = urllib.request.urlopen(req)
        contents = resp.read()
        parsed_html = BeautifulSoup(contents)

        for node in parsed_html.findAll(attrs={'class':'listA'}):
            if (len(node.findAll("td")[4].get_text()) > 4):
                lineItem = removeNonAscii(node.findAll("td")[1].get_text() + ',' + node.findAll("td")[4].get_text() + ',' + node.findAll("td")[3].get_text() + ',' + node.findAll("td")[2].get_text() + '\n').encode('ascii')
                f.write(lineItem)

        for node in parsed_html.findAll(attrs={'class':'listB'}):
            if (len(node.findAll("td")[4].get_text()) > 4):
                lineItem = removeNonAscii(node.findAll("td")[1].get_text() + ',' + node.findAll("td")[4].get_text() + ',' + node.findAll("td")[3].get_text() + ',' + node.findAll("td")[2].get_text() + '\n').encode('ascii')
                f.write(lineItem)


