# -*- coding: utf-8 -*-
import fontinfo
import pml
import util
<<<<<<< HEAD
import math
import misc
=======
# PDF변환할때의 정보인듯
>>>>>>> cliegh/master

from reportlab.pdfgen import canvas
import StringIO
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# users should only use this.
def generate(doc):
    tmp = PDFExporter(doc)
    return tmp.generate()

# An abstract base class for all PDF drawing operations.
class PDFDrawOp:

    # perform PDF drawing operations corresponding to the PML object pmlOp
    # on pdfgen canvas. pe = PDFExporter.
    def draw(self, pmlOp, pageNr, canvas, pe):
        raise Exception("draw not implemented")

class PDFTextOp(PDFDrawOp):
    def draw(self, pmlOp, pageNr, canvas, pe):
        # we need to adjust y position since PDF uses baseline of text as
        # the y pos, but pml uses top of the text as y pos. The Adobe
        # standard Courier family font metrics give 157 units in 1/1000
        # point units as the Descender value, thus giving (1000 - 157) =
        # 843 units from baseline to top of text.

        # http://partners.adobe.com/asn/tech/type/ftechnotes.jsp contains
        # the "Font Metrics for PDF Core 14 Fonts" document.

        x = pe.x(pmlOp.x)
        y = pe.y(pmlOp.y) - 0.843 * pmlOp.size

        if pe.doc.tocs and pmlOp.toc:
            key = "id%d" % id(pmlOp)
            canvas.bookmarkPage(key,fit="XYZ",left=pe.x(pmlOp.x),top=pe.y(pmlOp.y))
            canvas.addOutlineEntry(pmlOp.toc.text,key)

        newFont = (pe.getFontNr(pmlOp.flags), pmlOp.size)
        if newFont != pe.currentFont:
            canvas.setFont(*newFont)
            pe.currentFont = newFont

	if pmlOp.angle is None or pmlOp.angle == 0.0:
            canvas.drawString(x,y,pmlOp.text)
        else:
            canvas.saveState()
            canvas.translate(x,y)
            canvas.rotate(pmlOp.angle)
            canvas.drawString(0,0,pmlOp.text)
            canvas.restoreState()

        if pmlOp.flags & pml.UNDERLINED:

            undLen = fontinfo.getMetrics(pmlOp.flags).getTextWidth(
                pmlOp.text, pmlOp.size)

            # all standard PDF fonts have the underline line 100 units
            # below baseline with a thickness of 50
            undY = y - 0.1 * pmlOp.size

            canvas.setLineWidth(0.05 * pmlOp.size)
            canvas.line(x, undY, x + undLen, undY)

class PDFLineOp(PDFDrawOp):
    def draw(self, pmlOp, pageNr, canvas, pe):
        p = pmlOp.points

        pc = len(p)

        if pc < 2:
            print "LineOp contains only %d points" % pc

            return

        canvas.setLineWidth(pe.mm2points(pmlOp.width))

        path = canvas.beginPath()

        path.moveTo(*pe.xy(p[0]))

        for point in p[1:]:
            path.lineTo(*pe.xy(point))

        if pmlOp.isClosed:
            path.close()

        canvas.drawPath(path)

class PDFRectOp(PDFDrawOp):
    def draw(self, pmlOp, pageNr, canvas, pe):
        if pmlOp.lw != -1:
            canvas.setLineWidth(pe.mm2points(pmlOp.lw))

        path = canvas.beginPath()

        path.rect(pe.x(pmlOp.x),
            pe.y(pmlOp.y) - pe.mm2points(pmlOp.height),
            pe.mm2points(pmlOp.width), pe.mm2points(pmlOp.height))

        if pmlOp.fillType == pml.STROKE:
            canvas.drawPath(path)
        elif pmlOp.fillType == pml.FILL:
            canvas.drawPath(path, stroke=0, fill=1)
        elif pmlOp.fillType == pml.STROKE_FILL:
            canvas.drawPath(path, stroke=1, fill=1)
        else:
            print "Invalid fill type for RectOp"

