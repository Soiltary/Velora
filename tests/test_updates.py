import hashlib,io,json,os,subprocess,tempfile,unittest,zipfile
from pathlib import Path
from unittest.mock import patch
from velora import update_core as u
ROOT=Path(__file__).resolve().parents[1]
def payload(extra=None):
    out=io.BytesIO()
    with zipfile.ZipFile(out,'w') as z:
        for name,data in {'Velora/main.py':b'new','Velora/Velora.exe':b'exe','Velora/runtime/pythonw.exe':b'python',**(extra or {})}.items():z.writestr(name,data)
    return out.getvalue()
def manifest(data):return {'version':'1.3.1','url':'https://github.com/Soiltary/Velora/releases/download/v1.3.1/Velora-Windows-x64-v1.3.1.zip','size':len(data),'sha256':hashlib.sha256(data).hexdigest()}
class Updates(unittest.TestCase):
    def test_manifest_and_versions(self):
        self.assertGreater(u.version('1.10.0'),u.version('1.9.9'));self.assertEqual(u.version('1.3'),u.version('1.3.0'))
        for bad in ['1.3.1-evil','1.','65536.1','../1.0']:
            with self.assertRaises(ValueError):u.version(bad)
        for field,value in [('url','https://evil.test/a.zip'),('sha256','X'*64),('size',True),('size',u.MAX_SIZE+1)]:
            m=manifest(b'a');m[field]=value
            with self.assertRaises(ValueError):u.validate_manifest(m)
    def test_download_integrity(self):
        data=payload()
        class Opener:
            def open(self,*a,**k):return io.BytesIO(data)
        with tempfile.TemporaryDirectory() as folder,patch('urllib.request.build_opener',return_value=Opener()):
            path=Path(folder)/'update.zip';self.assertEqual(u.download(manifest(data),path).read_bytes(),data)
            path.unlink();bad=manifest(data);bad['sha256']='0'*64
            with self.assertRaises(ValueError):u.download(bad,path)
            self.assertFalse(path.exists());self.assertFalse(path.with_suffix('.part').exists())
    def test_reject_unsafe_zip(self):
        for name in ['Velora/../../evil','Velora/C:/evil','Velora/foo/../evil','other/evil','Velora/foo\\evil','Velora/main.PY']:
            with tempfile.TemporaryDirectory() as folder:
                path=Path(folder)/'update.zip';path.write_bytes(payload({name:b'x'}))
                with self.assertRaises(ValueError,msg=name):u.check_archive(path)
    @unittest.skipUnless(os.name=='nt','Windows PowerShell helper')
    def test_installer_copy_and_rollback(self):
        shell=str(Path(os.environ['SystemRoot'])/'System32/WindowsPowerShell/v1.0/powershell.exe')
        for fail in [False,True]:
            with tempfile.TemporaryDirectory(prefix='Velora update test ') as folder:
                base=Path(folder);target=base/'installed';(target/'runtime').mkdir(parents=True);(target/'Velora.exe').write_bytes(b'old exe');(target/'runtime/pythonw.exe').write_bytes(b'old python');(target/'main.py').write_bytes(b'old');(target/'personal.txt').write_text('keep')
                extra={}
                if fail:(target/'zzz.bin').mkdir();extra={'Velora/zzz.bin':b'fail after other writes'}
                archive=base/'update.zip';archive.write_bytes(payload(extra));script=ROOT/'velora/apply_update.ps1';digest=hashlib.sha256(archive.read_bytes()).hexdigest()
                result=subprocess.run([shell,'-NoProfile','-ExecutionPolicy','Bypass','-File',str(script),'-Target',str(target),'-Archive',str(archive),'-ExpectedHash',digest,'-NoRestart','-Silent'],capture_output=True,text=True,timeout=60)
                self.assertEqual(result.returncode,1 if fail else 0,result.stdout+result.stderr);self.assertEqual((target/'main.py').read_bytes(),b'old' if fail else b'new');self.assertEqual((target/'personal.txt').read_text(),'keep')
