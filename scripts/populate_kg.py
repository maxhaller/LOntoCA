import pandas as pd
import datetime
from glob import glob
import re
from tqdm import tqdm
import pytz
from bs4 import BeautifulSoup as Bs
from rdflib import Graph, URIRef, Literal
from rdflib.namespace import RDF, OWL, RDFS, XSD, Namespace
from LOntoCA.util.constants import month_dict

coming_into_effect_pattern = r'(?:tritt|treten|ist\sam).*(((\d+\.\s?\d+\.\s?\d{4}))|([\d]+\.\s?[a-zA-Zä]+\s[\d]{4})).*in\sKraft'
normal_working_hours_period_pattern = r'(?:(?:Durchrechnungszeitraum)|(?:(?:(?:Normalarbeitszeit)|(?:Wochenarbeitszeit))[^\.]*eines Zeitraumes)|(?:Innerhalb eines Abrechnungszeitraumes))[^\.]*\s((?:(?:ein(?:em)?|zwei|drei|vier|fünf|sechs|sieben|acht|neun|zehn|elf|zwölf)|[0-9]+) (?:(?:Tage)|(?:Woche)|(?:(?:Kalender)?[mM]onat)|(?:Jahr))[en]*)|in(?:nerhalb)? eine[ms] ([a-zäöü]+(?:wöchig|tägig|monatig|jährig))[en]*\s(?:Durchrechnungs)?[zZ]eitraum|Normalarbeitszeit.*überschreit.*\s((?:[a-zäöü]+(?:wöchig|tägig|monatig|jährig))[en]*)\sDurchschnitt|[aA]m Ende des (.*jährlich)[en]*\sDurchrechnungszeitraumes'
daily_normal_working_hours_pattern = r'[Tt]ägliche(?:\sHöchstgrenze der)? Normalarbeitszeit.*\s((?:(?:[0-9]+)|(?:[a-zöüä]+))\sStunden)'
weekly_normal_working_hours_pattern = r'(?:(?:[Ww]öchentliche(?:\sHöchstgrenze der)? Normalarbeitszeit)|(?:wöchentliche Arbeitszeit))[^.^;]*\s((?:(?:[0-9]+,?[0-9]?)|(?:[a-zöüä]+))\sStunden)|normale Arbeitszeit[^\.^;]*wöchentlich\s((?:(?:[0-9]+,?[0-9]?)|(?:[a-zöüä]+))\sStunden)'
bonus_pay_pattern = ['sonderzahlung', 'urlaubszuschuss', 'urlaubsgeld', 'weihnachtsremuneration']
name_pattern = r'((?:(?:Rahmen\s?)?[kK]ollektivvertrag|Dienst- und Besoldungsornung (?:\(DBO\))?) (?:(?:(?:für)|(?:betreffend)) [^\.]+))\s[^\.]\.'
anniversary_bonus_pay_pattern = ['jubiläumszuwendung', 'dienstjubiläum', 'dienstjubiläen', 'jubiläumsgeld']

