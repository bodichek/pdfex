from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.core.files.storage import FileSystemStorage
import os

# Save files to /files folder (in root)
BASE_UPLOAD_DIR = os.path.join('files')


# -----------------------------
# Registrace nového uživatele
# -----------------------------
def register_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('welcome')  # přesměrujeme na úvodní stránku
    else:
        form = UserCreationForm()
    return render(request, 'registration/register.html', {'form': form})


# -----------------------------
# Úvodní stránka (povídací)
# -----------------------------
@login_required
def welcome(request):
    return render(request, 'welcome.html')


# -----------------------------
# Dashboard – statistiky/výsledky
# -----------------------------
@login_required
def dashboard(request):
    return render(request, 'dashboard.html')


# -----------------------------
# Obecné nahrávání souborů
# -----------------------------
@login_required
def upload(request):
    if request.method == 'POST' and 'file' in request.FILES:
        file = request.FILES['file']
        fs = FileSystemStorage(location=BASE_UPLOAD_DIR)
        fs.save(f"upload_{request.user.id}_{file.name}", file)
        return redirect('dashboard')
    return render(request, 'upload.html')


# -----------------------------
# Upload Rozvaha (balance sheet)
# -----------------------------
@login_required
def upload_rozvaha(request):
    if request.method == 'POST' and 'file' in request.FILES:
        file = request.FILES['file']
        fs = FileSystemStorage(location=BASE_UPLOAD_DIR)
        fs.save(f"rozvaha_{request.user.id}_{file.name}", file)
        return redirect('dashboard')
    return redirect('dashboard')


# -----------------------------
# Upload Výkaz (profit & loss)
# -----------------------------
@login_required
def upload_vykaz(request):
    if request.method == 'POST' and 'file' in request.FILES:
        file = request.FILES['file']
        fs = FileSystemStorage(location=BASE_UPLOAD_DIR)
        fs.save(f"vykaz_{request.user.id}_{file.name}", file)
        return redirect('dashboard')
    return redirect('dashboard')
