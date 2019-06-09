import spacy
from mining.mining.pipelines import clean_string
from litigations.models import Litigation, Title, Reference
import datetime


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


def test_contrinue_loop():
    for i in range(1995, 2019):
        if i in [2016, 1999, 1995]:
            print(i)


def remove_characters(s: str, excluded_characters: str) -> str:
    return s.translate(str.maketrans("", "", excluded_characters))


def test_remove_characters():
    s = "a, DHHDHDHDH, c,\n\rd\t\t,e,f....,.'n\n,g,h,i"
    result = remove_characters(s.lower(), " .,dh\n\r\t")
    print(result)


def parse_date_modified(value: str):
    if type(value) is not str:
        return None
    result = value.replace("Modified", "")
    excluded_characters = ' .,:\n\r\t\\/'
    result = result.translate(str.maketrans("", "", excluded_characters))
    formats = ["%b%d%Y", "%B%d%Y", '%m%d%Y']
    for fmt in formats:
        try:
            return datetime.datetime.strptime(result, fmt).date()
        except ValueError:
            pass
    return result


def test_parse_date_modified():
    date_strings = ['Modified: Sep.  7, 2019', 'Modified: September.  7, 2019', 'Modified: Nov.  7, 2019',
                    'Modified: November.  7, 2019',
                    'Modified: June  7, 2019', 'Modified: 12/30/2009', 'Modified: 12/28/2016', 'Modified:10/05/1999',
                    'Modified:10/4/1999', None]
    for date in date_strings:
        print(parse_date_modified(date))


if __name__ == '__main__':
    print('casual.py')
    # test_spacy_load()
    # test_litigation_to_string()
    # test_contrinue_loop()
    # test_remove_characters()
    test_parse_date_modified()
