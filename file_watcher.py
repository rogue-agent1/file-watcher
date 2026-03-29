#!/usr/bin/env python3
"""File watcher using polling. Zero dependencies."""
import os, sys, time, hashlib

class FileWatcher:
    def __init__(self, paths, interval=1.0):
        self.paths = paths if isinstance(paths, list) else [paths]
        self.interval = interval
        self.state = self._scan()

    def _hash(self, path):
        try:
            s = os.stat(path)
            return f"{s.st_mtime}:{s.st_size}"
        except OSError:
            return None

    def _scan(self):
        state = {}
        for p in self.paths:
            if os.path.isfile(p):
                state[p] = self._hash(p)
            elif os.path.isdir(p):
                for root, dirs, files in os.walk(p):
                    for f in files:
                        fp = os.path.join(root, f)
                        state[fp] = self._hash(fp)
        return state

    def check(self):
        """Check for changes. Returns dict of created/modified/deleted."""
        new_state = self._scan()
        created = [f for f in new_state if f not in self.state]
        deleted = [f for f in self.state if f not in new_state]
        modified = [f for f in new_state if f in self.state and new_state[f] != self.state[f]]
        self.state = new_state
        return {"created": created, "modified": modified, "deleted": deleted}

    def has_changes(self):
        changes = self.check()
        return any(changes.values())

    def watch(self, callback, max_iterations=None):
        """Poll for changes and call callback."""
        i = 0
        while max_iterations is None or i < max_iterations:
            changes = self.check()
            if any(changes.values()):
                callback(changes)
            time.sleep(self.interval)
            i += 1

if __name__ == "__main__":
    paths = sys.argv[1:] or ["."]
    w = FileWatcher(paths)
    print(f"Watching {len(w.state)} files...")
    def on_change(c):
        for t, fs in c.items():
            for f in fs: print(f"  {t}: {f}")
    w.watch(on_change)
