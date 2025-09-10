import os
import pandas as pd
import datetime
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.core.mail import mail_admins
from django.contrib.auth.decorators import login_required
from django.core.files import File
from django.contrib.auth.models import User
from .models import UploadedFile, ClientCoachRelation
from .utils import extract_table_from_pdf


# -----------------------------
# Pomocná funkce: souhrnné statistiky
# -----------------------------
def calculate_summary(files):
    summary = {
        "rozvaha": {"aktiva": 0, "pasiva": 0},
        "vykaz": {"trzby": 0, "naklady": 0, "zisk": 0},
    }

    for f in files:
        if not f.csv_file:
            continue
        try:
            df = pd.read_csv(f.csv_file.path)

            if f.file_type == "rozvaha":
                if "Aktiva" in df.columns:
                    summary["rozvaha"]["aktiva"] = df["Aktiva"].sum()
                if "Pasiva" in df.columns:
                    summary["rozvaha"]["pasiva"] = df["Pasiva"].sum()

            elif f.file_type == "vykaz":
                if "Trzby" in df.columns:
                    summary["vykaz"]["trzby"] = df["Trzby"].sum()
                if "Naklady" in df.columns:
                    summary["vykaz"]["naklady"] = df["Naklady"].sum()
                summary["vykaz"]["zisk"] = (
                    summary["vykaz"]["trzby"] - summary["vykaz"]["naklady"]
                )
        except Exception as e:
            print(f"Chyba při čtení {f.csv_file.path}: {e}")

    return summary


# -----------------------------
# Dashboard – klient (vidí jen svoje data)
# -----------------------------
@login_required
def dashboard(request):
    current_year = datetime.date.today().year
    # vezmeme rok z query parametru (GET) nebo default = aktuální rok
    selected_year = int(request.GET.get("year", current_year))
    years = list(range(current_year, current_year - 6, -1))

    user_to_show = request.user
    files = UploadedFile.objects.filter(user=user_to_show, year=selected_year).order_by('-uploaded_at')
    summary = calculate_summary(files)

    context = {
        "files": files,
        "summary": summary,
        "user_to_show": user_to_show,
        "is_coach": request.user.groups.filter(name="coach").exists(),
        "years": years,
        "current_year": current_year,
        "selected_year": selected_year,
    }
    return render(request, "dashboard.html", context)


# -----------------------------
# Dashboard – kouč (vidí klienty a jejich data)
# -----------------------------
@login_required
def coach_dashboard(request, client_id=None):
    if not request.user.groups.filter(name="coach").exists():
        messages.error(request, "Nemáte oprávnění vidět dashboard kouče.")
        return redirect("dashboard")

    current_year = datetime.date.today().year
    selected_year = int(request.GET.get("year", current_year))
    years = list(range(current_year, current_year - 6, -1))

    relations = ClientCoachRelation.objects.filter(coach=request.user)
    clients = [rel.client for rel in relations]

    if client_id:
        relation = relations.filter(client_id=client_id).first()
        if not relation:
            messages.error(request, "Tento klient vám není přiřazen.")
            return redirect("coach_dashboard")

        user_to_show = relation.client
        files = UploadedFile.objects.filter(user=user_to_show, year=selected_year).order_by('-uploaded_at')
        summary = calculate_summary(files)

        context = {
            "files": files,
            "summary": summary,
            "user_to_show": user_to_show,
            "readonly": True,
            "coach_clients": clients,
            "is_coach": True,
            "years": years,
            "current_year": current_year,
            "selected_year": selected_year,
        }
        return render(request, "dashboard.html", context)

    return render(
        request,
        "filesapp/coach_dashboard.html",
        {"clients": clients, "is_coach": True, "years": years, "selected_year": selected_year},
    )

@login_required
def upload(request):
    current_year = datetime.date.today().year
    years = list(range(current_year, current_year - 6, -1))  # aktuální + 5 let zpět

    return render(
        request,
        "filesapp/upload.html",
        {
            "is_coach": request.user.groups.filter(name="coach").exists(),
            "years": years,
            "current_year": current_year,
        },
    )

