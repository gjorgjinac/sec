
import spacy

from mining.mining.pipelines import clean_string

if __name__ == '__main__':
    print('a')
    nlp = spacy.load('en_core_web_sm')
    doc = nlp("google amazon org")
    print ('; '.join(), list(set(map(lambda y: clean_string(y.text), filter(lambda x: x.label_ == 'ORG', doc.ents)))))