#!/usr/bin/env python3
"""File system watcher using polling."""
import os,time,hashlib,json
class FileWatcher:
    def __init__(self,paths,extensions=None):
        self.paths=paths;self.extensions=extensions;self.state={};self.callbacks=[]
    def on_change(self,fn): self.callbacks.append(fn)
    def scan(self):
        current={}
        for path in self.paths:
            if os.path.isfile(path): current[path]=self._hash(path)
            elif os.path.isdir(path):
                for root,_,files in os.walk(path):
                    for f in files:
                        fp=os.path.join(root,f)
                        if self.extensions and not any(f.endswith(e) for e in self.extensions): continue
                        current[fp]=self._hash(fp)
        return current
    def check(self):
        current=self.scan(); events=[]
        for f in current:
            if f not in self.state: events.append(("created",f))
            elif current[f]!=self.state[f]: events.append(("modified",f))
        for f in self.state:
            if f not in current: events.append(("deleted",f))
        self.state=current
        for ev in events:
            for cb in self.callbacks: cb(*ev)
        return events
    def _hash(self,path):
        try:
            with open(path,"rb") as f: return hashlib.md5(f.read(8192)).hexdigest()
        except: return None
if __name__=="__main__":
    import tempfile
    d=tempfile.mkdtemp(); f1=os.path.join(d,"test.txt")
    with open(f1,"w") as f: f.write("hello")
    w=FileWatcher([d]); w.scan(); w.state=w.scan()
    with open(f1,"w") as f: f.write("changed")
    events=w.check()
    assert any(e[0]=="modified" for e in events)
    print(f"Events: {events}"); print("File watcher OK")
