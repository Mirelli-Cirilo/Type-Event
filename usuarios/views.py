from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.messages import constants
from django.contrib.auth import authenticate, login
from django.urls import reverse

def cadastro(request):
    if request.method == 'GET':
        return render(request, 'cadastro.html')
    if request.method == 'POST':

        username = request.POST.get('username')
        email = request.POST.get('email')
        senha = request.POST.get('senha')
        confirmar_senha = request.POST.get('confirmar_senha')

        if senha != confirmar_senha:
            messages.add_message(request, constants.ERROR, 'Digite a senha corretamente')
            return redirect(reverse('cadastro'))
        
        user = User.objects.filter(username=username)

        if user:
            messages.add_message(request, constants.ERROR, 'Este usuário já existe!')
            return redirect(reverse('cadastro'))
        
        user = User.objects.create_user(username=username, email=email, password=senha)
        
        messages.add_message(request, constants.SUCCESS, 'Cadastro concluído com sucesso!')

        return redirect(reverse('login'))
    
def loginPage(request):

    if request.method == 'GET':
        return render(request, 'login.html')
    
    elif request.method == 'POST':
        username = request.POST.get('username')
        senha = request.POST.get('senha')

        user = authenticate(username=username, password=senha)

        if user:
            login(request, user)
            return redirect(reverse('novo_evento'))
        
        else:
            messages.add_message(request, constants.ERROR, 'Nome de usúario ou senha estão incorretos')
            return redirect(reverse('login'))