labor_unions = {
    'Österreichischer Gewerkschaftsbund': ['österreichischer gewerkschaftsbund', 'österreichischen gewerkschaftsbund', 'ögb'],
    'Gewerkschaft GPA': ['gewerkschaft der privatangestellten', 'gpa'],
    'Younion': ['younion'],
    'Produktionsgewerkschaft - PRO-GE': ['pro- ge', 'pro-ge'],
    'Gewerkschaft Handel, Transport, Verkehr': ['gewerkschaft handel, transport, verkehr', 'gewerkschaft der bediensteten in handel, transport und verkehr'],
    'Gewerkschaft Bau-Holz': ['gbh', 'gewerkschaft bau-holz '],
    'Gewerkschaft der Post- und Fernmeldebediensteten': ['gewerkschaft der post- und fernmeldebediensteten'],
    'Gewerkschaft Kunst, Medien, freie Berufe': ['gewerkschaft kunst, medien, freie berufe', 'gewerkschaft kunst, medien, sport, freie berufe'],
    'Gewerkschaft Öffentlicher Dienst': ['gewerkschaft öffentlicher dienst', 'göd'],
    'Gewerkschaft der Gemeindebediensteten – Kunst, Medien, Sport, freie Berufe': ['gewerkschaft der gemeindebediensteten – kunst, medien, sport, freie berufe'],
    'Gewerkschaft der Lebens- und Genußmittelarbeiter': ['gewerkschaft der lebens- und genußmittelarbeiter'],
    'Gewerkschaft Agrar-Nahrung-Genuss': ['gewerkschaft agrar-nahrung-genuß', 'gewerkschaft agrar-nahrung-genuss'],
    'Gewerkschaft vida': ['gewerkschaft vida'],
    'Landarbeiterkammer Tirol': ['landarbeiterkammer tirol'],
    'Landarbeiterkammer Vorarlberg': ['landarbeiterkammer vorarlberg'],
    'Gewerkschaft der Chemiearbeiter': ['gewerkschaft der chemiearbeiter'],
    'Kammer der Arbeiter und Angestellten in der Land- und Forstwirtschaft für Oberösterreich': ['kammer der arbeiter und angestellten in der land- und forstwirtschaft', 'oö. land- und forstarbeiterbund', 'o.ö. land- und forstarbeiterbund'],
    'Verein Evangelischer Pfarrerinnen und Pfarrer': ['verein evangelischer pfarrerinnen und pfarrer'],
    'Verband Angestellter Apotheker Österreichs': ['verband angestellter apotheker österreichs'],
    'Gewerkschaft Hotel, Gastgewerbe, Persönlicher Dienst': ['gewerkschaft hotel, gastgewerbe, persönlicher dienst'],
    'Kurienversammlung der angestellten Ärzte der Ärztekammer für Oberösterreich': ['kurienversammlung der angestellten ärzte der ärztekammer für oberösterreich'],
    'Zentralbetriebsrat des ORF': ['zentralbetriebsrat des orf'],
    'Bundeskurie angestellte Ärzte': ['bundeskurie für angestellte ärzte']
}

