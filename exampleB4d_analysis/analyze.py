#!/snap/bin/pyroot
# was: #!/usr/bin/python3
# Ne 5. března 2023, 22:16:34 CET

#from __future__ import print_function

import ROOT
from math import sqrt, pow, log, exp
import os, sys, getopt

cans = []
stuff = []


##########################################

def DrawChi2(fun):
    chi2 = fun.GetChisquare()
    ndf = fun.GetNDF()
    txt = ROOT.TLatex(0.60, 0.85, '#chi^{2}/ndf=' + '{:1.2f}/{:1.0f}'.format(chi2,ndf))
    txt.SetNDC()
    txt.SetTextSize(0.034)
    txt.Draw()
    return txt
##########################################



##########################################
##########################################
##########################################
# https://www.tutorialspoint.com/python/python_command_line_arguments.htm

def main(argv):

    ROOT.gStyle.SetPalette(ROOT.kSolar)
    #ROOT.gStyle.SetPalette(ROOT.kOcean)
    ROOT.gStyle.SetOptTitle(0)

    Es = [1, 2, 3, 4, 5, 7, 10, 15, 20, 25, 30, 40, 50]
    treename = 'B4'
    hs = {}
    rfs = []
    nbs = 300
    e1 = 0.
    e2 = 3.


    canname = 'help'
    hcan = ROOT.TCanvas(canname, canname, 900, 900, 200, 200)
    #cans.append(can)
    for E in Es:
        print('*** Processing E={}GeV ***'.format(E))
        rfname = 'tree_el_{}GeV.root'.format(E)
        rfile = ROOT.TFile(rfname, 'read')
        rfs.append(rfile)
        tree = rfile.Get(treename)
        hname = 'h_Egap_{}'.format(E)
        h = ROOT.TH1D(hname, hname + ';E_{dep} [GeV]', nbs, e1, e2)
        print(tree)
        tree.Draw('Egap / 1000. >> {}'.format(hname))
        hs[E] = h
    opt = 'hist plc pfc'
    bopt = 'hist plc pfc'
    print('Drawing...')
    gr_reso = ROOT.TGraphErrors()
    gr_Edep = ROOT.TGraphErrors()
    ip = 0

    canname = 'Edep_el'
    ecan = ROOT.TCanvas(canname, canname, 0, 0, 1000, 800)
    cans.append(ecan)
    ROOT.gPad.SetGridx(1)
    ROOT.gPad.SetGridy(1)

    
    for E in hs:
        h = hs[E]
        print(h)
        h.SetStats(0)
        hcan.cd()
        h.Draw(bopt)
        h.GetXaxis().SetMoreLogLabels()
        h.GetYaxis().SetMoreLogLabels()
        ROOT.gPad.Update()
        
        h.SetFillColorAlpha(h.GetFillColor(), 0.3)
        ecan.cd()
        h.Draw(opt)
        opt = 'hist same plc pfc'
        
        gr_reso.SetPoint(ip, E, h.GetStdDev() / E)
        gr_reso.SetPointError(ip, 0, h.GetStdDevError() / E )

        gr_Edep.SetPoint(ip, E, h.GetMean())
        gr_Edep.SetPointError(ip, 0, h.GetMeanError())
        
        ip = ip+1

    ROOT.gPad.RedrawAxis()
    ROOT.gPad.Update()

    ROOT.gStyle.SetPadLeftMargin(0.15)
    
    canname = 'Energy_el'
    gcan = ROOT.TCanvas(canname, canname, 100, 100, 1325, 600)
    gcan.Divide(2,1)
    cans.append(gcan)
    
    gcan.cd(1)
    ROOT.gPad.SetGridx(1)
    ROOT.gPad.SetGridy(1)

    gr_Edep.SetMarkerStyle(20)
    gr_Edep.SetMarkerSize(1)
    gr_Edep.SetMarkerColor(ROOT.kRed)
    gr_Edep.SetLineColor(ROOT.kBlack)
    gr_Edep.SetLineWidth(1)
    gr_Edep.SetLineStyle(1)
    gr_Edep.Draw('AP')
    gr_Edep.GetYaxis().SetRangeUser(0., 3.)
    gr_Edep.GetYaxis().SetTitle('E_{dep} [GeV]')
    gr_Edep.GetXaxis().SetTitle('E [GeV]')
    fun1 = ROOT.TF1('fun1', '[0] + [1]*x', e1, e2)
    fun1.SetLineWidth(1)
    fun1.SetLineStyle(2)
    gr_Edep.Fit('fun1')
    txt1 = DrawChi2(fun1)
    ROOT.gPad.RedrawAxis()
    ROOT.gPad.Update()
    
    gcan.cd(2)
    ROOT.gPad.SetGridx(1)
    ROOT.gPad.SetGridy(1)

    gr_reso.SetMarkerStyle(20)
    gr_reso.SetMarkerSize(1)
    gr_reso.SetMarkerColor(ROOT.kRed)
    gr_reso.SetLineColor(ROOT.kBlack)
    gr_reso.SetLineWidth(1)
    gr_reso.SetLineStyle(1)
    gr_reso.Draw('AP')
    gr_reso.GetYaxis().SetRangeUser(0., 0.0210)
    gr_reso.GetYaxis().SetTitle('#sigma / E')
    gr_reso.GetXaxis().SetTitle('E [GeV]')
    fun2 = ROOT.TF1('fun2', '[0] + [1]/sqrt(x)', e1, e2)
    fun2.SetLineWidth(1)
    fun2.SetLineStyle(2)
    gr_reso.Fit('fun2')
    txt2 = DrawChi2(fun2)
    ROOT.gPad.RedrawAxis()
    ROOT.gPad.Update()


    for can in cans:
        can.cd()
        can.Update()
        can.Print(can.GetName() + '.png')
        can.Print(can.GetName() + '.pdf')

    ecan.SetGridx(1)
    ecan.SetGridy(1)
    ecan.SetLogx(1)
    ecan.SetLogy(1)
    ecan.Update()
    ecan.Print(ecan.GetName() + '_logx.png')
    ecan.Print(ecan.GetName() + '_logx.pdf')

    ecan.SetLogx(0)
    ecan.SetLogy(0)
    ecan.Update()
    
    ROOT.gApplication.Run()
    return


###################################
###################################
###################################

if __name__ == "__main__":
    # execute only if run as a script"
    main(sys.argv)
    
###################################
###################################
###################################

