from django.shortcuts import render

def index(request):
    """Renderiza a página principal com a aplicação de tarefas."""
    return render(request, 'index.html')