economic_unions = {
    'Bundesinnung der Chemischen Gewerbe und der Denkmal-, Fassaden- und Gebäudereiniger': ['bundesinnung der chemischen gewerbe und der denkmal-, fassaden- und gebäudereiniger'],
    'Agrarmarkt Austria': ['agrarmarkt austria'],
    'Bundeskammer der Architekten und Ingenieurkonsulenten': ['bundeskammer der architekten und ingenieurkonsulenten', 'bundeskammer der ziviltechniker'],
    'Österreichischem Apothekerverband': ['österreichischer apothekerverband', 'österreichischem apothekerverband'],
    'Ärztekammer für Burgenland': ['ärztekammer für burgenland'],
    'Ärztekammer für Tirol': ['ärztekammer für tirol'],
    'Ärztekammer für Vorarlberg': ['ärztekammer für vorarlberg'],
    'Wirtschaftskammer': ['bundeskammer der gewerblichen wirtschaft', 'wirtschaftskammer österreich'],
    'Kammer der gewerblichen Wirtschaft Steiermark, Sektion Tourismus und Freizeitwirtschaft, Fachgruppe der Lichtspieltheater und Audiovisionsveranstalter': ['Kammer der gewerblichen Wirtschaft Steiermark, Sektion Tourismus und Freizeitwirtschaft, Fachgruppe der Lichtspieltheater und Audiovisionsveranstalter'],
    'AUSTRO CONTROL Österreichische Gesellschaft für Zivilluftfahrt mbH': ['austro control österreichische gesellschaft für zivilluftfahrt mbh'],
    'Theatererhalterverband ': ['theatererhalterverband '],
    'Bundesinnung der Bäcker': ['bundesinnung der bäcker'],
    'Oberösterreichischer Land- und Forstarbeiterbund': ['o.ö. land- und forstarbeiterbund', 'oö. land- und forstarbeiterbund'],
    'Bauarbeiter-Urlaubs- und Abfertigungskasse': ['bauarbeiter-urlaubs- und abfertigungskasse'],
    'Bundesinnung der Baugewerbe': ['bundesinnung der baugewerbe'],
    'Fachverband der Bauindustrie': ['fachverband der bauindustrie'],
    'Bundesinnung der Zimmermeister': ['bundesinnung der zimmermeister'],
    'Bundesinnung der Steinmetzmeister': ['bundesinnung der steinmetzmeister'],
    'Bundesinnung der Gärtner und Floristen': ['bundesinnung der gärtner und floristen'],
    'Land Oberösterreich': ['land oberösterreich'],
    'Bund': ['für den bund'],
    'Bundestheater-Holding GmbH': ['bundestheater-holding gmbh'],
    'Landwirtschaftskammer Tirol': ['landwirtschaftskammer tirol'],
    'Landwirtschaftskammer für Vorarlberg Sektion Landwirte': ['sektion landwirte'],
    'Fachverband Textil-, Bekleidungs-, Schuh und Lederindustrie': ['fachverband textil-, bekleidungs-, schuh und lederindustrie'],
    'Landesinnung Wien der Fleischer': ['landesinnung wien der fleischer'],
    'Verband Österreichischer Zeitungsherausgeber und Zeitungsverleger': ['verband österreichischer zeitungsherausgeber und zeitungsverleger'],
    'Dachverband der Film- und Musikwirtschaft Österreichs': ['dachverband der film- und musikwirtschaft österreichs'],
    'Fonds Soziales Wien': ['fonds soziales wien'],
    'Landesinnung der Fotografen für Niederösterreich': ['landesinnung der fotografen für niederösterreich'],
    'Österreichischen Fußball-Bundesliga': ['österreichischen fußball-bundesliga', 'öfbl'],
    'Bundesinnung der Fußpfleger, Kosmetiker und Masseure': ['bundesinnung der fußpfleger, kosmetiker und masseure'],
    'Fachverband der Glasindustrie': ['fachverband der glasindustrie'],
    'Bundesinnung der Glaser': ['bundesinnung der glaser'],
    'Arbeitgeberverband der Land- und Forstwirtschaft in Steiermark': ['arbeitgeberverband der land- und forstwirtschaft in steiermark', 'Arbeitgeberverband der Land- und Forstwirtschaft in der Steiermark'],
    'Arbeitgeberverband der land- und forstwirtschaftlichen Betriebe Kärntens': ['arbeitgeberverband der land- und forstwirtschaftlichen betriebe kärntens'],
    'Land- und Forstwirtschaftlichen Arbeitsgeberverband in Salzburg': ['land- und forstwirtschaftlichen arbeitsgeberverband in salzburg'],
    'Evangelische Kirche A.B. in Österreich': ['evangelische kirche a.b. in österreich'],
    'Evangelische Kirche A.u.H.B. in Österreich': ['evangelische kirche a.u.hb. in österreich'],
    'Evangelische Kirche H.B. in Österreich': ['evangelische kirche h.b. in österreich'],
    'Bischöfliches Ordinariat': ['bischöfliche ordinariat'],
    'Arbeitgeberverein der Bauvereinigungen Österreichs': ['arbeitgeberverein der bauvereinigungen österreichs'],
    'Österreichische Zeitschriften- und Fachmedien-Verband': ['Österreichischen Zeitschriften- und Fachmedien-Verband'],
    'Österreichische Zahnärztekammer': ['Österreichischen Zahnärztekammer'],
    'Verband Österreichischer Banken und Bankiers': ['VERBAND ÖSTERREICHISCHER BANKEN UND BANKIERS'],
    'Österreichischer Raiffeisenverband': ['Österreichischen Raiffeisenverband'],
    'Wiener Tierschutzverein GmbH': ['Wiener Tierschutzverein GmbH'],
    'Verein Wiener Symphoniker': ['VEREIN “WIENER SYMPHONIKER”'],
    'Wiener Trabrennverein': ['Wiener Trabrennverein'],
    'Wiener Stadtwerke GmbH': ['Wiener Stadtwerke GmbH'],
    'Fachgruppe Wien der Freizeitbetriebe': ['Wirtschaftskammer Wien, Fachgruppe Wien der Freizeitbetriebe', 'Fachgruppe Wien der Freizeit- und Sportbetriebe'],
    'Fachgruppe Werbung und Marktkommunikation Wien': [' Fachgruppe Werbung und Marktkommunikation Wien'],
    'Bundesinnung der Kraftfahrzeugtechniker': ['Bundesinnung der Kraftfahrzeugtechniker'],
    'Fachgruppe Wien der Kino-, Kultur- und Vergnügungsbetriebe': ['Fachgruppe Wien der Kino-, Kultur- und Vergnügungsbetriebe', 'Fachgruppe der Vergnügungsbetriebe'],
    'Verband Österreichischer Festspiele': ['Verband Österreichischer Festspiele'],
    'Unser Lagerhaus Warenhandels G.m.b.H': ['„Unser Lagerhaus“ Warenhandels G.m.b.H'],
    'Allgemeine Fachgruppe Wien des Gewerbes': ['ALLGEMEINE FACHGRUPPE WIEN DES GEWERBES', 'Allgemeinen Landesinnung Wien des Gewerbes'],
    'Kammer der Steuerberater: innen und Wirtschaftsprüfer:innen': ['Kammer der Steuerberater: innen und Wirtschaftsprüfer:innen'],
    'Interessenvertretung von Ordensspitälern und von konfessionellen Alten- und Pflegeheimen Österreichs': ['Interessenvertretung von Ordensspitälern und von konfessionellen Alten- und Pflegeheimen Österreichs'],
    'Verband Druck und Medientechnik': ['Verband Druck & Medientechnik'],
    'Arbeitgeberverband Land- und Forstwirtschaft in Niederösterreich, Burgenland und Wien': ['Arbeitgeberverband Land- und Forstwirtschaft in Niederösterreich, Burgenland und Wien', 'Arbeitgeberverband der Land- und Forstwirtschaft in Niederösterreich, Burgenland und Wien', 'Zentralverband der land- und forstwirtschaftlichen Arbeitgeber in Niederösterreich, Burgenland und Wien'],
    'Fachgruppe der Gesundheitsbetriebe Wien': ['Fachgruppe der Gesundheitsbetriebe Wien', 'Fachgruppe Wien der Gesundheitsbetriebe'],
    'Sozial- und Gesundheitsverein Gratkorn und Umgebung': ['Sozial- und Gesundheitsverein Gratkorn und Umgebung'],
    'Vereinigung der Schischulunternehmer Österreichs': ['Vereinigung der Schischulunternehmer Österreichs'],
    'Rechtsanwaltskammer Wien': ['Rechtsanwaltskammer Wien'],
    'Rechtsanwaltskammer Burgenland': ['Rechtsanwaltskammer Burgenland'],
    'Rechtsanwaltskammer Niederösterreich': ['Rechtsanwaltskammer Niederösterreich'],
    'Rechtsanwaltskammer Steiermark': ['Rechtsanwaltskammer Steiermark', 'Steiermärkischen Rechtsanwaltskammer'],
    'Rechtsanwaltskammer Tirol': ['Rechtsanwaltskammer Tirol', 'Tiroler Rechtsanwaltskammer'],
    'Rechtsanwaltskammer Vorarlberg': ['Rechtsanwaltskammer Vorarlberg'],
    'Interessensvertretung von Ordensspitälern und von konfessionellen Alten- und Pflegeheimen Österreichs': ['Interessensvertretung von Ordensspitälern und von konfessionellen Alten- und Pflegeheimen Österreichs', 'Interessenvertretung von Ordensspitälern, konfessionellen Alten- und Pflegeheimen, Erziehungs- und Bildungseinrichtungen Österreichs'],
    'Wirtschaftskammer Steiermark, Fachgruppe der privaten Krankenanstalten und der Kurbetriebe': ['Wirtschaftskammer Steiermark, Fachgruppe der privaten Krankenanstalten und der Kurbetriebe'],
    'Arbeitgeberverein für Sozial- und Gesundheitsorganisationen in Vorarlberg': ['Arbeitgeberverein für Sozial- und Gesundheitsorganisationen in Vorarlberg', 'AGV'],
    'Fachverband der industriellen Hersteller von Produkten aus Papier und Karton in Österreich': ['Fachverbandes der industriellen Hersteller von Produkten aus Papier und Karton in Österreich'],
    'ORF Fernsehprogramm- Service GmbH & Co KG': ['ORF Fernsehprogramm- Service GmbH & Co KG'],
    'Österreichischen Rundfunk': ['Österreichischen Rundfunk'],
    'Revisionsverband der österreichischen Konsumgenossenschaften': ['Revisionsverband der österreichischen Konsumgenossenschaften'],
    'Pflegeanstalt für chronisch Kranke der Barmherzigen Brüder': ['Pflegeanstalt für chronisch Kranke der Barmherzigen Brüder'],
    'Notariatskammer für Tirol und Vorarlberg': ['Notariatskammer für Tirol und Vorarlberg'],
    'Notariatskammer für Steiermark': ['Notariatskammer für Steiermark'],
    'Gruppe der Notare im Bundesland Salzburg': ['Gruppe der Notare im Bundesland Salzburg'],
    'Notariatskammer für Oberösterreich': ['Notariatskammer für Oberösterreich'],
    'Notariatskammer für Kärnten': ['Notariatskammer für Kärnten'],
    'Gemeinde Wien': ['Gemeinde Wien'],
    'Veranstalterverband Österreich': ['Veranstalterverband Österreich'],
    'Museen der Stadt Wien': ['Museen der Stadt Wien'],
    'Bundesinnung der Müller': ['Bundesinnung der Müller'],
    'Land Salzburg': ['Land Salzburg'],
    'Fachverband der Mineralölindustrie Österreichs': ['Fachverband der Mineralölindustrie Österreichs'],
    'Bundeskurie niedergelassene Ärzte': ['Bundeskurie niedergelassene Ärzte'],
    'Verband der österreichischen Landes-Hypothekenbanken': ['VERBAND DER ÖSTERREICHISCHEN LANDES-HYPOTHEKENBANKEN'],
    'Konvent der Barmherzigen Brüder': ['Konvent der Barmherzigen Brüder'],
    'Krankenfürsorgeanstalt der Bediensteten der Stadt Wien': ['Krankenfürsorgeanstalt der Bediensteten der Stadt Wien'],
    'Krankenanstaltenverband Waldviertel': ['Krankenanstaltenverband Waldviertel'],
    'Bundesinnung der Konditoren': ['Bundesinnung der Konditoren'],
    'Vorarlberger Jägerschaft': ['Vorarlberger Jägerschaft'],
    'Österreichs E-Wirtschaft': ['Österreichs E-Wirtschaf'],
    'Tiroler Landesinnung der Sanitär- Heizungs- und Lüftungstechniker': ['Tiroler Landesinnung der Sanitär- Heizungs- und Lüftungstechniker'],
    'Tiroler Landesinnung der Mechatroniker': ['Tiroler Landesinnung der Mechatroniker'],
    'Tiroler Landesinnung der Metalltechniker': ['Tiroler Landesinnung der Metalltechniker'],
    'Tiroler Landesinnung der Elektro-, Gebäude-, Alarm- und Kommunikationstechniker': ['Tiroler Landesinnung der Elektro-, Gebäude-, Alarm- und Kommunikationstechniker'],
    'Fachgruppe Gastronomie': ['Fachgruppe Gastronomie'], # Hier sollte es heißen Fachgruppe Gastronomie Niederösterreich (aber [...] zwischen Gastronomie u NOE)
    'Fachgruppe der Hotel-, und Beherbergungsbetriebe für Niederösterreich': ['Fachgruppe der Hotel-, und Beherbergungsbetriebe für Niederösterreich'],
    'Fachgruppe der Heilbade-, Kur- und Krankenanstalten sowie Mineralquellenbetriebe': ['Fachgruppe der Heilbade-, Kur- und Krankenanstalten sowie Mineralquellenbetriebe'],
    'Bundesinnung der Dachdecker, Glaser und Spengler': ['Bundesinnung der Dachdecker, Glaser und Spengler'],
    'Österreichischer Genossenschaftsverband': ['ÖSTERREICHISCHER GENOSSENSCHAFTSVERBAND'],
    'Fachverband der gewerblichen Dienstleister': ['Fachverband der gewerblichen Dienstleister'],
    'Verband Österreichischer Zeitungen': ['Verband Österreichischer Zeitungen']
}


