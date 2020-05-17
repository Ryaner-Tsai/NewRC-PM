from django.shortcuts import render, redirect
from django.contrib import auth
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.contrib import messages
from .ForcedObject import section
import numpy as np
from numpy import array as ar
from matplotlib import pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg
from django.http import HttpResponse
import simplejson as json
# Create your views here.
def home(request):

    if request.method == 'POST' and request.POST.get('inputTextarea'):
        #Section
        InputDataValue = request.POST['inputTextarea'].split()
        InputSectionValue = InputDataValue[0:8]
        InputSectionKey = ['Dx', 'Dy', 'fc', 'fy', 'db', 'As', 'BarXCoord', 'BarYCoord']
        InputSectionDict = {Keyi: Valuei for Keyi, Valuei in zip(InputSectionKey, InputSectionValue)}
        InputSectionDict['BarXCoord'] = InputSectionDict['BarXCoord'].split(',')
        InputSectionDict['BarYCoord'] = InputSectionDict['BarYCoord'].split(',')
        for Key, Value in InputSectionDict.items():
            if type(Value) == list:
                InputSectionDict[Key] = [float(Valuei) for Valuei in Value]
            else:
                InputSectionDict[Key] = float(Value)
        InputSectionDict['fy'] = [InputSectionDict['fy'] for _ in range(len(InputSectionDict['BarXCoord']))]
        InputSectionDict['As'] = [InputSectionDict['As'] for _ in range(len(InputSectionDict['BarXCoord']))]
        Section = section(InputSectionDict['Dx'], InputSectionDict['Dy'], InputSectionDict['fc'],
                              ar(InputSectionDict['BarXCoord']), ar(InputSectionDict['BarYCoord']),
                              ar(InputSectionDict['As']),
                              ar(InputSectionDict['fy']), Angle=0)
        StackedCombineCompressionForce = ar([])
        StackedMxx = ar([])
        StackedMyy = ar([])
        i = 0
        for __, _ in zip(*Section.strained()):
            if Section.Concrete.StressPolygon is not None:
                Section.stress_nonoverlapping()
                StackedCombineCompressionForce = np.hstack([StackedCombineCompressionForce, ar(
                    [Section.ForceSystem.CombineCompressionForce * Section.Reinforcements.Phi])])
                StackedMxx = np.hstack([StackedMxx, ar([Section.ForceSystem.Mxx * Section.Reinforcements.Phi])])
                StackedMyy = np.hstack([StackedMyy, ar([Section.ForceSystem.Myy * Section.Reinforcements.Phi])])
            i += 1
            # (self, B, H, fc, X, Y, As, Fy, Angle=0, IsDegree=1, TransType='Tie')

        InputLoadValue = InputDataValue[8:]
        Pu = [None] * len(InputLoadValue)
        Mux = [None] * len(InputLoadValue)
        for i, InputLoadValuei in enumerate(InputLoadValue):
            LoadiList = InputLoadValuei.split(';')
            Pu[i] = float(LoadiList[1])
            Mux[i] = float(LoadiList[2])
        return render(request, 'accounts/home.html', {'Mxx': StackedMxx/1000/100, 'P': StackedCombineCompressionForce/1000, 'Pu': Pu, 'Mux': Mux})
    else:
        return render(request, 'accounts/home.html')
