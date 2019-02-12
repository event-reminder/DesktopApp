from PyQt5.QtCore import QRunnable, QThreadPool


class BackgroundProcess(QRunnable):
    def __init__(self, target, args):
        QRunnable.__init__(self)
        self.target = target
        self.args = args

    def run(self):
        self.target(*self.args)

    def start(self):
        QThreadPool.globalInstance().start(self)
        # QThreadPool().globalInstance().start(self)
