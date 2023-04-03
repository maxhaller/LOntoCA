def GET_CONTRACTS_WITH_TITLE():
    return'''
    PREFIX : <https://semantics.id/ns/>
    PREFIX re: <https://semantics.id/ns/resource/>
    
    SELECT DISTINCT ?c ?n (GROUP_CONCAT(?t) AS ?scope) ?d 
    WHERE {
        ?c a :CollectiveAgreement . 
        ?c :title ?n . 
        ?c :personalScopeOfApplication ?t . 
        ?c :dateOfComingIntoEffect ?d
    } 
    GROUP BY ?c ?n ?d 
    ORDER BY ?n
    '''


def GET_CONTRACT(substring: str):
    return f'''
    PREFIX : <https://semantics.id/ns/> 
    PREFIX re: <https://semantics.id/ns/resource/>
    
    SELECT ?c 
    WHERE {{
      ?s a :CollectiveAgreement .
      ?s :title ?c .
      FILTER REGEX(str(?s), "{substring}")
    }}
    '''


def GET_CONTRACT_INFO(substring: str):
    return f'''
    PREFIX : <https://semantics.id/ns/> 
    PREFIX re: <https://semantics.id/ns/resource/>

SELECT DISTINCT ?c ?ti ?d (GROUP_CONCAT(DISTINCT ?t ;separator="/") AS ?scope) (GROUP_CONCAT(DISTINCT ?pr ; separator=";") AS ?r_parties) (GROUP_CONCAT(DISTINCT ?prn ; separator=";") AS ?r_parties_name) (GROUP_CONCAT(DISTINCT ?pe ; separator=";") AS ?e_parties) (GROUP_CONCAT(DISTINCT ?pen ; separator=";") AS ?e_parties_name)
    WHERE {{
    ?c a :CollectiveAgreement .
      ?c :title ?ti .
    OPTIONAL {{
      ?c :hasContractPartyRepresentingEmployers ?pr .
      ?pr :partyName ?prn .
    }}
    OPTIONAL {{
        ?c :hasContractPartyRepresentingEmployees ?pe .
        ?pe :partyName ?pen .
    }}
      ?c :personalScopeOfApplication ?t .
      ?c :dateOfComingIntoEffect ?d .
      FILTER regex(str(?c), "{substring}")
    }} GROUP BY ?c ?ti ?d
    '''


def HAS_ANNIVERSARY_BONUS_PAY_CLAUSE(iri: str):
    return f'''
    PREFIX : <https://semantics.id/ns/> 
    PREFIX re: <https://semantics.id/ns/resource/>
    
    ASK {{
        <{iri}> :hasAnniversaryBonusPayClause ?o
    }}
    '''


def GET_ANNIVERSARY_BONUS_PAY_CLAUSES(iri: str):
    return f'''
    PREFIX : <https://semantics.id/ns/> 
    PREFIX re: <https://semantics.id/ns/resource/>
    
    SELECT ?iri ?c WHERE {{
        <{iri}> :hasAnniversaryBonusPayClause ?iri .
        ?iri :heading ?c
    }} ORDER BY ?c
    '''

def HAS_BONUS_PAY_CLAUSE(iri: str):
    return f'''
    PREFIX : <https://semantics.id/ns/> 
    PREFIX re: <https://semantics.id/ns/resource/>
    
    ASK {{
        <{iri}> :hasBonusPayClause ?o
    }}
    '''


def GET_BONUS_PAY_CLAUSES(iri: str):
    return f'''
    PREFIX : <https://semantics.id/ns/> 
    PREFIX re: <https://semantics.id/ns/resource/>
    
    SELECT ?iri ?c WHERE {{
        <{iri}> :hasBonusPayClause ?iri .
        ?iri :heading ?c
    }} ORDER BY ?c
    '''