class PDFQuarterCircleOp(PDFDrawOp):
<<<<<<< HEAD
    def draw(self, pmlOp, pageNr, canvas, pe):
        canvas.setLineWidth(pe.mm2points(pmlOp.width))
        path = canvas.beginPath()
        path.arc( pe.x(pmlOp.x - pmlOp.radius), pe.y(pmlOp.y - pmlOp.radius),
               pe.x(pmlOp.x + pmlOp.radius), pe.y(pmlOp.y + pmlOp.radius),
               startAng=pmlOp.startAngle, extent=90)
        canvas.drawPath(path)

class PDFSetFillGray(PDFDrawOp):
    def draw(self, pmlOp, pageNr, canvas, pe):
        canvas.setFillGray(pmlOp.grayvalue)

class PDFSetFillRGB(PDFDrawOp):
    def draw(self, pmlOp, pageNr, canvas, pe):
        canvas.setFillColorRGB(*pmlOp.color)

class PDFSetStrokeGray(PDFDrawOp):
    def draw(self, pmlOp, pageNr, canvas, pe):
        canvas.setStrokeGray(pmlOp.grayvalue)

class PDFSetDash(PDFDrawOp):
    def draw(self, pmlOp, pageNr, canvas, pe):
        canvas.setDash(pmlOp.dashArray, pmlOp.phase)
=======
    def draw(self, pmlOp, pageNr, output, pe):
        sX = pmlOp.flipX and -1 or 1
        sY = pmlOp.flipY and -1 or 1

        # The traditional constant is: 0.552284749
        # however, as described here:
        # http://spencermortensen.com/articles/bezier-circle/,
        # this has a maximum radial drift of 0.027253%.
        # The constant calculated by Spencer Mortensen
        # has a max. drift of 0.019608% which is 28% better.
        A = pmlOp.radius * 0.551915024494

        output += "%f w\n"\
                  "%s m\n" % (pe.mm2points(pmlOp.width),
                              pe.xy((pmlOp.x - pmlOp.radius * sX, pmlOp.y)))

        output += "%f %f %f %f %f %f c\n" % (
            pe.x(pmlOp.x - pmlOp.radius * sX), pe.y(pmlOp.y - A * sY),
            pe.x(pmlOp.x - A * sX), pe.y(pmlOp.y - pmlOp.radius * sY),
            pe.x(pmlOp.x), pe.y(pmlOp.y - pmlOp.radius * sY))

        output += "S\n"

class PDFArbitraryOp(PDFDrawOp):
    def draw(self, pmlOp, pageNr, output, pe):
        output += "%s\n" % pmlOp.cmds
>>>>>>> cliegh/master

# used for keeping track of used fonts
class FontInfo:
    def __init__(self, name):
        self.name = name

        # font number (the name in the /F PDF command), or -1 if not used
        self.number = -1

