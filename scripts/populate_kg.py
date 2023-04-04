from pandas import read_csv
from glob import glob
from tqdm import tqdm
from bs4 import BeautifulSoup as Bs
from rdflib import Graph, URIRef, Literal
from rdflib.namespace import RDF, OWL, RDFS, XSD
from LOntoCA.util.constants import ExtractionConfig, OntologyConfig, URLConfig, PathConfig, ParseConfig
import re
import pytz
import datetime


def _add_contract_party(g: Graph, party: str, relation: str):
    p_transformed = party.lower().translate(ExtractionConfig.SPECIAL_CHAR_MAP).replace(' ', '-')
    g.add((id_to_iri_dict[p_transformed], URIRef(OntologyConfig.CA_NS + 'hasSignedContract'), this_uri))
    g.add((this_uri, URIRef(OntologyConfig.CA_NS + 'hasContractParty'), id_to_iri_dict[p_transformed]))
    g.add((this_uri, URIRef(OntologyConfig.CA_NS + relation), id_to_iri_dict[p_transformed]))


if __name__ == '__main__':
    # Initialize Graph
    g = Graph(base=OntologyConfig.CA_NS)
    g.parse(OntologyConfig.CA_NS)
    g.bind('re', OntologyConfig.RE_NS)  # Namespace for instances
    g.bind('', OntologyConfig.CA_NS)    # Base Namespace

    # List of all known parties
    party_list = [*ExtractionConfig.LABOR_UNIONS.keys(), *ExtractionConfig.ECONOMIC_UNIONS.keys()]

    counter = 0
    id_to_iri_dict = {}
    party_name_uri_ref = URIRef(OntologyConfig.CA_NS + 'partyName')
    contract_party_uri_ref = URIRef(OntologyConfig.CA_NS + 'ContractParty')

    # Create an index in order to structure clauses
    g.add((URIRef(OntologyConfig.CA_NS + 'index'), RDF.type, OWL.DatatypeProperty))
    g.add((URIRef(OntologyConfig.CA_NS + 'index'), RDFS.domain, URIRef(OntologyConfig.CA_NS + 'ContractualClause')))
    g.add((URIRef(OntologyConfig.CA_NS + 'index'), RDFS.range, XSD.int))

    # Initialize the contract parties first
    print("Creating Contract Parties in KG..")
    for party in tqdm(party_list):
        party_id = party.lower().translate(ExtractionConfig.SPECIAL_CHAR_MAP).replace(' ', '-')
        party_iri = URIRef(party_id, OntologyConfig.RE_NS)
        id_to_iri_dict[party_id] = party_iri
        g.add((party_iri, RDF.type, OWL.NamedIndividual))
        g.add((party_iri, RDF.type, contract_party_uri_ref))
        g.add((party_iri, party_name_uri_ref, Literal(party, datatype=XSD.string)))


    ca_uri = URIRef(OntologyConfig.CA_NS + 'CollectiveAgreement')
    ca_url_uri = URIRef(OntologyConfig.CA_NS + 'collectiveAgreementUrl')
    scope_uri = URIRef(OntologyConfig.CA_NS + 'personalScopeOfApplication')

    # Now iterate over the collective agreements
    print("Creating Contracts in KG")
    for f in tqdm(glob(f'{PathConfig.FINAL_CSV_DIR}*.csv')):
        df = read_csv(f, encoding=ParseConfig.ENCODING, sep=',', header=None)

        # Extract worker type
        worker_type = []
        file_name = f.split('\\')[-1].split('.')[0]
        if 'arb' in file_name:
            worker_type.append('arb')
        if 'ang' in file_name:
            worker_type.append('ang')

        # Initialize variables
        date_of_coming_into_effect = ''
        labor_parties = []
        economic_parties = []
        averaging_periods = []
        daily_normal_working_hours = []
        weekly_normal_working_hours = []
        bonus_pay = []
        anniversary_bonus_pay = []
        name = ''

        # Initialize Contract in Knowledge Graph
        this_uri = URIRef(file_name, OntologyConfig.RE_NS)
        g.add((this_uri, RDF.type, OWL.NamedIndividual))
        g.add((this_uri, RDF.type, ca_uri))
        g.add((this_uri, ca_url_uri, Literal(URLConfig.CA_BASE_URL + file_name, datatype=XSD.anyURI)))

        # Add Worker Type
        if 'ang' in worker_type:
            g.add((this_uri, scope_uri, Literal('Angestellte', datatype=XSD.string)))
        if 'arb' in worker_type:
            g.add((this_uri, scope_uri, Literal('Arbeiter', datatype=XSD.string)))

        clause_titles = {}

        # Go over contract rows (each row is a clause)
        for index, row in df.iterrows():
            if isinstance(row[4], str) and isinstance(row[3], str):
                # A clause has a title and an id, the id has to be unique
                # For this reason, a counter is added to the end of the id
                title_parts = [file_name, *row[3].split('>')]
                transformed_title = '_'.join(['_'.join(p.lower().translate(ExtractionConfig.SPECIAL_CHAR_MAP).strip().split()) for p in title_parts])
                if transformed_title in clause_titles:
                    clause_titles[transformed_title] += 1
                else:
                    clause_titles[transformed_title] = 1

                transformed_title += '_' + str(clause_titles[transformed_title])

                # Create clause
                clause_uri = URIRef(transformed_title, OntologyConfig.RE_NS)
                g.add((clause_uri, RDF.type, OWL.NamedIndividual))
                g.add((clause_uri, RDF.type, URIRef(OntologyConfig.CA_NS + 'ContractualClause')))
                g.add((clause_uri, URIRef(OntologyConfig.CA_NS + 'partOf'), this_uri))
                g.add((this_uri, URIRef(OntologyConfig.CA_NS + 'hasContractualClause'), clause_uri))
                g.add((clause_uri, URIRef(OntologyConfig.CA_NS + 'heading'), Literal(row[3], datatype=XSD.string)))
                g.add((clause_uri, URIRef(OntologyConfig.CA_NS + 'text'), Literal(row[4], datatype=XSD.string)))
                g.add((clause_uri, URIRef(OntologyConfig.CA_NS + 'index'), Literal(index, datatype=XSD.int)))

                # Get date of coming into effect
                if len(date_of_coming_into_effect) < 1:
                    found = re.search(ExtractionConfig.COMING_INTO_EFFECT_PATTERN, ' '.join(row[4].split()))
                    if found:
                        date_of_coming_into_effect = found.group(1)

                # Get labor parties
                for k in ExtractionConfig.LABOR_UNIONS.keys():
                    for v in ExtractionConfig.LABOR_UNIONS[k]:
                        if v.lower() in row[4].lower():
                            if k not in labor_parties:
                                labor_parties.append(k)

                # Get economic parties
                for k in ExtractionConfig.ECONOMIC_UNIONS.keys():
                    for v in ExtractionConfig.ECONOMIC_UNIONS[k]:
                        if v.lower() in row[4].lower():
                            if k not in economic_parties:
                                economic_parties.append(k)

                # Get the period for averaging normal working hours
                found = re.search(ExtractionConfig.NORMAL_WORKING_HOURS_PERIOD_PATTERN, ' '.join(row[4].split()))
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
                    g.add((clause_uri, URIRef(OntologyConfig.CA_NS + 'periodForTheAveragingOfWorkingTime'), Literal(averaging_period[0], datatype=XSD.string)))
                    g.add((this_uri, RDF.type, URIRef(OntologyConfig.CA_NS + 'NormalWorkingHoursClause')))
                    g.add((this_uri, URIRef(OntologyConfig.CA_NS + 'hasNormalWorkingHoursClause'), clause_uri))

                # Get daily normal working hours
                found = re.search(ExtractionConfig.DAILY_NORMAL_WORKING_HOURS_PATTERN, ' '.join(row[4].split()))
                if found:
                    if found.group(1) is not None:
                        daily_normal_working_hours.append([found.group(1), row[3]])
                        g.add((clause_uri, URIRef(OntologyConfig.CA_NS + 'normalWorkingHoursPerDay'), Literal(found.group(1), datatype=XSD.string)))
                        g.add((this_uri, RDF.type, URIRef(OntologyConfig.CA_NS + 'NormalWorkingHoursClause')))
                        g.add((this_uri, URIRef(OntologyConfig.CA_NS + 'hasNormalWorkingHoursClause'), clause_uri))

                # Get weekly normal working hours
                found = re.search(ExtractionConfig.WEEKLY_NORMAL_WORKING_HOURS_PATTERN, ' '.join(row[4].split()))
                if found:
                    if found.group(1) is not None:
                        weekly_normal_working_hours.append([found.group(1), row[3]])
                        g.add((clause_uri, URIRef(OntologyConfig.CA_NS + 'normalWorkingHoursPerWeek'), Literal(found.group(1), datatype=XSD.string)))
                        g.add((this_uri, RDF.type, URIRef(OntologyConfig.CA_NS + 'NormalWorkingHoursClause')))
                        g.add((this_uri, URIRef(OntologyConfig.CA_NS + 'hasNormalWorkingHoursClause'), clause_uri))
                    if found.group(2) is not None:
                        weekly_normal_working_hours.append([found.group(2), row[3]])
                        g.add((clause_uri, URIRef(OntologyConfig.CA_NS + 'normalWorkingHoursPerWeek'), Literal(found.group(2), datatype=XSD.string)))
                        g.add((this_uri, RDF.type, URIRef(OntologyConfig.CA_NS + 'NormalWorkingHoursClause')))
                        g.add((this_uri, URIRef(OntologyConfig.CA_NS + 'hasNormalWorkingHoursClause'), clause_uri))

                # Check if clause is about bonus pay
                if isinstance(row[3], str):
                    for synonym in ExtractionConfig.BONUS_PAY_PATTERN:
                        if synonym in row[3].lower() or synonym in row[4].lower():
                            bonus_pay.append(row[3])
                            g.add((this_uri, RDF.type, URIRef(OntologyConfig.CA_NS + 'BonusPayClause')))
                            g.add((this_uri, URIRef(OntologyConfig.CA_NS + 'hasBonusPayClause'), clause_uri))
                            break

                    # ... or about anniversary bonus pay
                    for synonym in ExtractionConfig.ANNIVERSARY_BONUS_PAY_PATTERN:
                        if synonym in row[3].lower() or synonym in row[4].lower():
                            anniversary_bonus_pay.append(row[3])
                            g.add((this_uri, RDF.type, URIRef(OntologyConfig.CA_NS + 'AnniversaryBonusPayClause')))
                            g.add((this_uri, URIRef(OntologyConfig.CA_NS + 'hasAnniversaryBonusPayClause'), clause_uri))
                            break

                # If the contract's name has not yet been found, look for it in column 1 (=> document name)
                if len(name) < 1:
                    if isinstance(row[1], str):
                        found = re.search(ExtractionConfig.NAME_PATTERN, row[1])
                        if found:
                            name = found.group(1)

            # Get labor parties in the headline in case it could not be found in the paragraphs
            if len(labor_parties) < 1:
                if isinstance(row[1], str):
                    for k in ExtractionConfig.LABOR_UNIONS.keys():
                        for v in ExtractionConfig.LABOR_UNIONS[k]:
                            if v.lower() in row[1].lower():
                                if k not in labor_parties:
                                    labor_parties.append(k)

            # Get economic parties in the headline in case it could not be found in the paragraphs
            if len(economic_parties) < 1:
                if isinstance(row[1], str):
                    for k in ExtractionConfig.ECONOMIC_UNIONS.keys():
                        for v in ExtractionConfig.ECONOMIC_UNIONS[k]:
                            if v.lower() in row[1].lower():
                                if k not in economic_parties:
                                    economic_parties.append(k)

        # If the name has still not been found, take the name from a 'redak' elements (redaktionelle anmerkungen)
        if len(name) < 1:
            with open(f'{PathConfig.HTML_DIR}{file_name}.html', 'r', encoding=ParseConfig.ENCODING) as html:
                soup = Bs(html.read(), ParseConfig.HTMLPARSER).find('div', {'class': 'document'})
                added_text_tags = soup.find_all('div', {'class': 'redak'})
                for tag in added_text_tags:
                    tag.extract()
            found = re.search(ExtractionConfig.NAME_PATTERN, ' '.join(soup.get_text().split()), re.IGNORECASE)
            if found:
                name = ' '.join([part.capitalize() if part.isupper() else part for part in found.group(1).strip().split(' ')])

        # Cut the name off at certain keywords
        if len(name) > 0:
            for ending in ExtractionConfig.POSSIBLE_ENDINGS:
                index = name.lower().find(ending.lower())
                if index > -1:
                    name = name[:index]
            if name.endswith('('):
                name = name[:len(name)-2]

        # If no name was found, simply construct it from the file id
        else:
            name = 'Kollektivvertrag für ' + ' '.join([ExtractionConfig.translate_state(part).capitalize() for part in file_name[len('detail-'):].split('-') if part != 'arb' and part != 'ang'])

        # Add the title to the knowledge graph
        g.add((this_uri, URIRef(OntologyConfig.CA_NS + 'title'), Literal(name, datatype=XSD.string)))

        # Transform the date of coming into effect and add it to the knowledge graph
        if date_of_coming_into_effect:
            for key, value in zip(ExtractionConfig.MONTH_DICT.keys(), ExtractionConfig.MONTH_DICT.values()):
                date_of_coming_into_effect = date_of_coming_into_effect.lower().replace(key, str(value))
            found = re.search(ExtractionConfig.DAY_MONTH_YEAR_REGEX, date_of_coming_into_effect)
            if found:
                final_datetime = datetime.datetime(day=int(found.group(1)), month=int(found.group(2)), year=int(found.group(3)), hour=0, minute=0, second=0, tzinfo=pytz.timezone('Europe/Vienna')).isoformat()
                g.add((this_uri, URIRef(OntologyConfig.CA_NS + 'dateOfComingIntoEffect'), Literal(final_datetime, datatype=XSD.dateTime)))

        # Add relation between contract and parties
        for party in economic_parties:
            _add_contract_party(g=g, party=party, relation='hasContractPartyRepresentingEmployers')

        for party in labor_parties:
            _add_contract_party(g=g, party=party, relation='hasContractPartyRepresentingEmployees')

    # Export populated knowledge graph
    print("Saving knowledge graph...")
    g.serialize(destination=OntologyConfig.FINAL_GRAPH_NAME)

