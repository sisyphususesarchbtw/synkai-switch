"""An OS-held lock prevents two supervisors sharing a case budget."""
import os
from pathlib import Path


class RuntimeLease:
    def __init__(self,path: Path):
        path.parent.mkdir(parents=True,exist_ok=True)
        self.path,self.file=path,None

    def __enter__(self):
        self.file=self.path.open('a+b')
        if os.fstat(self.file.fileno()).st_size==0:
            self.file.write(b'0'); self.file.flush()
        self.file.seek(0)
        try:
            if os.name=='nt':
                import msvcrt
                msvcrt.locking(self.file.fileno(),msvcrt.LK_NBLCK,1)
            else:
                import fcntl
                fcntl.flock(self.file.fileno(),fcntl.LOCK_EX|fcntl.LOCK_NB)
        except OSError as exc:
            self.file.close(); self.file=None
            raise RuntimeError('A Synkai supervisor is already running for this local state') from exc
        return self

    def __exit__(self,*args):
        if self.file is not None:
            self.file.close(); self.file=None
