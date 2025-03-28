from django.urls import include, path
from rest_framework.routers import DefaultRouter

from api.views import (CoverageViewSet, DocumentViewSet, FormMergeViewSet,
                       PolicyViewSet, VesselViewSet)

app_name = 'api'

router = DefaultRouter()

router.register(r'coverage', CoverageViewSet, basename='coverage')
router.register(r'documents', DocumentViewSet, basename='documents')
router.register(r'merge', FormMergeViewSet, basename='merge')
router.register(r'policies', PolicyViewSet, basename='policies')
router.register(r'vessels', VesselViewSet, basename='vessels')

urlpatterns = [
    path('', include(router.urls)),
]
