import requests

from application.app.static.queries import queries
from application.app.constants import SPARQL_ENDPOINT, QUERY_TYPE, TRANSFORMATIONS


class ResponseService:

    @staticmethod
    def transform_value(v: str, transformation):
        if transformation == TRANSFORMATIONS.NONE:
            return v
        if transformation == TRANSFORMATIONS.REMOVE_NS:
            return v.split('/')[-1]
        if transformation == TRANSFORMATIONS.SPLIT_TIME:
            return v.split('T')[0]
        if transformation == TRANSFORMATIONS.SPLIT_GROUP:
            return v.split(';')
        if transformation == TRANSFORMATIONS.SPLIT_GROUP_AND_REMOVE_NS:
            return [ResponseService.transform_value(t, TRANSFORMATIONS.REMOVE_NS) for t in ResponseService.transform_value(v, TRANSFORMATIONS.SPLIT_GROUP)]
        if transformation == TRANSFORMATIONS.CLAUSE_TO_HTML:
            return v.replace(']', '</b><br>').replace('[', '<br><br><b>')
        if transformation == TRANSFORMATIONS.REPLACE_WITH_SLASH:
            return v.replace(' ', '/')

    @staticmethod
    def get_row_attributes(result_rows, attr_trans: dict, aggregate: list | None):
        for result_row in result_rows:
            result_dict = {}
            for key, value in attr_trans.items():
                if key in result_row:
                    if isinstance(value, list):
                        result_dict[key] = [ResponseService.transform_value(result_row[key]['value'], t) for t in value]
                    else:
                        result_dict[key] = ResponseService.transform_value(result_row[key]['value'], value)
                else:
                    result_dict[key] = None
            if aggregate is not None:
                aggregate.append(result_dict)
            else:
                return result_dict
        return aggregate


class RequestService:

    @staticmethod
    def send_request(query):
        return requests.post(SPARQL_ENDPOINT, data={'query': query}).json()

    @staticmethod
    def handle_response_data(data, query_type):
        if query_type == QUERY_TYPE.SELECT:
            return data['results']['bindings']
        if query_type == QUERY_TYPE.ASK:
            return data['boolean']

    @staticmethod
    def get_query_results(query, query_type):
        return RequestService.handle_response_data(data=RequestService.send_request(query=query), query_type=query_type)