def GET_NORMAL_WORKING_HOURS_CLAUSES(iri: str):
    return f'''
    PREFIX : <https://semantics.id/ns/> 
    PREFIX re: <https://semantics.id/ns/resource/>
    
    SELECT ?iri ?c ?d ?w ?ap WHERE {{
        <{iri}> 
     :hasNormalWorkingHoursClause ?iri .
        ?iri :heading ?c .
        OPTIONAL {{ ?iri :normalWorkingHoursPerDay ?d . }}
        OPTIONAL {{ ?iri :normalWorkingHoursPerWeek ?w . }}
        OPTIONAL {{ ?iri :periodForTheAveragingOfWorkingTime ?ap . }}
    }} ORDER BY ?c
    '''


def GET_CLAUSES(iri: str):
    return f'''
    PREFIX : <https://semantics.id/ns/> 
    PREFIX re: <https://semantics.id/ns/resource/>
    
    SELECT ?c ?t WHERE {{
        ?c :partOf <{iri}> .
        ?c :heading ?t .
        ?c :index ?i
    }} ORDER BY ?i
    '''


def FIND_CLAUSE(substring: str):
    return f'''
    PREFIX : <https://semantics.id/ns/> 
    PREFIX re: <https://semantics.id/ns/resource/>
    PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
    
    SELECT ?clause_iri ?clause_heading ?text ?contract_iri ?contract_name ?prev_clause_iri ?prev_clause_name ?next_clause_iri ?next_clause_name ?next_i ?next_index WHERE {{
        ?clause_iri a :ContractualClause .
        ?clause_iri :heading ?clause_heading .
        ?clause_iri :partOf ?contract_iri .
        ?contract_iri :title ?contract_name .
        ?clause_iri :text ?text .
        ?clause_iri :index ?i .
        FILTER REGEX(str(?clause_iri), '{substring}') .
        BIND (xsd:int(?i - 1) AS ?prev_i)
        BIND (xsd:int(?i + 1) AS ?next_i)
        OPTIONAL {{ ?prev_clause_iri a :ContractualClause . ?prev_clause_iri :partOf ?contract_iri . ?prev_clause_iri :index ?prev_index . ?prev_clause_iri :heading ?prev_clause_name . FILTER (?prev_index = ?prev_i) }}
        OPTIONAL {{ ?next_clause_iri a :ContractualClause . ?next_clause_iri :partOf ?contract_iri . ?next_clause_iri :index ?next_index . ?next_clause_iri :heading ?next_clause_name . FILTER (?next_i = ?next_index) }}
    }}
    '''

def GET_CONTRACT_PARTIES():
    return f'''
    PREFIX : <https://semantics.id/ns/> 
    PREFIX re: <https://semantics.id/ns/resource/>
        
    SELECT ?p_iri ?p_name ?side WHERE {{
        ?p_iri a :ContractParty .
      ?p_iri :partyName ?p_name .
      BIND (if ( EXISTS {{ ?c1 a :CollectiveAgreement . ?c1 :hasContractPartyRepresentingEmployees ?p_iri }}, 
          if ( EXISTS {{ ?c2 a :CollectiveAgreement . ?c2 :hasContractPartyRepresentingEmployers ?p_iri }}, 'Arbeitnehmer / Arbeitgeber' , 'Arbeitnehmer' ), 
          if ( EXISTS {{ ?c3 a :CollectiveAgreement . ?c3 :hasContractPartyRepresentingEmployers ?p_iri }}, 'Arbeitgeber' , 'Unbekannt' )) AS ?side)
      }}
    '''

def GET_SIGNED_CONTRACTS(substring: str):
    return f'''
    PREFIX : <https://semantics.id/ns/> 
    PREFIX re: <https://semantics.id/ns/resource/>
        
    SELECT ?c ?n ?p ?p_name WHERE {{
    ?c a :CollectiveAgreement .
    ?c :hasContractParty ?p .
    ?p :partyName ?p_name .
      ?c :title ?n .
      FILTER REGEX (str(?p), "{substring}")
      }} ORDER BY ?n
    '''