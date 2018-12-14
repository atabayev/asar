from django.shortcuts import render
from django.http import HttpResponse
from core.grabber import Grabbing

"""
    grabber   
"""


def grab(request):
    grabber = Grabbing()
    grabber.start()
    return HttpResponse('Grab started!')
