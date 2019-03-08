from rest_framework import viewsets
from litigations.models import Litigation, Reference, Title
from litigations.serializers import LitigationSerializer, ReferenceSerializer, TitleSerializer


class LitigationViewSet(viewsets.ModelViewSet):
    queryset = Litigation.objects.all()
    serializer_class = LitigationSerializer


class LitigationViewSetByYear(viewsets.ModelViewSet):
    queryset = Litigation.objects.all()
    serializer_class = LitigationSerializer


class ReferenceViewSet(viewsets.ModelViewSet):
    queryset = Reference.objects.all()
    serializer_class = ReferenceSerializer


class TitleViewSet(viewsets.ModelViewSet):
    queryset = Title.objects.all()
    serializer_class = TitleSerializer
