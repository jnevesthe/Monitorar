#Josemar Neves

from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.utils import timezone
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView, ListView, DetailView
from django.views.generic.edit import DeleteView
#Josemar Neves
from django.contrib.auth import login, logout, authenticate 
from django.contrib.auth.decorators import login_required
from .models import Proprietario, Veiculo, Multa

class List(LoginRequiredMixin, ListView):
    model=Proprietario
    template_name='list.html'
    context_object_name="proprietarios"
    login_url='login'

class Listb(LoginRequiredMixin, ListView):
    model=Veiculo
    template_name='list_v.html'
    context_object_name="veiculos"
    login_url='login'

    
def login_view(request):
    if request.method=="POST":
        username=request.POST.get("username")
        password=request.POST.get("password")
        
        user=authenticate(request,username=username, password=password)
        
        if(user):
            login(request, user)
            #print(user.autorizado)
            return redirect('list_c')                    
            
    return render(request, 'login.html')     
    
def logout_view(request):
    logout(request) 
    return redirect('login')
def pagina_404(request, exception=None):
    return render(request, '404.html', status=404)     
 
@login_required       
def multar(request , pk):
    
    if request.method=='POST':
        valor=request.POST.get('valor')
        local=request.POST.get('local')
        print("ok")
        
        multa=Multa.objects.create(
            veiculo=Veiculo.objects.filter(id=pk).first(),
            valor=valor,
            localizacao=local,
            data=timezone.now(),
            agente=request.user,
	    confirmada=False
	    
        )
        
        #m=Multa.objects.filter(id=multa.id)
        return redirect('confirm', multa.id)
        
    
    v=Veiculo.objects.filter(id=pk).first()
    return render(request, 
    'multar.html', 
    {'v':v}
    
    )


@login_required
def multar1(request , pk):
    if request.method=='POST':
        valor=request.POST.get('valor')
        local=request.POST.get('local')
        print("ok")

        multa=Multa.objects.create(
            veiculo=Veiculo.objects.filter(id=pk).first(),
            valor=valor,
            localizacao=local,
            data=timezone.now(),
            agente=request.user,
            confirmada=False
   	    
        )

        #m=Multa.objects.filter(id=multa.id)
        return redirect('confirm1', multa.id)


    v=Veiculo.objects.filter(id=pk).first()
    return render(request,'multar1.html',{'v':v})
    
    
@login_required          
def confirm(request, pk):
    multa=get_object_or_404(Multa, id=pk)
    return render(request, 'confirm.html', {'multa':multa})

@login_required
def confirmar_multa(request, pk):
    multa = get_object_or_404(Multa, id=pk)

    multa.confirmada = True
    multa.save()

    return redirect('list')

@login_required
def confirmar_multa1(request, pk):
    multa = get_object_or_404(Multa, id=pk)

    multa.confirmada = True
    multa.save()

    return redirect('list_c')

@login_required
def confirm1(request, pk):
    multa=get_object_or_404(Multa, id=pk)
    return render(request, 'confirm1.html', {'multa':multa})

    
class Delete(LoginRequiredMixin, DeleteView):
    model=Multa
    template_name='delete.html'
    context_object_name='multa'    
    success_url=reverse_lazy('list')
    login_url='login'

    def dispatch(self, request, *args, **kwargs):
        multa = self.get_object()

        if multa.confirmada:
            return redirect('list')  # 🚫 bloqueia delete

        return super().dispatch(request, *args, **kwargs)


class Delete1(LoginRequiredMixin, DeleteView):
    model=Multa
    template_name='delete.html'
    context_object_name='multa'
    success_url=reverse_lazy('list_v')
    login_url='login'

    def dispatch(self, request, *args, **kwargs):
        multa = self.get_object()

        if multa.confirmada:
            return redirect('list_c')  # 🚫 bloqueia delete

        return super().dispatch(request, *args, **kwargs)


class Detail(LoginRequiredMixin, DetailView):
    model = Veiculo
    template_name = "detail.html"
    context_object_name = "veiculo"    
    login_url='login'

