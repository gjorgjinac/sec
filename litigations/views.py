from rest_framework import viewsets, generics
from litigations.models import Litigation, Reference, Title
from litigations.serializers import LitigationSerializer, ReferenceSerializer, TitleSerializer


class LitigationViewSet(viewsets.ModelViewSet):
    queryset = Litigation.objects.all()
    serializer_class = LitigationSerializer
    def get_queryset(self):
        relno = self.request.GET.get('relno')
        year = self.request.GET.get('year')
        orgs = self.request.GET.get('organizations')
        people = self.request.GET.get('people')
        respondents = self.request.GET.get('respondents')

        if relno is not None:
            return Litigation.objects.filter(release_no=relno)
        if year is not None:
            return Litigation.objects.filter(date__year=year)
        if orgs is not None:
            return Litigation.objects.filter(organizations__contains=orgs)
        if people is not None:
            return Litigation.objects.filter(people__contains=people)
        if respondents is not None:
            return Litigation.objects.filter(respondents__contains=respondents)
        return Litigation.objects.all()


class ReferenceViewSet(viewsets.ModelViewSet):
    queryset = Reference.objects.all()
    serializer_class = ReferenceSerializer


class TitleViewSet(viewsets.ModelViewSet):
    queryset = Title.objects.all()
    serializer_class = TitleSerializer
