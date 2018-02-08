# -*- coding: utf-8 -*-
import gutil
import misc
import util

import characterreport
import locationreport
import scenereport
import scriptreport

import wx
#화면상의 메뉴에서 Report 를 담당하는 부분 (통합 부분)
def genSceneReport(mainFrame, sp):
    report = scenereport.SceneReport(sp)

    dlg = misc.CheckBoxDlg(mainFrame, "Report type", report.inf,
        "Information to include:", False)

    ok = False
    if dlg.ShowModal() == wx.ID_OK:
        ok = True

    dlg.Destroy()

    if not ok:
        return

    data = report.generate()

    gutil.showTempPDF(data, sp.cfgGl, mainFrame)

def genLocationReport(mainFrame, sp):
    report = locationreport.LocationReport(scenereport.SceneReport(sp))

    dlg = misc.CheckBoxDlg(mainFrame, "Report type", report.inf,
        "Information to include:", False)

    ok = False
    if dlg.ShowModal() == wx.ID_OK:
        ok = True

    dlg.Destroy()

    if not ok:
        return

    data = report.generate()

    gutil.showTempPDF(data, sp.cfgGl, mainFrame)

def genCharacterReport(mainFrame, sp):
    report = characterreport.CharacterReport(sp)

    if not report.cinfo:
        wx.MessageBox("No characters speaking found.",
                      "Error", wx.OK, mainFrame)

        return

    charNames = [character.name for character in report.cinfo]
    charCheckBoxItems = list([misc.CheckBoxItem(name) for name in charNames])

    dlg = misc.CheckBoxDlg(mainFrame, "Report type", report.inf,
        "Information to include:", False, charCheckBoxItems,
        "Characters to include:", True)

    ok = False
    if dlg.ShowModal() == wx.ID_OK:
        ok = True

        for i in range(len(report.cinfo)):
            report.cinfo[i].include = charCheckBoxItems[i].selected

    dlg.Destroy()

    if not ok:
        return

    data = report.generate()

    gutil.showTempPDF(data, sp.cfgGl, mainFrame)

def genScriptReport(mainFrame, sp):
    report = scriptreport.ScriptReport(sp)
    data = report.generate()

    gutil.showTempPDF(data, sp.cfgGl, mainFrame)
