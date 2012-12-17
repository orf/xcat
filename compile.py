from bbfreeze import Freezer
import zipfile
import os
import shutil

f = Freezer("xcat-bin")
f.addScript("src/xcat.py")
f()

with zipfile.ZipFile('xcat_compiled.zip','w',zipfile.ZIP_DEFLATED) as zf:
    for root, dirs, files in os.walk("xcat-bin"):
        for fn in files:
            absfn = os.path.join(root, fn)
            zfn = absfn[len("xcat-bin")+len(os.sep):] #XXX: relative path
            zf.write(absfn, zfn)

if os.path.isdir("xcat-bin"): shutil.rmtree("xcat-bin")
if os.path.isdir("xcat"): shutil.rmtree("xcat")