class PDFExporter:
    def __init__(self, doc):
        # pml.Document
        self.doc = doc
        self.stringIO = StringIO.StringIO()
        self.canvas = canvas.Canvas(self.stringIO,
            pagesize=(self.mm2points(self.doc.w), self.mm2points(self.doc.h)),
            pageCompression=1)

    # generate PDF document and return it as a string
    def generate(self):
        #lsdjflksj = util.TimerDev("generate")
        doc = self.doc

        # fast lookup of font information
        self.fonts = {
            pml.COURIER : FontInfo("Courier"),
            pml.COURIER | pml.BOLD: FontInfo("Courier-Bold"),
            pml.COURIER | pml.ITALIC: FontInfo("Courier-Oblique"),
            pml.COURIER | pml.BOLD | pml.ITALIC:
              FontInfo("Courier-BoldOblique"),

            pml.HELVETICA : FontInfo("Helvetica"),
            pml.HELVETICA | pml.BOLD: FontInfo("Helvetica-Bold"),
            pml.HELVETICA | pml.ITALIC: FontInfo("Helvetica-Oblique"),
            pml.HELVETICA | pml.BOLD | pml.ITALIC:
              FontInfo("Helvetica-BoldOblique"),

            pml.TIMES_ROMAN : FontInfo("Times-Roman"),
            pml.TIMES_ROMAN | pml.BOLD: FontInfo("Times-Bold"),
            pml.TIMES_ROMAN | pml.ITALIC: FontInfo("Times-Italic"),
            pml.TIMES_ROMAN | pml.BOLD | pml.ITALIC:
              FontInfo("Times-BoldItalic"),
            }

        self.setInfo()

        if doc.tocs and doc.showTOC:
            self.canvas._doc.Catalog.showOutline()

        if doc.defPage != -1:
            self.canvas._doc.Catalog.OpenAction = self.canvas._bookmarkReference("launch_page")

        self.genPages()

        return self.genPDF()

    def setInfo(self):
        version = self.doc.version
        trelbyVersion = "Trelby %s" % version

        self.canvas._doc.info.creator = trelbyVersion
        self.canvas._doc.info.producer = trelbyVersion

        if self.doc.uniqueId:
            self.canvas._doc.info.keywords = self.doc.uniqueId

    # generate a single page
    def genPages(self):
        for (pageNr, page) in enumerate(self.doc.pages):
            self.currentFont = None

            for op in page.ops:
                op.pdfOp.draw(op, pageNr, self.canvas, self)

            if self.doc.defPage == pageNr:
                self.canvas.bookmarkPage("launch_page",fit="XYZ")

            self.canvas.showPage()

    # generate PDF file and return it as a string
    def genPDF(self):
        self.canvas.save()
        return self.stringIO.getvalue()

    # get font number to use for given flags. also creates the PDF object
    # for the font if it does not yet exist.
    def getFontNr(self, flags):
        # the "& 15" gets rid of the underline flag
        fi = self.fonts.get(flags & 15)

        if not fi:
            print "PDF.getfontNr: invalid flags %d" % flags

            return 0

        if fi.number == -1:
            fi.number = 1

            # the "& 15" gets rid of the underline flag
            pfi = self.doc.fonts.get(flags & 15)

            if pfi and pfi.fontProgram:
                    pdfmetrics.registerFont(TTFont(fi.name,
                        StringIO.StringIO(pfi.fontProgram)))
            elif misc.isWindows:
                #on Windows attempt to use platform-specific defaults
                winFonts = {
                    pml.COURIER : "cour.ttf",
                    pml.COURIER | pml.BOLD: "courbd.ttf",
                    pml.COURIER | pml.ITALIC: "couri.ttf",
                    pml.COURIER | pml.BOLD | pml.ITALIC:
                      "courbi.ttf",

                    pml.HELVETICA : "arial.ttf",
                    pml.HELVETICA | pml.BOLD: "arialbd.ttf",
                    pml.HELVETICA | pml.ITALIC: "ariali.ttf",
                    pml.HELVETICA | pml.BOLD | pml.ITALIC:
                      "arialbi.ttf",

                    pml.TIMES_ROMAN : "times.ttf",
                    pml.TIMES_ROMAN | pml.BOLD: "timesbd.ttf",
                    pml.TIMES_ROMAN | pml.ITALIC: "timesi.ttf",
                    pml.TIMES_ROMAN | pml.BOLD | pml.ITALIC:
                      "timesbi.ttf",
                    }

                filename = winFonts.get(flags & 15)
                if filename:
                    fullPath = r'C:\\Windows\\Fonts\\' + filename
                    try:
                        pdfmetrics.registerFont(TTFont(fi.name,
                            fullPath))
                    except:
                        pass

        return fi.name

    # convert mm to points (1/72 inch).
    def mm2points(self, mm):
        # 2.834 = 72 / 25.4
        return mm * 2.83464567

    # convert x coordinate
    def x(self, x):
        return self.mm2points(x)

    # convert y coordinate
    def y(self, y):
        return self.mm2points(self.doc.h - y)

    # convert xy, which is (x, y) pair, into PDF coordinates
    def xy(self, xy):
        x = self.x(xy[0])
        y = self.y(xy[1])

        return (x, y)
