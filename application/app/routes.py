from flask import render_template, request
from application.app import app
from application.app.service.service import AppService
import json


@app.route('/', methods=['GET', 'POST'])
@app.route('/contracts', methods=['GET', 'POST'])
def contracts():
    if request.method == 'POST':
        search_string = request.form['searchString']
        search_results = AppService.get_contracts(search_string)

        return app.response_class(
            response=json.dumps(search_results),
            status=200,
            mimetype='application/json'
        )
    return render_template('contracts.html', title='Contracts', contracts=AppService.get_contracts())


@app.route('/contracts/<contract>')
def single_contract(contract):
    return render_template('contract-detail.html', title='Detailansicht', contract_info=AppService.get_contract_info(contract=contract), zip=zip)


@app.route('/parties', methods=['GET', 'POST'])
def parties():
    if request.method == 'POST':
        search_string = request.form['searchString']
        search_results = AppService.get_parties(search_string)

        return app.response_class(
            response=json.dumps(search_results),
            status=200,
            mimetype='application/json'
        )
    return render_template('parties.html', title='Parties', parties=AppService.get_parties())


@app.route('/parties/<party>')
def single_party(party):
    return render_template('party-detail.html', title='Party', party=AppService.get_party_info(party=party))


@app.route('/clauses/<clause>')
def clause(clause):
    return render_template('clause.html', title='Klausel', clause=AppService.get_clause_info(clause=clause))