from flask import render_template
from application.app import app
from application.app.service.service import AppService


@app.route('/')
@app.route('/contracts')
def contracts():
    return render_template('contracts.html', title='Contracts', contracts=AppService.get_contracts())


@app.route('/contracts/<contract>')
def single_contract(contract):
    return render_template('contract-detail.html', title='Detailansicht', contract_info=AppService.get_contract_info(contract=contract), zip=zip)


@app.route('/parties')
def parties():
    return render_template('parties.html', title='Parties', parties=AppService.get_parties())


@app.route('/parties/<party>')
def single_party(party):
    return render_template('party-detail.html', title='Party', party=AppService.get_party_info(party=party))


@app.route('/clauses/<clause>')
def clause(clause):
    return render_template('clause.html', title='Klausel', clause=AppService.get_clause_info(clause=clause))