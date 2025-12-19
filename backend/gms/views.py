from django.shortcuts import render

from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view

from .services.gms_client import call_gms_openai

# Create your views here.
@api_view(["GET"])
def gms_test(request):
    text = call_gms_openai(
        "나에게 자존감을 올려줄 말을 해줘"
    )
    return Response({
        "result": text
    })

