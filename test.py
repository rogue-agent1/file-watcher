import tempfile, os, time
from file_watcher import FileWatcher
with tempfile.TemporaryDirectory() as td:
    f1 = os.path.join(td, "a.txt")
    with open(f1, "w") as f: f.write("initial")
    w = FileWatcher(td)
    c = w.check()
    assert not any(c.values())  # no changes yet
    time.sleep(0.1)
    with open(f1, "w") as f: f.write("modified")
    c = w.check()
    assert f1 in c["modified"]
    f2 = os.path.join(td, "b.txt")
    with open(f2, "w") as f: f.write("new")
    c = w.check()
    assert f2 in c["created"]
    os.remove(f1)
    c = w.check()
    assert f1 in c["deleted"]
print("file_watcher tests passed")
