from django.urls import include, path
from rest_framework import routers
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from . import views


router = routers.DefaultRouter()
router.register("articles", views.ArticleViewSet)
router.register("factures", views.FactureViewSet, basename="facture")

urlpatterns = [
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    path("api/token/", TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path("api/token/refresh/", TokenRefreshView.as_view(), name='token_refresh'),
    path('api/sign-up/', views.SignUpAPIView.as_view(), name='sign_up'),
    path('api/', include(router.urls)),
]

# urlpatterns += router.urls
