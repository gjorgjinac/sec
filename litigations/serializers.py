from rest_framework import serializers
from .models import Litigation, Reference, Title


class ReferenceSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Reference
        fields = ('id', 'litigation_id', 'reference', 'reference_text')


class TitleSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Title
        fields = ('id', 'litigation_id', 'title_text', 'priority')


class LitigationSerializer(serializers.HyperlinkedModelSerializer):
    references = ReferenceSerializer(many=True, read_only=True, source='litigation_fk_reference')
    titles = TitleSerializer(many=True, read_only=True, source='litigation_fk_title')

    class Meta:
        model = Litigation
        fields = (
        'id', 'release_no', 'date', 'respondents', 'people', 'organizations', 'references', 'titles', 'content')
