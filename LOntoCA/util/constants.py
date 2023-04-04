from rdflib import Namespace


class URLConfig:
    CA_BASE_URL = 'https://www.kollektivvertrag.at'
    CA_DATABASE_BASE_URL = 'https://www.kollektivvertrag.at/cms/KV/KV_1.4/kollektivvertrag-suchen/alphabetische-liste'


class PathConfig:
    CA_PREFIX = 'detail-'
    HTML_DIR = './data/html/'
    STANDING_ORDERS_WILDCARD = f'{HTML_DIR}{CA_PREFIX}do-*.html'
    CSV_DIR = './data/csv/'
    FINAL_CSV_DIR = './data/final_csv/'

    @staticmethod
    def get_file_path(file_name: str, file_type: str, pref: str = 'detail-') -> str:
        return PathConfig.HTML_DIR + pref + file_name + '.' + file_type


class ParseConfig:
    HTMLPARSER = 'html.parser'
    CA_LINK_REGEX = r'<a href="(/kv/[a-zA-Z0-9-]+)">'
    RELATED_DOCUMENTS = 'related_documents'
    TABELLEN_WRAPPER = 'tabellen_wrapper'
    TABELLE = 'tabelle'
    ABS_GR_DIST = '.abs_gr_dist'
    ABSATZ_LITGR = '.absatz_litgr'
    LIT_TEXT_LISTE = 'lit_text_liste'
    SEP = '###SEP###'
    HIERARCHY = ['active', 'kopf1-ve', 'kvgkopf', 'para',
                 'abs_gr', 'absatz', 'lit_gr_dist', 'lit_text_liste', 'ueb',
                 'intended_list', 'vwgrp', 'vwgrp_dist', 'tabellen_wrapper']
    HEADING_LIST = ['kopf1', 'dokheadline_bigger', 'dokheadline', 'abs_grtit', 'absnr', 'abstitel', 'list_nr']
    HEADING_DICT = {
        'active': None,
        'kopf1-ve': 'kopf1',
        'kvgkopf': 'dokheadline_bigger',
        'para': 'dokheadline',
        'abs_gr_dist': 'abs_grtit',
        'abs_gr': 'abs_grtit',
        'absatz': ['absnr', 'abstitel'],
        'absatz_litgr': ['absnr', 'abstitel'],
        'intended_list': 'list_nr',
        'vwgrp': 'grptitel',
        'vwgrp_dist': 'grptitel',
        'tabellen_wrapper': '',
        'lit_text_liste': '',
        'ueb': ''
    }
    ENCODING = 'utf-8'


