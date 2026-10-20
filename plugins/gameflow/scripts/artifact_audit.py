#!/usr/bin/env python3
"""Read-only tracked working-tree size and Git object inventory (not history pruning)."""
import argparse
from collections import defaultdict
import json
from pathlib import Path
import subprocess

p=argparse.ArgumentParser(description=__doc__);p.add_argument('--project',type=Path,default=Path('.'));p.add_argument('--output',type=Path);a=p.parse_args();root=a.project.resolve()
def git(*args):return subprocess.check_output(['git','-C',str(root),*args])
groups=defaultdict(lambda:{'files':0,'bytes':0});largest=[];raster=[]
for name in git('ls-files','-z').decode().split('\0'):
    f=root/name
    if not name or not f.is_file():continue
    size=f.stat().st_size;group='/'.join(name.split('/')[:2]) if name.startswith('.gameflow/') else name.split('/')[0]
    groups[group]['files']+=1;groups[group]['bytes']+=size;largest.append({'path':name,'bytes':size})
    if name.startswith('.gameflow/verification/') and f.suffix.lower() in ('.png','.jpg','.jpeg','.jfif','.exr','.webp'):
        raster.append({'path':name,'bytes':size})
report={'basis':'Tracked working-tree file sizes, not compressed history or clone transfer size. No deletion performed.','groups':dict(groups),'largest':sorted(largest,key=lambda x:-x['bytes'])[:20],'verification_rasters':raster,'git_objects':git('count-objects','-vH').decode()}
s=json.dumps(report,indent=2)+'\n'
if a.output:a.output.write_text(s)
else:print(s,end='')
