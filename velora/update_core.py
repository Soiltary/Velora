"""Fixed-origin release discovery and bounded verified downloads; no UI imports."""
from __future__ import annotations
import hashlib,json,re,urllib.request,urllib.parse,zipfile,stat
from pathlib import Path
VERSION='1.3.0'
FEED='https://velora-windows.soltairy.chatgpt.site/downloads/windows-update.json'
MAX_SIZE=250*1024*1024

def version(value):
    if not isinstance(value,str) or not re.fullmatch(r'\d{1,5}(?:\.\d{1,5}){1,3}',value):raise ValueError('Invalid version')
    parts=tuple(map(int,value.split('.')))
    if any(p>65535 for p in parts):raise ValueError('Invalid version')
    return parts+(0,)*(4-len(parts))

def validate_manifest(data):
    if not isinstance(data,dict):raise ValueError('Invalid update manifest')
    offered=data.get('version');version(offered)
    expected=f'https://github.com/Soiltary/Velora/releases/download/v{offered}/Velora-Windows-x64-v{offered}.zip'
    if data.get('url')!=expected or not re.fullmatch('[0-9a-fA-F]{64}',str(data.get('sha256',''))) or type(data.get('size')) is not int or not 0<data['size']<=MAX_SIZE:raise ValueError('Invalid update manifest')
    return data

class SafeRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self,req,fp,code,msg,headers,newurl):
        url=urllib.parse.urlsplit(newurl)
        if url.scheme!='https' or url.username or url.password or url.port not in (None,443) or not (url.hostname=='github.com' or url.hostname.endswith('.githubusercontent.com')):raise ValueError('Unexpected update redirect')
        return super().redirect_request(req,fp,code,msg,headers,newurl)

def check():
    req=urllib.request.Request(FEED,headers={'Cache-Control':'no-cache','Pragma':'no-cache','User-Agent':'Velora-Updater/'+VERSION})
    # Feed redirects are never accepted; manifests must come from the fixed site.
    class NoRedirect(urllib.request.HTTPRedirectHandler):
        def redirect_request(self,*args,**kwargs):raise ValueError('Unexpected manifest redirect')
    with urllib.request.build_opener(NoRedirect()).open(req,timeout=20) as response:
        data=response.read(65537)
    if len(data)>65536:raise ValueError('Update manifest too large')
    manifest=validate_manifest(json.loads(data))
    return manifest if version(manifest['version'])>version(VERSION) else None

def check_archive(path):
    """Reject traversal, alternate streams, links and duplicate Windows paths."""
    seen=set();total=0
    with zipfile.ZipFile(path) as archive:
        for item in archive.infolist():
            name=item.filename
            if '\\' in name or not name.startswith('Velora/') or ':' in name:raise ValueError('Unsafe archive path')
            rel=name[len('Velora/'):].rstrip('/')
            if not rel:continue
            parts=rel.split('/')
            if any(not p or p in ('.','..') or p.endswith((' ','.')) or any(ord(c)<32 for c in p) for p in parts):raise ValueError('Unsafe archive path')
            key=rel.casefold()
            if key in seen or stat.S_ISLNK(item.external_attr>>16):raise ValueError('Unsafe archive entry')
            seen.add(key);total+=item.file_size
            if total>1200*1024*1024:raise ValueError('Expanded update too large')
        if 'main.py' not in seen or 'velora.exe' not in seen or 'runtime/pythonw.exe' not in seen:raise ValueError('Incomplete application update')

def download(manifest,destination,progress=lambda value:None):
    manifest=validate_manifest(manifest);destination=Path(destination);partial=destination.with_suffix('.part');digest=hashlib.sha256();total=0
    try:
        with urllib.request.build_opener(SafeRedirect()).open(manifest['url'],timeout=30) as response,partial.open('xb') as output:
            while chunk:=response.read(1024*1024):
                total+=len(chunk)
                if total>manifest['size']:raise ValueError('Update size mismatch')
                output.write(chunk);digest.update(chunk);progress(total*100//manifest['size'])
        if total!=manifest['size'] or digest.hexdigest().lower()!=manifest['sha256'].lower():raise ValueError('Update verification failed')
        check_archive(partial);partial.replace(destination);return destination
    finally:
        partial.unlink(missing_ok=True)
