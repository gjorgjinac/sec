from rest_framework import serializers
from .models import Litigation, Reference, Title

'''The reference and title serializers only need to supply the model class 
and the fields that are supposed to be serialized'''

class ReferenceSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Reference
        fields = ('id', 'litigation_id', 'reference', 'reference_text')


class TitleSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Title
        fields = ('id', 'litigation_id', 'title_text', 'priority')

'''Since we want the titles and references to be serialized along with the litigation, 
we need to provide their serializers and include them in the fields tuple. 
Note: the source parameter provided in the constructor of the ReferenceSerializer and TitleSerializer
has to match the name of the foreign key field defined in the model
'''
class LitigationSerializer(serializers.HyperlinkedModelSerializer):
    references = ReferenceSerializer(many=True, read_only=True, source='litigation_fk_reference')
    titles = TitleSerializer(many=True, read_only=True, source='litigation_fk_title')

    class Meta:
        model = Litigation
        fields = (
            'id', 'release_no', 'date', 'date_modified', 'respondents', 'people', 'organizations', 'references',
            'titles', 'content')
