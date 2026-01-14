from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('home.urls')),
    path('squash/', include('squash.urls')),
    path('yamb/', include('yamb.urls', namespace='yamb')),
]
