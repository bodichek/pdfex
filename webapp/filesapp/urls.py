from django.urls import path
from . import views

urlpatterns = [
    path("dashboard/", views.dashboard, name="dashboard"),  # klient
    path("coach/", views.coach_dashboard, name="coach_dashboard"),  # seznam klientů kouče
    path("coach/<int:client_id>/", views.coach_dashboard, name="coach_dashboard_client"),  # detail klienta
    path("upload/", views.upload, name="upload"),  # 👈 musí tam být
    path("upload/rozvaha/", views.upload_rozvaha, name="upload_rozvaha"),
    path("upload/vykaz/", views.upload_vykaz, name="upload_vykaz"),
    path("view/<int:file_id>/", views.view_table, name="view_table"),
    path("delete/<int:file_id>/", views.delete_file, name="delete_file"),
]
