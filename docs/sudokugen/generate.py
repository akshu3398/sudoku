import os
from WebKit.Page import Page
import tempfile
from lib import printpuzzles

class generate(Page):

    def writeHTML(self):
        req = self.request()
        try:
            num = int(self.request().value('number', 1))
        except:
            num = 1
        if num > 50:
            num = 50
        try:
            difficulty = self.request().value('difficulty', 'Any')
        except:
            difficulty = 'Any'
        try:
            perPage = int(self.request().value('perPage', 1))
        except:
            perPage = 1
        solutions = req.hasValue('solutions')
        footer = int(req.value('footer', 1))

        fd, tfile = tempfile.mkstemp()
        os.close(fd)
        printpuzzles.go(tfile, num, difficulty, solutions, footer, perPage)
        f = open(tfile)
        pdf = f.read()
        f.close()
        os.unlink(tfile)
        res = self.response()
        res.setHeader('Content-type', 'application/pdf')
        res.setHeader('Content-Length', '%d' % len(pdf))
        res.setHeader('Content-Disposition', 'attachment; filename=sudoku.pdf')
        res.write(pdf)
