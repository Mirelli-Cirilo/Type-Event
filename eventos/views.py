from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Evento, Certificado
from django.http import Http404, HttpResponse
from django.urls import reverse
from django.contrib import messages
from django.contrib.messages import constants
import csv
from secrets import token_urlsafe
import os
from django.conf import settings
from PIL import Image, ImageDraw, ImageFont
import sys
from io import BytesIO  
from django.core.files.uploadedfile import InMemoryUploadedFile

@login_required
def novo_evento(request):
    
    if request.method == 'GET':
        return render(request, 'novo_evento.html')
    
    elif request.method == 'POST':
        nome = request.POST.get('nome')
        descricao = request.POST.get('descricao')
        data_inicio = request.POST.get('data_inicio')
        data_termino = request.POST.get('data_termino')
        carga_horaria = request.POST.get('carga_horaria')

        cor_principal = request.POST.get('cor_principal')
        cor_secundaria = request.POST.get('cor_secundaria')
        cor_fundo = request.POST.get('cor_fundo')
        
        logo = request.FILES.get('logo_evento')

        evento = Evento(
            dono=request.user,
            nome=nome,
            descricao=descricao,
            data_inicio=data_inicio,
            data_termino=data_termino,
            carga_horaria=carga_horaria,
            cor_principal=cor_principal,
            cor_secundaria=cor_secundaria,
            cor_fundo=cor_fundo,
            logo_evento=logo,
        )

        evento.save()

        messages.add_message(request, constants.SUCCESS, 'Evento cadastrado com sucesso.')

        return redirect(reverse('novo_evento'))
    
@login_required    
def gerenciar_evento(request):
    
    if request.method == 'GET':
        nome = request.GET.get('nome')
        
        eventos = Evento.objects.filter(dono=request.user)
        # realizar filtro por data
        if nome:
            eventos = eventos.filter(nome__icontains=nome)
               
        return render(request, 'gerenciar_evento.html', {'eventos': eventos})
    
@login_required
def inscrever_evento(request, pk):

    evento = get_object_or_404(Evento, id=pk)
    
    if request.method == 'GET':
        
        return render(request, 'inscrever_evento.html', {'evento': evento})
        
    
    elif request.method == 'POST':
         
        part = Evento.objects.get(id=pk)

        if part == None:
            evento.participantes.add(request.user)

            evento.save()

            messages.add_message(request, constants.SUCCESS, 'Inscrição Concluída!')

            return redirect(f'/eventos/inscrever_evento/{pk}')
        
        messages.add_message(request, constants.INFO, 'VOCÊ JÁ ESTÁ INSCRITO!')

        return redirect(f'/eventos/inscrever_evento/{pk}')


def listar_participantes(request, pk):
    

    evento = get_object_or_404(Evento, id=pk)
    if evento.dono != request.user:
        raise Http404('Esse evento não é seu!')

    if request.method == 'GET':
        participantes = evento.participantes.all()[:3]

       
        return render( request, 'listar_participantes.html', {'evento':evento, 'participantes': participantes})
    
def gerar_csv(request, pk):
    
    evento = get_object_or_404(Evento, id=pk)
    if evento.dono != request.user:
        raise Http404('Esse evento não é seu')
    participantes = evento.participantes.all()
    
    token = f'{token_urlsafe(6)}.csv'
    path = os.path.join(settings.MEDIA_ROOT, token)

    with open(path, 'w') as arq:
        writer = csv.writer(arq, delimiter=",")
        for participante in participantes:
            x = (participante.username, participante.email)
            writer.writerow(x)

    return redirect(f'/media/{token}')
    
def certificado_evento(request, pk):
    evento = get_object_or_404(Evento, id=pk)
    if evento.dono != request.user:
        raise Http404('Esse evento não é seu')
    
    elif request.method == 'GET':
        qtd_certificados = evento.participantes.all().count() - Certificado.objects.filter(evento=evento).count()

        return render(request, 'certificado_evento.html', {'qtd_certificados': qtd_certificados, 'evento': evento})

def gerar_certificado(request, pk):
    evento = get_object_or_404(Evento, id=pk)
    if evento.dono != request.user:
        raise Http404('Esse evento não é seu')

    path_template = os.path.join(settings.BASE_DIR, 'templates/static/evento/images/template_certificado.png')
    path_fonte = os.path.join(settings.BASE_DIR, 'templates/static/fontes/arimo.ttf')
    for participante in evento.participantes.all(): 

        img = Image.open(path_template)
        path_template = os.path.join(settings.BASE_DIR, 'templates/static/evento/images/template_certificado.png')
        draw = ImageDraw.Draw(img)
        fonte_nome = ImageFont.truetype(path_fonte, 60)
        fonte_info = ImageFont.truetype(path_fonte, 40)
        draw.text((230, 651), f"{participante.username}", font=fonte_nome, fill=(0, 0, 0))
        draw.text((761, 782), f"{evento.nome}", font=fonte_info, fill=(0, 0, 0))
        draw.text((816, 849), f"{evento.carga_horaria} horas", font=fonte_info, fill=(0, 0, 0))
        output = BytesIO()
        img.save(output, format="PNG", quality=100)
        output.seek(0)
        img_final = InMemoryUploadedFile(output,
                                        'ImageField',
                                        f'{token_urlsafe(8)}.png',
                                        'image/jpeg',
                                        sys.getsizeof(output),
                                        None)
        certificado_gerado = Certificado(
            certificado=img_final,
            participante=participante,
            evento=evento,
        )
        certificado_gerado.save()
    
    messages.add_message(request, constants.SUCCESS, 'Certificados gerados')
    return redirect(reverse('certificado_evento', kwargs={'pk': evento.id}))   

def procurar_certificado(request, pk):
    evento = get_object_or_404(Evento, id=pk)
    if evento.dono != request.user:
        raise Http404('Esse evento não é seu')
    
    email = request.POST.get('email')

    certificado = Certificado.objects.filter(evento=evento).filter(participante__email=email).first()

    if not certificado:
        messages.add_message(request, constants.WARNING, 'Certificado não encontrado')
        return redirect(reverse('certificado_evento', kwargs={'pk': evento.id}))
    
    return redirect(certificado.certificado.url)