# -----------------------------
# Upload rozvaha (PDF → CSV) – pouze klient
# -----------------------------
@login_required
def upload_rozvaha(request):
    current_year = datetime.date.today().year
    years = list(range(current_year, current_year - 6, -1))  # aktuální + 5 let zpět

    if request.method == 'POST' and 'file' in request.FILES:
        if request.user.groups.filter(name="coach").exists():
            messages.error(request, "Kouč nemůže nahrávat soubory.")
            return redirect("dashboard")

        pdf_file = request.FILES['file']
        year = int(request.POST.get("year", current_year))  # rok z formuláře

        uploaded = UploadedFile.objects.create(
            user=request.user,
            original_file=pdf_file,
            file_type='rozvaha',
            year=year
        )

        pdf_path = uploaded.original_file.path
        csv_path = extract_table_from_pdf(pdf_path, f"rozvaha_{request.user.id}_{year}")

        if csv_path:
            with open(csv_path, 'rb') as f:
                uploaded.csv_file.save(os.path.basename(csv_path), File(f), save=True)
            messages.success(request, "Soubor byl úspěšně zpracován.")
            mail_admins(
                subject="Nový soubor nahrán",
                message=f"Uživatel {request.user.username} nahrál rozvahu {pdf_file.name} pro rok {year}.",
            )
        else:
            messages.error(request, "Zpracování souboru selhalo.")
            mail_admins(
                subject="Chyba při zpracování souboru",
                message=f"Uživatel {request.user.username} nahrál rozvahu {pdf_file.name}, ale zpracování selhalo.",
            )

        return redirect('dashboard')

    return render(
        request,
        'filesapp/upload.html',
        {
            "is_coach": request.user.groups.filter(name="coach").exists(),
            "years": years,
            "current_year": current_year,
        },
    )


# -----------------------------
# Upload výkaz – pouze klient
# -----------------------------
@login_required
def upload_vykaz(request):
    current_year = datetime.date.today().year
    years = list(range(current_year, current_year - 6, -1))  # aktuální + 5 let zpět

    if request.method == 'POST' and 'file' in request.FILES:
        if request.user.groups.filter(name="coach").exists():
            messages.error(request, "Kouč nemůže nahrávat soubory.")
            return redirect("dashboard")

        pdf_file = request.FILES['file']
        year = int(request.POST.get("year", current_year))  # rok z formuláře

        uploaded = UploadedFile.objects.create(
            user=request.user,
            original_file=pdf_file,
            file_type='vykaz',
            year=year
        )

        pdf_path = uploaded.original_file.path
        csv_path = extract_table_from_pdf(pdf_path, f"vykaz_{request.user.id}_{year}")

        if csv_path:
            with open(csv_path, 'rb') as f:
                uploaded.csv_file.save(os.path.basename(csv_path), File(f), save=True)
            messages.success(request, "Soubor byl úspěšně zpracován.")
            mail_admins(
                subject="Nový soubor nahrán",
                message=f"Uživatel {request.user.username} nahrál výkaz {pdf_file.name} pro rok {year}.",
            )
        else:
            messages.error(request, "Zpracování souboru selhalo.")
            mail_admins(
                subject="Chyba při zpracování souboru",
                message=f"Uživatel {request.user.username} nahrál výkaz {pdf_file.name}, ale zpracování selhalo.",
            )

        return redirect('dashboard')

    return render(
        request,
        'filesapp/upload.html',
        {
            "is_coach": request.user.groups.filter(name="coach").exists(),
            "years": years,
            "current_year": current_year,
        },
    )

# -----------------------------
# Zobrazení tabulky z CSV
# -----------------------------
@login_required
def view_table(request, file_id):
    uploaded = get_object_or_404(UploadedFile, id=file_id)

    # klient může zobrazit jen svoje soubory
    if request.user == uploaded.user:
        pass
    # kouč může zobrazit soubory klienta, pokud je přiřazen
    elif request.user.groups.filter(name="coach").exists():
        relation = ClientCoachRelation.objects.filter(coach=request.user, client=uploaded.user).first()
        if not relation:
            messages.error(request, "Nemáte oprávnění zobrazit tento soubor.")
            return redirect("dashboard")
    else:
        messages.error(request, "Nemáte oprávnění zobrazit tento soubor.")
        return redirect("dashboard")

    try:
        df = pd.read_csv(uploaded.csv_file.path)

        if uploaded.file_type == "vykaz":
            for col in df.columns:
                if pd.api.types.is_numeric_dtype(df[col]):
                    if df[col].dropna().apply(float.is_integer).all():
                        df[col] = df[col].astype('Int64')

        headers = df.columns.tolist()
        table_data = df.values.tolist()

    except Exception as e:
        print(f"Chyba při čtení {uploaded.csv_file.path}: {e}")
        headers, table_data = [], []

    context = {
        'uploaded': uploaded,
        'headers': headers,
        'table_data': table_data,
        "is_coach": request.user.groups.filter(name="coach").exists(),
    }
    return render(request, 'filesapp/view_table.html', context)


# -----------------------------
# Mazání souboru – pouze klient
# -----------------------------
@login_required
def delete_file(request, file_id):
    uploaded = get_object_or_404(UploadedFile, id=file_id, user=request.user)

    if request.user.groups.filter(name="coach").exists():
        messages.error(request, "Kouč nemůže mazat soubory.")
        return redirect("dashboard")

    if request.method == "POST":
        if uploaded.original_file:
            uploaded.original_file.delete(save=False)
        if uploaded.csv_file:
            uploaded.csv_file.delete(save=False)

        uploaded.delete()
        messages.success(request, "Soubor byl úspěšně smazán.")
        return redirect('dashboard')

    return redirect('dashboard')
