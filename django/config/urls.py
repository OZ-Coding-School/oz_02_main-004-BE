from django.contrib import admin
from django.urls import path, include, re_path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions
from django.conf.urls.static import static
from django.conf import settings

schema_view = get_schema_view(
    openapi.Info(
        title='Petodo API',
        default_version='v1',
        description='API documentation for Team4. Project',
        terms_of_service='https://www.oz-02-main-04.xyz/',
        contact=openapi.Contact(email='contact@example.com'),
        license=openapi.License(name='BSD License'),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/pets/', include('pets.urls.deploy')),
    path('api/v1/guestbook/', include('guestbook.urls.deploy')),
    path('api/v1/pets/', include('pets.urls.testForLocal')),     # 배포시 지우기
    path('api/v1/guestbook/', include('guestbook.urls.testForLocal')), # 배포시 지우기
    path('api/v1/users/', include('users.urls')),
    path('api/v1/posts/', include('posts.urls')),
    path('api/v1/recommendation/', include('recommendation.urls')),
    path('api/v1/accounts/', include('allauth.urls')),
    path('api/v1/api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/v1/api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    re_path(r'^swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0), name='schema-json',),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui',),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