@login_required  
def get_view(request):
    if request.method == "POST":
        matricula = request.POST.get("matricula", "").strip().upper()
        
        veiculo = Veiculo.objects.filter(matricula__icontains=matricula).first()

        if veiculo:
            proprietario = veiculo.proprietario
            # agora redirecionamos para a página de resultado
            print(proprietario.id)
            
            return redirect('lista', pk=veiculo.id)
            
            """
            return render(request, "resultado.html", {
                "matricula": veiculo.matricula,
                "proprietario": proprietario
            })
           """
           
        else:
            return render(request, "get.html", {
                "erro": "Nenhum veículo encontrado com essa matrícula."
            })

    return render(request, "get.html")


@login_required
def list_v(request):
    # select_related busca o proprietário (ForeignKey)
    # prefetch_related busca todas as multas associadas (Related Name)
    veiculos = Veiculo.objects.select_related('proprietario').prefetch_related('multas').all()
    
    return render(request, 'list_v.html', {'veiculos': veiculos})



@login_required
def logout_confirm(request):
    return render(request, 'logout_confirm.html')


"""
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import cv2, numpy as np
from PIL import Image
import pytesseract


@csrf_exempt
def api_multar(request):
    if request.method != "POST":
        return JsonResponse({"erro": "Apenas POST permitido"}, status=405)

    if "foto" not in request.FILES:
        return JsonResponse({"erro": "Envie uma foto no campo 'foto'"}, status=400)

    # pega o arquivo
    arquivo = request.FILES["foto"].read()

    # transforma em imagem do OpenCV
    np_data = np.frombuffer(arquivo, np.uint8)
    img = cv2.imdecode(np_data, cv2.IMREAD_COLOR)

    # Pré-processamento
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gray = cv2.bilateralFilter(gray, 11, 17, 17)
    _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)

    # OCR - leitura da matrícula
    pil_img = Image.fromarray(thresh)
    texto = pytesseract.image_to_string(pil_img, config="--psm 8")

    # limpa caracteres
    matricula = ''.join(ch for ch in texto.upper() if ch.isalnum())

    if not matricula:
        return JsonResponse({"erro": "Não foi possível ler a matrícula"}, status=400)

    # procura veículo
    veiculo = Veiculo.objects.filter(matricula__icontains=matricula).first()

    if not veiculo:
        return JsonResponse({"erro": "Veículo não encontrado", "matricula": matricula}, status=404)

    # cria multa automaticamente
    multa = Multa.objects.create(
        veiculo=veiculo,
        valor=100,  # defina o valor automático
        localizacao="Detectado pela API",
        data=timezone.now()
        agente=request.user
    )

    return JsonResponse({
        "status": "ok",
        "multa_id": multa.id,
        "matricula": matricula,
        "veiculo": veiculo.id
    })

"""
    


"""

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.utils import timezone
from .models import Veiculo, Multa
from .serializers import MultaSerializer
import cv2, numpy as np
from PIL import Image
import pytesseract

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def api_multar(request):
    if 'foto' not in request.FILES:
        return Response({'erro': 'Sem foto'}, status=400)

    arquivo = request.FILES['foto'].read()
    np_data = np.frombuffer(arquivo, np.uint8)
    img = cv2.imdecode(np_data, cv2.IMREAD_COLOR)

    # Processamento OCR
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)
    pil_img = Image.fromarray(thresh)
    texto = pytesseract.image_to_string(pil_img, config="--psm 8")
    matricula = ''.join(c for c in texto.upper() if c.isalnum())

    if not matricula:
        return Response({'erro': 'Não foi possível ler'}, status=400)

    veiculo = Veiculo.objects.filter(matricula__icontains=matricula).first()
    if not veiculo:
        return Response({'erro': 'Veículo não encontrado', 'matricula': matricula}, status=404)

    multa = Multa.objects.create(
        veiculo=veiculo,
        valor=100,
        localizacao="Radar automático",
        data=timezone.now(),
        agente=request.user
    )

    # Aqui usamos o serializer para devolver a multa
    serializer = MultaSerializer(multa)
    return Response(serializer.data)


"""


   

# Josemar Neves


