#!/usr/bin/env python3
"""Prepare and validate project-local Noto Sans SC webfonts.
Prepare fonts against the public Google Fonts CSS API.
Online download is explicit (--download); offline mode uses supplied WOFF2.
"""
import argparse, hashlib, io, json, re, ssl, sys, urllib.parse, urllib.request
from html.parser import HTMLParser
from pathlib import Path

API='https://fonts.googleapis.com/css2'
LICENSE_URL='https://raw.githubusercontent.com/google/fonts/main/ofl/notosanssc/OFL.txt'
UA='Mozilla/5.0 AppleWebKit/537.36 Chrome/124.0.0.0 Safari/537.36'
class Text(HTMLParser):
    def __init__(self):super().__init__();self.parts=[];self.skip=0
    def handle_starttag(self,tag,attrs):
        if tag in ('script','style'):self.skip+=1
    def handle_endtag(self,tag):
        if tag in ('script','style'):self.skip=max(0,self.skip-1)
    def handle_data(self,data):
        if not self.skip:self.parts.append(data)

def collect(html, extra=''):
    parser=Text();parser.feed(html)
    return ''.join(sorted(set(c for c in ''.join(parser.parts)+extra+'0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz.,:;!?%+-/()·' if not c.isspace())))

def get(url):
    if urllib.parse.urlparse(url).scheme!='https':raise ValueError('Only HTTPS font sources are accepted')
    try:
        import certifi
        context=ssl.create_default_context(cafile=certifi.where())
    except ImportError:context=ssl.create_default_context()
    with urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':UA}),timeout=40,context=context) as response:
        data=response.read(8_000_001)
        if len(data)>8_000_000:raise ValueError('Font response exceeds 8 MB limit')
        return data

def coverage(data, text):
    try:from fontTools.ttLib import TTFont
    except ImportError:raise ValueError('Install fonttools[woff] to verify actual glyph coverage')
    if not data.startswith(b'wOF2'):raise ValueError('Expected WOFF2, received another format or an error page')
    font=TTFont(io.BytesIO(data));cmap=font.getBestCmap() or {};font.close()
    missing=[c for c in text if ord(c) not in cmap]
    if missing:raise ValueError('Font lacks required characters: '+repr(''.join(missing[:40])))
    return len(text)

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--html',required=True,type=Path);parser.add_argument('--out',required=True,type=Path)
    mode=parser.add_mutually_exclusive_group(required=True);mode.add_argument('--download',action='store_true');mode.add_argument('--regular',type=Path)
    parser.add_argument('--bold',type=Path);parser.add_argument('--license-file',type=Path);parser.add_argument('--text-file',type=Path)
    args=parser.parse_args()
    try:
        if not args.download and (not args.bold or not args.license_file):raise ValueError('Offline mode needs --regular, --bold and --license-file')
        text=collect(args.html.read_text(),args.text_file.read_text() if args.text_file else '')
        # Keep text private unless the caller explicitly authorizes a download.
        if args.download and len(text)>1200:raise ValueError('More than 1200 unique characters; provide full local WOFF2 files for offline verification')
        prepared=[]
        for weight,local in [(400,args.regular),(700,args.bold)]:
            if args.download:
                query=urllib.parse.urlencode({'family':f'Noto Sans SC:wght@{weight}','text':text,'display':'block'})
                source=API+'?'+query;css=get(source).decode('utf-8')
                urls=list(dict.fromkeys(re.findall(r'url\(\s*[\'"]?(https://[^\s)\'\"]+)',css)))
                if len(urls)!=1:raise ValueError('Expected one text-subset font; use offline fonts if API returns multiple partitions')
                font_url=urls[0];data=get(font_url)
            else:source=str(local);font_url=None;data=local.read_bytes()
            coverage(data,text)
            prepared.append((f'sans-{weight}.woff2',data,{'weight':weight,'source':'Google Fonts CSS2 (explicit text subset)' if args.download else 'user-supplied local WOFF2',
                'font_url':font_url,'sha256':hashlib.sha256(data).hexdigest(),'verified_characters':len(text)}))
        license_data=get(LICENSE_URL) if args.download else args.license_file.read_bytes()
        if b'SIL OPEN FONT LICENSE' not in license_data:raise ValueError('Expected a Noto SIL OFL license file; keep the actual font license with offline fonts')
        args.out.mkdir(parents=True,exist_ok=True)
        for name,data,_ in prepared:(args.out/name).write_bytes(data)
        (args.out/'OFL.txt').write_bytes(license_data)
        manifest={'family':'Noto Sans SC','character_set_sha256':hashlib.sha256(text.encode()).hexdigest(),'glyph_coverage':'verified with fontTools cmap','mode':'download' if args.download else 'offline',
                  'license_source':LICENSE_URL if args.download else 'user-supplied license','fonts':[{'file':n,**r} for n,_,r in prepared]}
        (args.out/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
        print(f'Prepared 400/700 WOFF2; {len(text)} unique visible characters verified; OFL and manifest saved.')
        return 0
    except (OSError,ValueError) as exc:print(f'ERROR: {exc}',file=sys.stderr);return 1
if __name__=='__main__':raise SystemExit(main())
