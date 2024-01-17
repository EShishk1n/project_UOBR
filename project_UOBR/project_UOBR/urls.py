"""
URL configuration for project_UOBR project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path

from dvizhenie import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('start', views.start_page, name='start_page'),
    path('rig', views.DrillingRigView.as_view(), name='rig'),
    path('rig/add', views.DrillingRigAddView.as_view(), name='rig_add'),
    path('rig/<int:pk>', views.DrillingRigUpdateView.as_view(), name='rig_update'),
    path('rig/<int:pk>/delete', views.DrillingRigDeleteView.as_view(), name='rig_delete'),
    path('pad', views.PadView.as_view(), name='pad'),
    path('pad/add', views.PadAddView.as_view(), name='pad_add'),
    path('pad/<int:pk>', views.PadUpdateView.as_view(), name='pad_update'),
    path('pad/<int:pk>/delete', views.PadDeleteView.as_view(), name='pad_delete'),
    path('rig_position', views.RigPositionView.as_view(), name='rig_position'),
    path('rig_position/<int:pk>', views.RigPositionUpdateView.as_view(), name='rig_position_update'),
    path('auth', views.auth, name='authentication'),
    path('next_position', views.next_position, name='next_position'),
]