class AppService:

    @staticmethod
    def get_contracts(substring: str = ''):
        return ResponseService.get_row_attributes(
            result_rows=RequestService.get_query_results(query=queries.GET_CONTRACTS_WITH_TITLE(substring=substring.lower()),
                                                         query_type=QUERY_TYPE.SELECT),
            attr_trans={
                'c':        TRANSFORMATIONS.REMOVE_NS,
                'n':        TRANSFORMATIONS.NONE,
                'scope':    TRANSFORMATIONS.REPLACE_WITH_SLASH,
                'd':        TRANSFORMATIONS.SPLIT_TIME
            },
            aggregate=[]
        )

    @staticmethod
    def get_contract_info(contract):
        single_contract = ResponseService.get_row_attributes(
            result_rows=RequestService.get_query_results(query=queries.GET_CONTRACT_INFO(contract),
                                                         query_type=QUERY_TYPE.SELECT),
            attr_trans={
                'c': TRANSFORMATIONS.NONE,
                'ti': TRANSFORMATIONS.NONE,
                'd': TRANSFORMATIONS.SPLIT_TIME,
                'scope': TRANSFORMATIONS.NONE,
                'r_parties_name': TRANSFORMATIONS.SPLIT_GROUP,
                'r_parties': TRANSFORMATIONS.SPLIT_GROUP_AND_REMOVE_NS,
                'e_parties_name': TRANSFORMATIONS.SPLIT_GROUP,
                'e_parties': TRANSFORMATIONS.SPLIT_GROUP_AND_REMOVE_NS,
            },
            aggregate=None
        )
        iri = single_contract['c']
        anniversary_bonus_pay_clauses = ResponseService.get_row_attributes(
            result_rows=RequestService.get_query_results(
                                                query=queries.GET_ANNIVERSARY_BONUS_PAY_CLAUSES(iri),
                                                query_type=QUERY_TYPE.SELECT),
            attr_trans={
                'iri': TRANSFORMATIONS.REMOVE_NS,
                'c': TRANSFORMATIONS.NONE
            },
            aggregate=[]
        )
        bonus_pay_clauses = ResponseService.get_row_attributes(
            result_rows=RequestService.get_query_results(
                                                query=queries.GET_BONUS_PAY_CLAUSES(iri),
                                                query_type=QUERY_TYPE.SELECT),
            attr_trans={
                'iri': TRANSFORMATIONS.REMOVE_NS,
                'c': TRANSFORMATIONS.NONE
            },
            aggregate=[]
        )
        normal_working_hours_clauses = ResponseService.get_row_attributes(
            result_rows=RequestService.get_query_results(
                                                query=queries.GET_NORMAL_WORKING_HOURS_CLAUSES(iri),
                                                query_type=QUERY_TYPE.SELECT),
            attr_trans={
                'iri': TRANSFORMATIONS.REMOVE_NS,
                'c': TRANSFORMATIONS.NONE,
                'd': TRANSFORMATIONS.NONE,
                'w': TRANSFORMATIONS.NONE,
                'ap': TRANSFORMATIONS.NONE
            },
            aggregate=[]
        )

        all_clauses = ResponseService.get_row_attributes(
            result_rows=RequestService.get_query_results(
                                                query=queries.GET_CLAUSES(iri),
                                                query_type=QUERY_TYPE.SELECT),
            attr_trans={
                'c': TRANSFORMATIONS.REMOVE_NS,
                't': TRANSFORMATIONS.NONE
            },
            aggregate=[]
        )

        single_contract['c'] = ResponseService.transform_value(single_contract['c'], TRANSFORMATIONS.REMOVE_NS)
        single_contract['e'] = zip(single_contract['e_parties'], single_contract['e_parties_name'])
        single_contract['r'] = zip(single_contract['r_parties'], single_contract['r_parties_name'])
        return [single_contract, anniversary_bonus_pay_clauses, bonus_pay_clauses, normal_working_hours_clauses, all_clauses]

    @staticmethod
    def get_parties(substring: str = ''):
        return ResponseService.get_row_attributes(
            result_rows=RequestService.get_query_results(query=queries.GET_CONTRACT_PARTIES(substring=substring.lower()),
                                                         query_type=QUERY_TYPE.SELECT),
            attr_trans={
                'p_iri': TRANSFORMATIONS.REMOVE_NS,
                'p_name': TRANSFORMATIONS.NONE,
                'side': TRANSFORMATIONS.NONE
            },
            aggregate=[]
        )

    @staticmethod
    def get_party_info(party):
        return ResponseService.get_row_attributes(
            result_rows=RequestService.get_query_results(query=queries.GET_SIGNED_CONTRACTS(party),
                                                         query_type=QUERY_TYPE.SELECT),
            attr_trans={
                'c': TRANSFORMATIONS.REMOVE_NS,
                'n': TRANSFORMATIONS.NONE,
                'p_name': TRANSFORMATIONS.NONE,
                'p': TRANSFORMATIONS.REMOVE_NS
            },
            aggregate=[]
        )

    @staticmethod
    def get_clause_info(clause):
        return ResponseService.get_row_attributes(
            result_rows=RequestService.get_query_results(query=queries.FIND_CLAUSE(clause),
                                                         query_type=QUERY_TYPE.SELECT),
            attr_trans={
                'clause_iri': TRANSFORMATIONS.REMOVE_NS,
                'clause_heading': TRANSFORMATIONS.NONE,
                'contract_iri': TRANSFORMATIONS.REMOVE_NS,
                'contract_name': TRANSFORMATIONS.NONE,
                'text': TRANSFORMATIONS.CLAUSE_TO_HTML,
                'next_clause_iri': TRANSFORMATIONS.REMOVE_NS,
                'next_clause_name': TRANSFORMATIONS.NONE,
                'prev_clause_iri': TRANSFORMATIONS.REMOVE_NS,
                'prev_clause_name': TRANSFORMATIONS.NONE
            },
            aggregate=None
        )