class ExtractionConfig:
    COMING_INTO_EFFECT_PATTERN = r'(?:tritt|treten|ist\sam).*(((\d+\.\s?\d+\.\s?\d{4}))|([\d]+\.\s?[a-zA-Zä]+\s[\d]{4})).*in\sKraft'
    NORMAL_WORKING_HOURS_PERIOD_PATTERN = r'(?:(?:Durchrechnungszeitraum)|(?:(?:(?:Normalarbeitszeit)|(?:Wochenarbeitszeit))[^\.]*eines Zeitraumes)|(?:Innerhalb eines Abrechnungszeitraumes))[^\.]*\s((?:(?:ein(?:em)?|zwei|drei|vier|fünf|sechs|sieben|acht|neun|zehn|elf|zwölf)|[0-9]+) (?:(?:Tage)|(?:Woche)|(?:(?:Kalender)?[mM]onat)|(?:Jahr))[en]*)|in(?:nerhalb)? eine[ms] ([a-zäöü]+(?:wöchig|tägig|monatig|jährig))[en]*\s(?:Durchrechnungs)?[zZ]eitraum|Normalarbeitszeit.*überschreit.*\s((?:[a-zäöü]+(?:wöchig|tägig|monatig|jährig))[en]*)\sDurchschnitt|[aA]m Ende des (.*jährlich)[en]*\sDurchrechnungszeitraumes'
    DAILY_NORMAL_WORKING_HOURS_PATTERN = r'[Tt]ägliche(?:\sHöchstgrenze der)? Normalarbeitszeit.*\s((?:(?:[0-9]+)|(?:[a-zöüä]+))\sStunden)'
    WEEKLY_NORMAL_WORKING_HOURS_PATTERN = r'(?:(?:[Ww]öchentliche(?:\sHöchstgrenze der)? Normalarbeitszeit)|(?:wöchentliche Arbeitszeit))[^.^;]*\s((?:(?:[0-9]+,?[0-9]?)|(?:[a-zöüä]+))\sStunden)|normale Arbeitszeit[^\.^;]*wöchentlich\s((?:(?:[0-9]+,?[0-9]?)|(?:[a-zöüä]+))\sStunden)'
    BONUS_PAY_PATTERN = ['sonderzahlung', 'urlaubszuschuss', 'urlaubsgeld', 'weihnachtsremuneration']
    NAME_PATTERN = r'((?:(?:Rahmen\s?)?[kK]ollektivvertrag|Dienst- und Besoldungsornung (?:\(DBO\))?) (?:(?:(?:für)|(?:betreffend)) [^\.]+))\s[^\.]\.'
    ANNIVERSARY_BONUS_PAY_PATTERN = ['jubiläumszuwendung', 'dienstjubiläum', 'dienstjubiläen', 'jubiläumsgeld']
    LABOR_UNIONS = {
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
    ECONOMIC_UNIONS = {
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
    MONTH_DICT = {
        'jänner': 1,
        'jannuar': 1,
        'februar': 2,
        'märz': 3,
        'april': 4,
        'mai': 5,
        'juni': 6,
        'juli': 7,
        'august': 8,
        'september': 9,
        'oktober': 10,
        'november': 11,
        'dezember': 12
    }
    SPECIAL_CHAR_MAP = {
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
    POSSIBLE_ENDINGS = ['vom', 'Stand', 'gültig ab', 'abgeschlossen zwischen', 'Diese Rechtsquellen', 'Änderungen', '§', 'gemäß', 'Redaktionelle Anmerkungen', 'in der geltenden Fassung', 'getroffene Vereinbarung', 'Gültig von', 'Öffnungszeiten', 'Abschnitt', 'unterliegen', 'in der Fassung', 'Beschäftigungsgruppen pro Stunde brutto ab', ', folgende Regelungen anzuwenden:', ' Textausgabeder ab', '•']
    DAY_MONTH_YEAR_REGEX = r'([\d]+)[^\d]+([\d]+)[^\d]+([\d]+)'


    @staticmethod
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


class OntologyConfig:
    BASE_NAMESPACE = 'https://semantics.id/ns/'
    CA_NS = Namespace(BASE_NAMESPACE + 'CollectiveAgreement#')
    RE_NS = Namespace(BASE_NAMESPACE + 'resource/')
    FINAL_GRAPH_NAME = 'kg.ttl'

# List of files that cannot be parsed
TO_BE_DELETED = [
    './data/html/detail-aehrenstolz-backwaren-u-muehlenind-arb.html',
    './data/html/detail-auslaendische-luftverkehrsgesellschaften-in-oest-htv-ang.html',
    './data/html/detail-baeuerliche-betriebe-stm-arb.html',
    './data/html/detail-baeuerliche-betriebe-s-arb.html',
    './data/html/detail-bordpersonal-austrian-air-services-ang.html',
    './data/html/detail-bordpersonal-austrian-airlines-und-lauda-air-ang.html',
    './data/html/detail-do-b-kfa-aerzte-und-dentisten-ang.html', # IMPOSSIBLE TO PARSE! Wrong classes!!
    './data/html/detail-donauschiffahrt-arb.html',
    './data/html/detail-general-kv-urlaubsgesetz-entgelt-arb-ang.html',
    './data/html/detail-int-schlafwagen-und-touristikges-werkstaette-wien-arb.html',
    './data/html/detail-landeskuranstalten-ooe-arb-ang.html',
    './data/html/detail-landwirtschaftliche-gutsbetriebe-stm-arb.html',
    './data/html/detail-landwirtschaftliche-gutsbetriebe-s-arb.html',
    './data/html/detail-landwirtschaftsbetriebe-gemeinde-wien-arb.html',
    './data/html/detail-lauda-air-bordpersonal-ang.html',
    './data/html/detail-konsum-arb.html',
    './data/html/detail-mieder-und-waeschewarenerzeuger-arb.html',
    './data/html/detail-steiermaerkische-landesbahnen-ang.html',
    './data/html/detail-suesswarenindustrie-konsolidiert-ang.html',
    './data/html/detail-taxi-vlb-arb.html',
    './data/html/detail-zementindustrie-arb.html'
]




