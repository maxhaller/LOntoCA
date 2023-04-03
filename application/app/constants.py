from enum import Enum

HOST = 'http://localhost'
PORT = '3030'
NS = 'CollectiveAgreement'
SPARQL_ENDPOINT = f'{HOST}:{PORT}/{NS}/sparql'


class QUERY_TYPE(Enum):
    SELECT, ASK = range(2)


class TRANSFORMATIONS(Enum):
    NONE, REMOVE_NS, CLAUSE_TO_HTML, SPLIT_GROUP, SPLIT_GROUP_AND_REMOVE_NS, SPLIT_TIME, REPLACE_WITH_SLASH = range(7)

