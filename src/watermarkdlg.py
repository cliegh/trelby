import pdf
import pml
import random
import util

import wx

# 워터마크도구 대화상자
# 이 도구를 사용하면 워터 마크가 삽입 된 여러 PDF를 생성하여 여러 사람에게 배포 할 수 있습니다.
# 워터마크는 당신이 리더들에게 이 스크립트가 보기전용이고 배포되어선 안된다는걸 알리는데 유용합니다.
# 디렉토리, 파일 이름 접두어 및 워터 마크 글꼴 크기와 같은 세부 정보를 입력하십시오. 
# 파일 당 두 줄의 워터 마크를 가질 수 있으며 첫 번째 줄은 모든 파일에서 공통적입니다. 각 파일의 두 번째 줄은 "워터 마크"입력 상자 아래 목록으로 제공됩니다.
# PDF의 워터 마크는 밝은 회색 색상의 경사 텍스트로 페이지의 배경으로 적용됩니다. 워터 마크는 모든 페이지에 적용됩니다.
# 고유 한 ID는 PDF 파일의 두 번째 소스 (워터 마크가 제거 된 채 누출 된 경우)로 PDF 파일의 '키워드'메타 데이터에도 저장됩니다.

class WatermarkDlg(wx.Dialog):
    # sp - PDF를 생성하는데 사용되는 스크린플레이 오브젝트
    # prefix - PDF파일의 앞에붙는이름. (유니코드)
    def __init__(self, parent, sp, prefix):
        wx.Dialog.__init__(self, parent, -1, "Watermarked PDFs generator",
                           style = wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER)# wx.dialog 초기화

        self.frame = parent
        self.sp = sp

        vsizer = wx.BoxSizer(wx.VERTICAL)

        vsizer.Add(wx.StaticText(self, -1, "Directory to save in:"), 0) # 디렉토리 지정해주는 text 박스 생성.
        hsizer = wx.BoxSizer(wx.HORIZONTAL)
        self.dirEntry = wx.TextCtrl(self, -1)
        hsizer.Add(self.dirEntry, 1, wx.EXPAND)

        btn = wx.Button(self, -1, "Browse") # 로컬의 탐색기창을 띄워주는 버튼
        wx.EVT_BUTTON(self, btn.GetId(), self.OnBrowse)
        hsizer.Add(btn, 0, wx.ALIGN_CENTER_VERTICAL | wx.LEFT, 10)

        vsizer.Add(hsizer, 0, wx.EXPAND | wx.TOP | wx.BOTTOM, 5)
        vsizer.Add(wx.StaticText(self, -1, "Filename prefix:"), 0) # 앞에붙을 이름 추가
        self.filenamePrefix = wx.TextCtrl(self, -1, prefix)
        vsizer.Add(self.filenamePrefix, 0, wx.EXPAND | wx.BOTTOM, 5)

        vsizer.Add(wx.StaticText(self, -1, "Watermark font size:"), 0) # 워터마크 폰트 크기 섲렁
        self.markSize = wx.SpinCtrl(self, -1, size=(60, -1))
        self.markSize.SetRange(20, 80)
        self.markSize.SetValue(40)
        vsizer.Add(self.markSize, 0, wx.BOTTOM, 5)

        vsizer.Add(wx.StaticLine(self, -1), 0, wx.EXPAND | wx.TOP | wx.BOTTOM, 5)

        vsizer.Add(wx.StaticText(self, -1, "Common mark:"), 0) # Common mark란에 디폴트값으로 Confidential
        self.commonMark = wx.TextCtrl(self, -1, "Confidential")
        vsizer.Add(self.commonMark, 0, wx.EXPAND| wx.BOTTOM, 5)

        vsizer.Add(wx.StaticText(self, -1, "Watermarks (one per line):")) # 큰 사이즈 공간 주고. 워터마크 작성
        self.itemsEntry = wx.TextCtrl(
            self, -1, style = wx.TE_MULTILINE | wx.TE_DONTWRAP,
            size = (300, 200))
        vsizer.Add(self.itemsEntry, 1, wx.EXPAND)

        hsizer = wx.BoxSizer(wx.HORIZONTAL)
        closeBtn = wx.Button(self, -1, "Close") # 클로즈버튼
        hsizer.Add(closeBtn, 0)
        hsizer.Add((1, 1), 1)
        generateBtn = wx.Button(self, -1, "Generate PDFs") # 실행버튼
        hsizer.Add(generateBtn, 0)

        vsizer.Add(hsizer, 0, wx.EXPAND | wx.TOP, 10)

        util.finishWindow(self, vsizer)

        wx.EVT_BUTTON(self, closeBtn.GetId(), self.OnClose)
        wx.EVT_BUTTON(self, generateBtn.GetId(), self.OnGenerate)

        self.dirEntry.SetFocus()

    @staticmethod
    def getUniqueId(usedIds): # 16진수?의 유니크한 uid를 생성한다.
        while True:
            uid = ""

            for i in range(8):
                uid += '%02x' % random.randint(0, 255)

            if uid in usedIds:
                continue

            usedIds.add(uid)

            return uid

    def OnGenerate(self, event): #pml을 이용해 워터마크가 있는 pdf 생성.
        watermarks = self.itemsEntry.GetValue().split("\n") # split 괄호안의 구분자 \n을 기준으로 문자열을 나누어 줌.
        common = self.commonMark.GetValue()
        directory = self.dirEntry.GetValue()
        fontsize = self.markSize.GetValue()
        fnprefix = self.filenamePrefix.GetValue()

        watermarks = set(watermarks) # 집합자료형 set. 나누어진 문자열을 집합으로 만들어줌.

        # keep track of ids allocated so far, just on the off-chance we 
        # randomly allocated the same id twice
        # 우리가 동일한 아이디를 두번 할당한것에대해 기회가 있을때 지금까지의 id들을 추적하시오
        usedIds = set()

        if not directory: # 디렉토리를 지정하지 않았을때
            wx.MessageBox("Please set directory.", "Error", wx.OK, self)
            self.dirEntry.SetFocus()
            return

        count = 0

        for item in watermarks: #
            s = item.strip()

            if not s:
                continue

            basename = item.replace(" ", "-")
            fn = directory + "/" + fnprefix + '-' + basename + ".pdf" #filename에 prefix 붙이고 뒤에 .pdf 붙임
            pmldoc = self.sp.generatePML(True)

            ops = []

            # almost-not-there gray
            ops.append(pml.PDFOp("0.85 g")) # 아마 color 지정. 그레이로

            if common:
                wm = pml.TextOp(
                    util.cleanInput(common),
                    self.sp.cfg.marginLeft + 20, self.sp.cfg.paperHeight * 0.45,
                    fontsize, pml.BOLD, angle = 45)
                ops.append(wm)

            wm = pml.TextOp(
                util.cleanInput(s),
                self.sp.cfg.marginLeft + 20, self.sp.cfg.paperHeight * 0.6,
                fontsize, pml.BOLD, angle = 45)
            ops.append(wm)

            # ...and back to black
            ops.append(pml.PDFOp("0.0 g"))

            for page in pmldoc.pages:
                page.addOpsToFront(ops)

            pmldoc.uniqueId = self.getUniqueId(usedIds)

            pdfdata = pdf.generate(pmldoc)

            if not util.writeToFile(fn, pdfdata, self):
                wx.MessageBox("PDF generation aborted.", "Error", wx.OK, self)
                return
            else:
                count += 1

        if count > 0:
            wx.MessageBox("Generated %d files in directory %s." %
                          (count, directory), "PDFs generated",
                          wx.OK, self)
        else:
            wx.MessageBox("No watermarks specified.", "Error", wx.OK, self)

    def OnClose(self, event): #클로즈 버튼 동작
        self.EndModal(wx.OK)

    def OnBrowse(self, event): # 브라우즈 버튼 동작
        dlg = wx.DirDialog(
            self.frame, style = wx.DD_NEW_DIR_BUTTON)

        if dlg.ShowModal() == wx.ID_OK:
            self.dirEntry.SetValue(dlg.GetPath())

        dlg.Destroy()
