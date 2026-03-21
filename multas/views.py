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
        descricao=request.POST.get('descricao')
        local=request.POST.get('local')
        tipo = request.POST.get('tipo_infracao')
        velocidade = request.POST.get('velocidade') # Virá vazio se não for excesso de velocidade
        print("ok")
        
        multa=Multa.objects.create(
            veiculo=Veiculo.objects.filter(id=pk).first(),
            valor=valor,
            localizacao=local,
            data=timezone.now(),
            tipo=tipo,
	    velocidade=velocidade,
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
        tipo = request.POST.get('tipo_infracao')
        try:
          velocidade = request.POST.get('velocidade') # Virá vazio se não for excesso de velocidade
        except:
          velocidade=0
        
        print("ok")

        multa=Multa.objects.create(
            veiculo=Veiculo.objects.filter(id=pk).first(),
            valor=valor,
            localizacao=local,
            data=timezone.now(),
            tipo=tipo,
	    velocidade=velocidade,
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



import pytesseract # Certifique-se de ter instalado: pip install pytesseract
from PIL import Image
from django.shortcuts import render, redirect
from .models import Veiculo

def get_view(request):
    if request.method == "POST":
        tipo_busca = request.POST.get("tipo_busca")
        matricula = ""

        if tipo_busca == "texto":
            # Busca simples por texto
            matricula = request.POST.get("matricula", "").strip().upper()
        
        elif tipo_busca == "foto":
            # Busca por imagem
            foto = request.FILES.get("foto")
            if foto:
                try:
                    # Abre a imagem e extrai o texto (OCR)
                    img = Image.open(foto)
                    texto_extraido = pytesseract.image_to_string(img)
                    
                    # Limpeza básica do texto (remove espaços e coloca em maiúsculas)
                    # Pode ser necessário usar Regex aqui dependendo do padrão das matrículas
                    matricula = texto_extraido.strip().upper().replace(" ", "").replace("\n", "")
                except Exception as e:
                    return render(request, "get.html", {"erro": "Erro ao processar a imagem."})
            else:
                return render(request, "get.html", {"erro": "Nenhuma foto foi enviada."})

        # Processamento comum para ambos os casos
        if matricula:
            veiculo = Veiculo.objects.filter(matricula__icontains=matricula).first()

            if veiculo:
                # Se encontrou, redireciona para a página de detalhes/lista
                return redirect('lista', pk=veiculo.id)
            else:
                return render(request, "get.html", {
                    "erro": f"Nenhum veículo encontrado para a matrícula: {matricula}"
                })
        else:
            return render(request, "get.html", {"erro": "Não foi possível identificar a matrícula."})

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



from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.utils import timezone
from .models import Veiculo, Multa
from .serializers import MultaSerializer
import cv2, numpy as np
from PIL import Image
import pytesseract
import hashlib

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def api_multar(request):

    # ---------------- FOTO ----------------
    if 'foto' not in request.FILES:
        return Response({'erro': 'Foto obrigatória'}, status=400)

    try:
        arquivo = request.FILES['foto'].read()
    except Exception as e:
        return Response({'erro': 'Falha ao ler arquivo da foto', 'detalhes': str(e)}, status=500)

    # ---------------- DADOS OPCIONAIS ----------------
    velocidade = request.data.get('velocidade')
    tipo = request.data.get('tipo_infracao', 'desconhecido')
    local = request.data.get('local', 'Radar automático')
    valor = request.data.get('valor', 10000)

    # converte velocidade
    if velocidade:
        try:
            velocidade = float(velocidade)
        except ValueError:
            velocidade = None
    else:
        velocidade = None

    # ---------------- OCR ----------------
    try:
        np_data = np.frombuffer(arquivo, np.uint8)
        img = cv2.imdecode(np_data, cv2.IMREAD_COLOR)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)
        pil_img = Image.fromarray(thresh)
        texto = pytesseract.image_to_string(pil_img, config="--psm 8")
        matricula = ''.join(c for c in texto.upper() if c.isalnum())
    except Exception as e:
        matricula = None

    if not matricula:
        matricula = "N/A"

    # ---------------- PROCURAR VEÍCULO ----------------
    veiculo = None
    if matricula != "N/A":
        try:
            veiculo = Veiculo.objects.filter(matricula__icontains=matricula).first()
        except:
            veiculo = None

    if not veiculo:
        veiculo = None  # mantém None se não encontrou

    # ---------------- HASH 32 ----------------
    try:
        hash_input = arquivo + str(timezone.now()).encode()
        if matricula:
            hash_input += matricula.encode()
        hash_id = hashlib.md5(hash_input).hexdigest()
    except:
        hash_id = None

    # ---------------- CRIAR MULTA ----------------
    try:
        multa = Multa.objects.create(
            veiculo=veiculo,
            valor=valor,
            localizacao=local,
            data=timezone.now(),
            tipo=tipo,
            velocidade=velocidade,
            agente="admin",
            confirmada=False
        )
    except Exception as e:
        return Response({'erro': 'Falha ao criar multa', 'detalhes': str(e)}, status=500)

    serializer = MultaSerializer(multa)

    # ---------------- RESPOSTA ----------------
    return Response({
        'status': 'ok',
        'matricula_detectada': matricula,
        'hash_id': hash_id,
        'multa': serializer.data
    })
