from rest_framework import viewsets, generics
from litigations.models import Litigation, Reference, Title
from litigations.serializers import LitigationSerializer, ReferenceSerializer, TitleSerializer
from rest_framework_swagger.views import get_swagger_view
import datetime

schema_view = get_swagger_view(title='SEC Litigations API')

''' A method that parses strings in the format DD-MM-YYYY and returns a date object '''
class LitigationViewSet(viewsets.ModelViewSet):

    def string_to_date(self, string_date):
        date_parts = string_date.split("-")
        return datetime.date(int(date_parts[0]), int(date_parts[1]), int(date_parts)[2])
    '''Building a query that will fetch the litigations from the database'''
    queryset = Litigation.objects.all()
    serializer_class = LitigationSerializer

    '''We check whether a value for each field was specified as a parameter in the request and
           add filters for the existing values to the query. Note that the query is not executed at this point,
           and we do not keep all of the litigations in memory'''
    def get_queryset(self):

        release_no = self.request.GET.get('release_no')
        year = self.request.GET.get('year')
        orgs = self.request.GET.get('organizations')
        people = self.request.GET.get('people')
        respondents = self.request.GET.get('respondents')
        date1 = self.request.GET.get('from')
        date2 = self.request.GET.get('to')
        litigations_query = Litigation.objects.all()
        if release_no is not None:
            litigations_query = litigations_query.filter(release_no=release_no)
        if year is not None:
            litigations_query = litigations_query.filter(date__year=year)
        if orgs is not None:
            litigations_query = litigations_query.filter(organizations__contains=orgs)
        if people is not None:
            litigations_query = litigations_query.filter(people__contains=people)
        if respondents is not None:
            litigations_query = litigations_query.filter(respondents__contains=respondents)
        if date1 is not None:
            litigations_query = litigations_query.filter(date__gte=self.string_to_date(date1))
        if date2 is not None:
            litigations_query = litigations_query.filter(date__lte=self.string_to_date(date2))

        return litigations_query


class ReferenceViewSet(viewsets.ModelViewSet):
    queryset = Reference.objects.all()
    serializer_class = ReferenceSerializer


class TitleViewSet(viewsets.ModelViewSet):
    queryset = Title.objects.all()
    serializer_class = TitleSerializer
