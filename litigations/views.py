from rest_framework import viewsets, generics
from litigations.models import Litigation, Reference, Title
from litigations.serializers import LitigationSerializer, ReferenceSerializer, TitleSerializer
import datetime

class LitigationViewSet(viewsets.ModelViewSet):
    queryset = Litigation.objects.all()
    serializer_class = LitigationSerializer
    def get_queryset(self):
        relno = self.request.GET.get('relno')
        year = self.request.GET.get('year')
        orgs = self.request.GET.get('organizations')
        people = self.request.GET.get('people')
        respondents = self.request.GET.get('respondents')
        date1=self.request.GET.get('from')
        date2=self.request.GET.get('to')
        allLitigations=Litigation.objects.all()
        if relno is not None:
            allLitigations=allLitigations.filter(release_no=relno)
        if year is not None:
            allLitigations = allLitigations.filter(date__year=year)
        if orgs is not None:
            allLitigations = allLitigations.filter(organizations__contains=orgs)
        if people is not None:
            allLitigations = allLitigations.filter(people__contains=people)
        if respondents is not None:
            allLitigations = allLitigations.filter(respondents__contains=respondents)
        if date1 is not None:
            allLitigations = allLitigations.filter(date__gte = datetime.date(int(date1.split("-")[0]),int(date1.split("-")[1]),int(date1.split("-")[2])))
        if date2 is not None:
            allLitigations = allLitigations.filter(date__lte = datetime.date(int(date2.split("-")[0]),int(date2.split("-")[1]),int(date2.split("-")[2])))

        return allLitigations


class ReferenceViewSet(viewsets.ModelViewSet):
    queryset = Reference.objects.all()
    serializer_class = ReferenceSerializer


class TitleViewSet(viewsets.ModelViewSet):
    queryset = Title.objects.all()
    serializer_class = TitleSerializer
