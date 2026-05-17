"""URL routes for the public-facing core app."""

from django.urls import path

from . import views

app_name = 'core'

urlpatterns = [
    path('', views.home, name='home'),
    path('servicos/', views.services, name='services'),
    path('contacto/', views.contact, name='contact'),
    path('contacto/obrigado/', views.contact_thanks, name='contact_thanks'),
    path('api/pedido-contacto/', views.pedido_contacto, name='pedido_contacto'),
]