def translate_state(s: str):
    if s == 't':
        return 'tirol'
    if s == 'vlb':
        return 'vorarlberg'
    if s == 'bgl':
        return 'burgenland'
    if s == 'w':
        return 'wien'
    if s == 'noe':
        return 'niederösterreich'
    if s == 'ooe':
        return 'oberösterreich'
    if s == 'stm':
        return 'steiermark'
    if s == 'k':
        return 'kärnten'
    if s == 's':
        return 'salzburg'
    return s


base_namespace = 'https://semantics.id/ns/'
ca_namespace = Namespace(base_namespace + 'CollectiveAgreement#')
re_namespace = Namespace(base_namespace + 'resource/')
g = Graph(base=ca_namespace)
g.parse(ca_namespace)
g.bind('re', re_namespace)
g.bind('', ca_namespace)
ca_base_url = 'https://www.kollektivvertrag.at/kv/'

party_list = [*labor_unions.keys(), *economic_unions.keys()]

counter = 0

special_char_map = {
    ord('ä'): 'ae',
    ord('ü'): 'ue',
    ord('ö'): 'oe',
    ord('ß'): 'ss',
    ord('§'): '',
    ord('.'): '',
    ord(')'): '',
    ord('('): '',
    ord(':'): '',
    ord('"'): '',
    ord('„'): '',
    ord('*'): '',
    ord(','): '',
    ord('²'): '2',
    ord('‒'): '-',
    ord('['): '',
    ord('—'): '-',
    ord(']'): '',
    ord('/'): '-',
    ord(''): '',
    ord('%'): ''
}

