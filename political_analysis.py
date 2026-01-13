import numpy as np
import pandas as pd
from scipy import stats
from datetime import datetime, timedelta
import json
import hashlib

class PoliticalAnalysis:
    def __init__(self, storage):
        self.storage = storage

    def analyze_filing_changes(self, candidate_id, period_days=90):
        """Analyze changes in FEC filings over time"""
        filings = self.storage.get_fec_filings(candidate_id=candidate_id)

        if len(filings) < 2:
            return []

        # Convert to DataFrame for analysis
        df = pd.DataFrame(filings, columns=[
            'id', 'candidate_id', 'filing_id', 'form_type', 'receipt_date',
            'total_receipts', 'total_disbursements', 'cash_on_hand',
            'ingested_at', 'reproducibility_hash', 'source'
        ])

        df['receipt_date'] = pd.to_datetime(df['receipt_date'])
        df = df.sort_values('receipt_date')

        results = []

        # Calculate period-over-period changes
        for i in range(1, len(df)):
            prev = df.iloc[i-1]
            curr = df.iloc[i]

            # Calculate changes
            receipts_change = curr['total_receipts'] - prev['total_receipts']
            disbursements_change = curr['total_disbursements'] - prev['total_disbursements']
            cash_change = curr['cash_on_hand'] - prev['cash_on_hand']

            # Calculate rates
            days_diff = (curr['receipt_date'] - prev['receipt_date']).days
            if days_diff > 0:
                receipts_rate = receipts_change / days_diff
                disbursements_rate = disbursements_change / days_diff
                cash_rate = cash_change / days_diff
            else:
                receipts_rate = disbursements_rate = cash_rate = 0

            # Statistical significance (simple t-test approximation)
            if len(df) > 2:
                historical_mean = df['total_receipts'].iloc[:i].mean()
                historical_std = df['total_receipts'].iloc[:i].std()
                if historical_std > 0:
                    z_score = (curr['total_receipts'] - historical_mean) / historical_std
                    p_value = 2 * (1 - stats.norm.cdf(abs(z_score)))
                    confidence = 1 - p_value
                else:
                    z_score = 0
                    p_value = 1.0
                    confidence = 0.0
            else:
                z_score = 0
                p_value = 1.0
                confidence = 0.0

            # Store results
            result = {
                'analysis_type': 'filing_changes',
                'candidate_id': candidate_id,
                'period_start': prev['receipt_date'].isoformat(),
                'period_end': curr['receipt_date'].isoformat(),
                'metric_name': 'receipts_change',
                'metric_value': receipts_change,
                'confidence': confidence,
                'p_value': p_value
            }
            self.storage.store_analysis_result(**result)
            results.append(result)

            # Additional metrics
            for metric_name, value in [
                ('disbursements_change', disbursements_change),
                ('cash_change', cash_change),
                ('receipts_rate', receipts_rate),
                ('disbursements_rate', disbursements_rate),
                ('cash_rate', cash_rate)
            ]:
                result_copy = result.copy()
                result_copy['metric_name'] = metric_name
                result_copy['metric_value'] = value
                self.storage.store_analysis_result(**result_copy)
                results.append(result_copy)

        return results

    def analyze_donation_patterns(self, candidate_id, period_days=90):
        """Analyze donation patterns and anomalies"""
        filings = self.storage.get_fec_filings(candidate_id=candidate_id)

        if len(filings) < 3:
            return []

        df = pd.DataFrame(filings, columns=[
            'id', 'candidate_id', 'filing_id', 'form_type', 'receipt_date',
            'total_receipts', 'total_disbursements', 'cash_on_hand',
            'ingested_at', 'reproducibility_hash', 'source'
        ])

        df['receipt_date'] = pd.to_datetime(df['receipt_date'])
        df = df.sort_values('receipt_date')

        results = []

        # Detect donation spikes
        df['receipts_diff'] = df['total_receipts'].diff()
        df['rolling_mean'] = df['receipts_diff'].rolling(window=3, center=True).mean()
        df['rolling_std'] = df['receipts_diff'].rolling(window=3, center=True).std()

        for idx, row in df.iterrows():
            if pd.isna(row['rolling_mean']) or pd.isna(row['rolling_std']) or row['rolling_std'] == 0:
                continue

            z_score = (row['receipts_diff'] - row['rolling_mean']) / row['rolling_std']
            p_value = 2 * (1 - stats.norm.cdf(abs(z_score)))
            confidence = 1 - p_value

            if abs(z_score) > 2:  # Significant spike/dip
                result = {
                    'analysis_type': 'donation_patterns',
                    'candidate_id': candidate_id,
                    'period_start': row['receipt_date'].isoformat(),
                    'period_end': row['receipt_date'].isoformat(),
                    'metric_name': 'donation_anomaly',
                    'metric_value': z_score,
                    'confidence': confidence,
                    'p_value': p_value
                }
                self.storage.store_analysis_result(**result)
                results.append(result)

        return results

    def analyze_lobbying_conflicts(self, candidate_id, period_days=180):
        """Analyze potential conflicts between lobbying and political activity"""
        filings = self.storage.get_fec_filings(candidate_id=candidate_id)
        disclosures = self.storage.get_lobbying_disclosures()

        if not filings or not disclosures:
            return []

        # Convert to DataFrames
        filings_df = pd.DataFrame(filings, columns=[
            'id', 'candidate_id', 'filing_id', 'form_type', 'receipt_date',
            'total_receipts', 'total_disbursements', 'cash_on_hand',
            'ingested_at', 'reproducibility_hash', 'source'
        ])
        filings_df['receipt_date'] = pd.to_datetime(filings_df['receipt_date'])

        disclosures_df = pd.DataFrame(disclosures, columns=[
            'id', 'filing_id', 'client_name', 'lobbyist_name', 'amount',
            'issue_area', 'filing_date', 'ingested_at', 'reproducibility_hash', 'source'
        ])
        disclosures_df['filing_date'] = pd.to_datetime(disclosures_df['filing_date'])

        results = []

        # Look for temporal correlations between large donations and lobbying activity
        for idx, filing in filings_df.iterrows():
            filing_date = filing['receipt_date']

            # Look for lobbying activity within the period
            period_start = filing_date - timedelta(days=period_days)
            period_end = filing_date + timedelta(days=period_days)

            relevant_disclosures = disclosures_df[
                (disclosures_df['filing_date'] >= period_start) &
                (disclosures_df['filing_date'] <= period_end)
            ]

            if len(relevant_disclosures) > 0:
                total_lobbying_amount = relevant_disclosures['amount'].sum()
                avg_lobbying_amount = relevant_disclosures['amount'].mean()

                # Calculate correlation strength (simplified)
                correlation_strength = min(1.0, total_lobbying_amount / filing['total_receipts'])

                # Statistical significance
                expected_correlation = 0.1  # Baseline expectation
                if correlation_strength > expected_correlation:
                    z_score = (correlation_strength - expected_correlation) / 0.05
                    p_value = 1 - stats.norm.cdf(z_score)
                    confidence = 1 - p_value
                else:
                    z_score = 0
                    p_value = 1.0
                    confidence = 0.0

                result = {
                    'analysis_type': 'lobbying_conflicts',
                    'candidate_id': candidate_id,
                    'period_start': period_start.isoformat(),
                    'period_end': period_end.isoformat(),
                    'metric_name': 'lobbying_correlation',
                    'metric_value': correlation_strength,
                    'confidence': confidence,
                    'p_value': p_value
                }
                self.storage.store_analysis_result(**result)
                results.append(result)

        return results

    def generate_summary_report(self, candidate_id):
        """Generate comprehensive summary of all analyses"""
        all_results = self.storage.get_analysis_results(candidate_id=candidate_id)

        summary = {
            'candidate_id': candidate_id,
            'generated_at': datetime.now().isoformat(),
            'total_analyses': len(all_results),
            'analysis_types': {},
            'key_findings': []
        }

        # Group by analysis type
        for result in all_results:
            analysis_type = result[1]  # analysis_type column
            if analysis_type not in summary['analysis_types']:
                summary['analysis_types'][analysis_type] = []
            summary['analysis_types'][analysis_type].append({
                'metric_name': result[5],  # metric_name
                'metric_value': result[6],  # metric_value
                'confidence': result[7],  # confidence
                'p_value': result[8],  # p_value
                'computed_at': result[9]  # computed_at
            })

        # Identify key findings (high confidence, significant p-values)
        for result in all_results:
            confidence = result[7]
            p_value = result[8]
            if confidence > 0.8 and p_value < 0.05:
                summary['key_findings'].append({
                    'analysis_type': result[1],
                    'metric_name': result[5],
                    'metric_value': result[6],
                    'confidence': confidence,
                    'p_value': p_value
                })

        # Generate reproducibility hash
        summary_data = json.dumps(summary, sort_keys=True)
        summary['reproducibility_hash'] = hashlib.sha256(summary_data.encode()).hexdigest()

        return summary