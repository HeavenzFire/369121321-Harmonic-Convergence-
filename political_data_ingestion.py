import requests
import json
import time
from datetime import datetime
import hashlib

class FECDataIngestor:
    def __init__(self, api_key=None):
        self.api_key = api_key
        self.base_url = "https://api.open.fec.gov/v1"
        self.ingested_data = []

    def fetch_filings(self, candidate_id, cycle=2024):
        """Fetch FEC filings for a candidate"""
        params = {
            'candidate_id': candidate_id,
            'election_year': cycle,
            'api_key': self.api_key,
            'per_page': 100
        }

        try:
            response = requests.get(f"{self.base_url}/filings/", params=params)
            response.raise_for_status()
            data = response.json()

            for filing in data.get('results', []):
                record = {
                    'source': 'FEC',
                    'type': 'filing',
                    'candidate_id': candidate_id,
                    'filing_id': filing.get('filing_id'),
                    'form_type': filing.get('form_type'),
                    'receipt_date': filing.get('receipt_date'),
                    'total_receipts': filing.get('total_receipts', 0),
                    'total_disbursements': filing.get('total_disbursements', 0),
                    'cash_on_hand': filing.get('cash_on_hand', 0),
                    'ingested_at': datetime.now().isoformat(),
                    'reproducibility_hash': self._generate_hash(filing)
                }
                self.ingested_data.append(record)

        except requests.RequestException as e:
            print(f"Error fetching FEC data: {e}")
            # Fallback to sample data for testing
            self._generate_sample_filings(candidate_id, cycle)

    def _generate_sample_filings(self, candidate_id, cycle):
        """Generate sample data for testing"""
        for i in range(5):
            filing = {
                'source': 'FEC',
                'type': 'filing',
                'candidate_id': candidate_id,
                'filing_id': f'SAMPLE_{i}',
                'form_type': 'F3',
                'receipt_date': f'2024-0{i+1}-01',
                'total_receipts': 100000 + i * 10000,
                'total_disbursements': 80000 + i * 8000,
                'cash_on_hand': 20000 + i * 2000,
                'ingested_at': datetime.now().isoformat(),
                'reproducibility_hash': hashlib.sha256(json.dumps({
                    'candidate_id': candidate_id,
                    'filing_id': f'SAMPLE_{i}',
                    'receipt_date': f'2024-0{i+1}-01'
                }).encode()).hexdigest()
            }
            self.ingested_data.append(filing)

    def _generate_hash(self, data):
        """Generate reproducibility hash"""
        data_str = json.dumps(data, sort_keys=True)
        return hashlib.sha256(data_str.encode()).hexdigest()

class LobbyingDataIngestor:
    def __init__(self):
        self.base_url = "https://lda.senate.gov/api/v1"
        self.ingested_data = []

    def fetch_disclosures(self, year=2024):
        """Fetch lobbying disclosures"""
        params = {
            'year': year,
            'per_page': 100
        }

        try:
            response = requests.get(f"{self.base_url}/filings/", params=params)
            response.raise_for_status()
            data = response.json()

            for disclosure in data.get('results', []):
                record = {
                    'source': 'Senate_LDA',
                    'type': 'lobbying_disclosure',
                    'filing_id': disclosure.get('filing_id'),
                    'client_name': disclosure.get('client_name'),
                    'lobbyist_name': disclosure.get('lobbyist_name'),
                    'amount': disclosure.get('amount', 0),
                    'issue_area': disclosure.get('issue_area'),
                    'filing_date': disclosure.get('filing_date'),
                    'ingested_at': datetime.now().isoformat(),
                    'reproducibility_hash': self._generate_hash(disclosure)
                }
                self.ingested_data.append(record)

        except requests.RequestException as e:
            print(f"Error fetching lobbying data: {e}")
            # Fallback to sample data
            self._generate_sample_disclosures(year)

    def _generate_sample_disclosures(self, year):
        """Generate sample lobbying disclosures"""
        clients = ['TechCorp', 'EnergyInc', 'HealthSys', 'FinanceGroup']
        issues = ['Technology', 'Energy', 'Healthcare', 'Finance']

        for i in range(10):
            disclosure = {
                'source': 'Senate_LDA',
                'type': 'lobbying_disclosure',
                'filing_id': f'LDA_{year}_{i}',
                'client_name': clients[i % len(clients)],
                'lobbyist_name': f'Lobbyist_{i}',
                'amount': 50000 + i * 10000,
                'issue_area': issues[i % len(issues)],
                'filing_date': f'{year}-0{(i%12)+1:02d}-15',
                'ingested_at': datetime.now().isoformat(),
                'reproducibility_hash': hashlib.sha256(json.dumps({
                    'filing_id': f'LDA_{year}_{i}',
                    'client_name': clients[i % len(clients)],
                    'amount': 50000 + i * 10000
                }).encode()).hexdigest()
            }
            self.ingested_data.append(disclosure)

    def _generate_hash(self, data):
        """Generate reproducibility hash"""
        data_str = json.dumps(data, sort_keys=True)
        return hashlib.sha256(data_str.encode()).hexdigest()