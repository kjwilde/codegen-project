from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib import auth

def login(request):
    if request.method == 'POST':
        # logging in, authenticate
        user = auth.authenticate(username=request.POST['username'],password=request.POST['password'])
        if user is not None:
            auth.login(request,user)
            return redirect('projects')
        else:
            return render(request,'accounts/login.html',{'error':'Authentication failed!'})
    else:
        return render(request,'accounts/login.html')

def logout(request):
    # TODO route to home and log out
    if request.method == 'POST':
        auth.logout(request)
        return redirect('home')