id_to_iri_dict = {}
party_name_uri_ref = URIRef(ca_namespace + 'partyName')
contract_party_uri_ref = URIRef(ca_namespace + 'ContractParty')

g.add((URIRef(ca_namespace + 'index'), RDF.type, OWL.DatatypeProperty))
g.add((URIRef(ca_namespace + 'index'), RDFS.domain, URIRef(ca_namespace + 'ContractualClause')))
g.add((URIRef(ca_namespace + 'index'), RDFS.range, XSD.int))

print("Creating Contract Parties in KG..")
for party in tqdm(party_list):
    party_id = party.lower().translate(special_char_map).replace(' ', '-')
    party_iri = URIRef(party_id, re_namespace)
    id_to_iri_dict[party_id] = party_iri
    g.add((party_iri, RDF.type, OWL.NamedIndividual))
    g.add((party_iri, RDF.type, contract_party_uri_ref))
    g.add((party_iri, party_name_uri_ref, Literal(party, datatype=XSD.string)))


ca_uri = URIRef(ca_namespace + 'CollectiveAgreement')
ca_url_uri = URIRef(ca_namespace + 'collectiveAgreementUrl')
scope_uri = URIRef(ca_namespace + 'personalScopeOfApplication')

print("Creating Contracts in KG")
for f in tqdm(glob('./data/final_csv/*.csv')):
    df = pd.read_csv(f, encoding='utf-8', sep=',', header=None)

    worker_type = []
    file_name = f.split('\\')[-1].split('.')[0]
    if 'arb' in file_name:
        worker_type.append('arb')
    if 'ang' in file_name:
        worker_type.append('ang')

    date_of_coming_into_effect = ''
    labor_parties = []
    economic_parties = []

    averaging_periods = []
    daily_normal_working_hours = []
    weekly_normal_working_hours = []
    bonus_pay = []
    anniversary_bonus_pay = []

    name = ''

    this_uri = URIRef(file_name, re_namespace)
    g.add((this_uri, RDF.type, OWL.NamedIndividual))
    g.add((this_uri, RDF.type, ca_uri))
    g.add((this_uri, ca_url_uri, Literal(ca_base_url + file_name, datatype=XSD.anyURI)))

    if 'ang' in worker_type:
        g.add((this_uri, scope_uri, Literal('Angestellte', datatype=XSD.string)))
    if 'arb' in worker_type:
        g.add((this_uri, scope_uri, Literal('Arbeiter', datatype=XSD.string)))

    clause_titles = {}

    for index, row in df.iterrows():
        if isinstance(row[4], str) and isinstance(row[3], str):
            title_parts = [file_name, *row[3].split('>')]
            transformed_title = '_'.join(['_'.join(p.lower().translate(special_char_map).strip().split()) for p in title_parts])
            if transformed_title in clause_titles:
                clause_titles[transformed_title] += 1
            else:
                clause_titles[transformed_title] = 1

            transformed_title += '_' + str(clause_titles[transformed_title])

            clause_uri = URIRef(transformed_title, re_namespace)
            g.add((clause_uri, RDF.type, OWL.NamedIndividual))
            g.add((clause_uri, RDF.type, URIRef(ca_namespace + 'ContractualClause')))
            g.add((clause_uri, URIRef(ca_namespace + 'partOf'), this_uri))
            g.add((this_uri, URIRef(ca_namespace + 'hasContractualClause'), clause_uri))
            g.add((clause_uri, URIRef(ca_namespace + 'heading'), Literal(row[3], datatype=XSD.string)))
            g.add((clause_uri, URIRef(ca_namespace + 'text'), Literal(row[4], datatype=XSD.string)))
            g.add((clause_uri, URIRef(ca_namespace + 'index'), Literal(index, datatype=XSD.int)))

            # Get date of coming into effect
            if len(date_of_coming_into_effect) < 1:
                found = re.search(coming_into_effect_pattern, ' '.join(row[4].split()))
                if found:
                    date_of_coming_into_effect = found.group(1)

            # Get labor parties
            for k in labor_unions.keys():
                for v in labor_unions[k]:
                    if v.lower() in row[4].lower():
                        if k not in labor_parties:
                            labor_parties.append(k)

            for k in economic_unions.keys():
                for v in economic_unions[k]:
                    if v.lower() in row[4].lower():
                        if k not in economic_parties:
                            economic_parties.append(k)

            found = re.search(normal_working_hours_period_pattern, ' '.join(row[4].split()))
            if found:
                averaging_period = []
                if found.group(1) is not None:
                    averaging_period = [found.group(1), row[3]]
                elif found.group(2) is not None:
                    averaging_period = [found.group(2), row[3]]
                elif found.group(3) is not None:
                    averaging_period = [found.group(3), row[3]]
                else:
                    averaging_period = [found.group(4), row[3]]

                averaging_periods.append([averaging_period])
                g.add((clause_uri, URIRef(ca_namespace + 'periodForTheAveragingOfWorkingTime'), Literal(averaging_period[0], datatype=XSD.string)))
                g.add((this_uri, RDF.type, URIRef(ca_namespace + 'NormalWorkingHoursClause')))
                g.add((this_uri, URIRef(ca_namespace + 'hasNormalWorkingHoursClause'), clause_uri))

            found = re.search(daily_normal_working_hours_pattern, ' '.join(row[4].split()))
            if found:
                if found.group(1) is not None:
                    daily_normal_working_hours.append([found.group(1), row[3]])
                    g.add((clause_uri, URIRef(ca_namespace + 'normalWorkingHoursPerDay'), Literal(found.group(1), datatype=XSD.string)))
                    g.add((this_uri, RDF.type, URIRef(ca_namespace + 'NormalWorkingHoursClause')))
                    g.add((this_uri, URIRef(ca_namespace + 'hasNormalWorkingHoursClause'), clause_uri))

            found = re.search(weekly_normal_working_hours_pattern, ' '.join(row[4].split()))
            if found:
                if found.group(1) is not None:
                    weekly_normal_working_hours.append([found.group(1), row[3]])
                    g.add((clause_uri, URIRef(ca_namespace + 'normalWorkingHoursPerWeek'), Literal(found.group(1), datatype=XSD.string)))
                    g.add((this_uri, RDF.type, URIRef(ca_namespace + 'NormalWorkingHoursClause')))
                    g.add((this_uri, URIRef(ca_namespace + 'hasNormalWorkingHoursClause'), clause_uri))
                if found.group(2) is not None:
                    weekly_normal_working_hours.append([found.group(2), row[3]])
                    g.add((clause_uri, URIRef(ca_namespace + 'normalWorkingHoursPerWeek'), Literal(found.group(2), datatype=XSD.string)))
                    g.add((this_uri, RDF.type, URIRef(ca_namespace + 'NormalWorkingHoursClause')))
                    g.add((this_uri, URIRef(ca_namespace + 'hasNormalWorkingHoursClause'), clause_uri))

            if isinstance(row[3], str):
                for synonym in bonus_pay_pattern:
                    if synonym in row[3].lower() or synonym in row[4].lower():
                        bonus_pay.append(row[3])
                        g.add((this_uri, RDF.type, URIRef(ca_namespace + 'BonusPayClause')))
                        g.add((this_uri, URIRef(ca_namespace + 'hasBonusPayClause'), clause_uri))
                        break

                for synonym in anniversary_bonus_pay_pattern:
                    if synonym in row[3].lower() or synonym in row[4].lower():
                        anniversary_bonus_pay.append(row[3])
                        g.add((this_uri, RDF.type, URIRef(ca_namespace + 'AnniversaryBonusPayClause')))
                        g.add((this_uri, URIRef(ca_namespace + 'hasAnniversaryBonusPayClause'), clause_uri))
                        break

            if len(name) < 1:
                if isinstance(row[1], str):
                    found = re.search(name_pattern, row[1])
                    if found:
                        name = found.group(1)

        # Get labor parties in the headline in case it could not be found in the paragraphs
        if len(labor_parties) < 1:
            if isinstance(row[1], str):
                for k in labor_unions.keys():
                    for v in labor_unions[k]:
                        if v.lower() in row[1].lower():
                            if k not in labor_parties:
                                labor_parties.append(k)

        if len(economic_parties) < 1:
            if isinstance(row[1], str):
                for k in economic_unions.keys():
                    for v in economic_unions[k]:
                        if v.lower() in row[1].lower():
                            if k not in economic_parties:
                                economic_parties.append(k)

    if len(name) < 1:
        with open(f'./data/html/{file_name}.html', 'r', encoding='utf-8') as html:
            soup = Bs(html.read(), 'html.parser').find('div', {'class': 'document'})
            added_text_tags = soup.find_all('div', {'class': 'redak'})
            for tag in added_text_tags:
                tag.extract()
        found = re.search(name_pattern, ' '.join(soup.get_text().split()), re.IGNORECASE)
        if found:
            name = ' '.join([part.capitalize() if part.isupper() else part for part in found.group(1).strip().split(' ')])

    possible_endings = ['vom', 'Stand', 'gültig ab', 'abgeschlossen zwischen', 'Diese Rechtsquellen', 'Änderungen', '§', 'gemäß', 'Redaktionelle Anmerkungen', 'in der geltenden Fassung', 'getroffene Vereinbarung', 'Gültig von', 'Öffnungszeiten', 'Abschnitt', 'unterliegen', 'in der Fassung', 'Beschäftigungsgruppen pro Stunde brutto ab', ', folgende Regelungen anzuwenden:', ' Textausgabeder ab', '•']

    if len(name) > 0:
        for ending in possible_endings:
            index = name.lower().find(ending.lower())
            if index > -1:
                name = name[:index]
        if name.endswith('('):
            name = name[:len(name)-2]
    else:
        name = 'Kollektivvertrag für ' + ' '.join([translate_state(part).capitalize() for part in file_name[len('detail-'):].split('-') if part != 'arb' and part != 'ang'])

    g.add((this_uri, URIRef(ca_namespace + 'title'), Literal(name, datatype=XSD.string)))
    if date_of_coming_into_effect:
        for key, value in zip(month_dict.keys(), month_dict.values()):
            date_of_coming_into_effect = date_of_coming_into_effect.lower().replace(key, str(value))
        day_month_year_regex = r'([\d]+)[^\d]+([\d]+)[^\d]+([\d]+)'
        found = re.search(day_month_year_regex, date_of_coming_into_effect)
        if found:
            final_datetime = datetime.datetime(day=int(found.group(1)), month=int(found.group(2)), year=int(found.group(3)), hour=0, minute=0, second=0, tzinfo=pytz.timezone('Europe/Vienna')).isoformat()
            g.add((this_uri, URIRef(ca_namespace + 'dateOfComingIntoEffect'), Literal(final_datetime, datatype=XSD.dateTime)))

    for party in economic_parties:
        p_transformed = party.lower().translate(special_char_map).replace(' ', '-')
        g.add((id_to_iri_dict[p_transformed], URIRef(ca_namespace + 'hasSignedContract'), this_uri))
        g.add((this_uri, URIRef(ca_namespace + 'hasContractParty'), id_to_iri_dict[p_transformed]))
        g.add((this_uri, URIRef(ca_namespace + 'hasContractPartyRepresentingEmployers'), id_to_iri_dict[p_transformed]))

    for party in labor_parties:
        p_transformed = party.lower().translate(special_char_map).replace(' ', '-')
        g.add((id_to_iri_dict[p_transformed], URIRef(ca_namespace + 'hasSignedContract'), this_uri))
        g.add((this_uri, URIRef(ca_namespace + 'hasContractParty'), id_to_iri_dict[p_transformed]))
        g.add((this_uri, URIRef(ca_namespace + 'hasContractPartyRepresentingEmployees'), id_to_iri_dict[p_transformed]))

print("Saving knowledge graph...")
g.serialize(destination="kg.ttl")


#%%
