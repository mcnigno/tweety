import requests
from requests import Request, Session
import urllib

#
# Get files in folder per user
#

# headers are still to be implemented
#header = {'Bearer':'sN9lCWsXJK5pUieh2paeuyZAzNf6jnMAizMHhze97i0MYKu91wnF2ECQB73HsnSP'}
#headers = {'content-type':'application/x-www-form-urlencoded'}

auth = ('danilo','lollipop300777')
url = 'https://cloud.quasarpm.com/remote.php/dav/files/danilo'
data = '<?xml version="1.0" encoding="UTF-8"?>\
 <d:propfind xmlns:d="DAV:">\
   <d:prop xmlns:oc="http://owncloud.org/ns">\
     <d:getlastmodified/>\
     <d:getcontentlength/>\
     <d:getcontenttype/>\
     <oc:permissions/>\
     <d:resourcetype/>\
     <oc:fileid />\
     <d:getetag/>\
   </d:prop>\
 </d:propfind>'

req = Request('PROPFIND',url=url,auth=auth, data=data)
session = Session()
prepared_req = req.prepare()

response = session.send(prepared_req, timeout=5)

path = 'danilo/'

key_info = ['id>',path,'modified>','getcontenttype>']

def filedav_parser(response):
    block = response.content.decode().split("<d:response>")
    main_list = []
    for line in block:
        line = urllib.parse.unquote(line)
        sub_list = []
        for k in key_info:
            try:
                info = line.split(k)[1].split('</')[0]
                sub_list.append(info)
            except:
                continue
        main_list.append(sub_list)
    return main_list



