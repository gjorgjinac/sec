import spacy
from mining.mining.pipelines import clean_string
from litigations.models import Litigation, Title, Reference


# Adjustment for Local Imports
# os.environ['DJANGO_SETTINGS_MODULE'] = 'sec.settings'
# django.setup()

def test_spacy_load():
    nlp = spacy.load('en_core_web_sm')
    doc = nlp("google amazon org")

    output = '; '.join(
        list(set(map(lambda y: clean_string(y.text), filter(lambda x: x.label_ == 'ORG', doc.ents)))))
    print(output)


def test_litigation_to_string():
    release_no = 'LR-254380'
    litigation: Litigation = Litigation.objects.filter(release_no=release_no).first()
    print(litigation)


if __name__ == '__main__':
    print('casual.py')
    # test_spacy_load()
    test_litigation_to_string()
