#!/usr/bin/env python3
"""Prepare and verify a single-branch rewrite in a NEW isolated bare clone.
Never updates the source repository or any remote. Requires an external verified
bundle and an explicitly supplied official git-filter-repo executable/script.
"""
import argparse
import json
from pathlib import Path
import subprocess
import sys
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--project',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
p.add_argument('--branch',required=True);p.add_argument('--backup',type=Path,required=True)
p.add_argument('--paths-file',type=Path,required=True,help='Reviewed git-filter-repo removal paths; never inferred')
p.add_argument('--filter-repo',type=Path,required=True);a=p.parse_args()
root=a.project.resolve();out=a.output.resolve();backup=a.backup.resolve();tool=a.filter_repo.resolve()
def git(*args,cwd=root):return subprocess.check_output(['git','-C',str(cwd),*args],stderr=subprocess.STDOUT).decode().strip()
if out.exists() or out.is_relative_to(root):raise SystemExit('Output must be a new directory outside project')
if not backup.is_file() or backup.is_relative_to(root):raise SystemExit('External bundle required')
git('bundle','verify',str(backup))
# Confirm the bundle includes current branch ancestry; source tip can contain the
# later policy commit that removes payloads but must descend from the backup tip.
heads=git('bundle','list-heads',str(backup)).splitlines()
old_backup=next((r.split()[0] for r in heads if r.split()[1]=='refs/heads/'+a.branch),None)
if not old_backup:raise SystemExit('Bundle does not contain selected branch')
git('merge-base','--is-ancestor',old_backup,'refs/heads/'+a.branch)
if not a.paths_file.is_file() or not tool.is_file():raise SystemExit('Paths file and filter-repo script must exist')
old=git('rev-parse','refs/heads/'+a.branch);tree=git('rev-parse',old+'^{tree}')
subprocess.run(['git','clone','--no-local','--bare','--single-branch','--no-tags','--branch',a.branch,str(root),str(out)],check=True)
refs=git('for-each-ref','--format=%(refname)',cwd=out).splitlines()
if refs!=['refs/heads/'+a.branch]:raise SystemExit('Unexpected refs in isolated clone')
before=git('count-objects','-vH',cwd=out)
subprocess.run([sys.executable,str(tool),'--paths-from-file',str(a.paths_file.resolve()),'--invert-paths'],cwd=out,check=True)
new=git('rev-parse','refs/heads/'+a.branch,cwd=out);after_tree=git('rev-parse',new+'^{tree}',cwd=out)
if tree!=after_tree:raise SystemExit('Retained tip tree changed: inspect candidate; do not publish')
report={'branch':a.branch,'old':old,'new':new,'tip_tree':tree,'tip_tree_identical':True,'before_objects':before,'after_objects':git('count-objects','-vH',cwd=out),'backup':str(backup),'remote_updated':False}
(out/'cleanup-report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
