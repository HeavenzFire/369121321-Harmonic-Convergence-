"""
Pattern Analyzer - Advanced Pattern Detection for Child Welfare Data
Detects complex patterns in case data using signal processing and machine learning
"""

import numpy as np
import pandas as pd
from scipy import signal
from sklearn.cluster import DBSCAN
from sklearn.preprocessing import StandardScaler
import warnings
warnings.filterwarnings('ignore')

class PatternAnalyzer:
    def __init__(self):
        self.scaler = StandardScaler()

    def detect_risk_patterns(self, case_data: pd.DataFrame) -> dict:
        """
        Detect complex risk patterns in case data using multiple analysis methods
        """
        results = {}

        # Extract numerical features for pattern analysis
        numerical_cols = case_data.select_dtypes(include=[np.number]).columns
        if len(numerical_cols) == 0:
            return {"error": "No numerical data available for pattern analysis"}

        features = case_data[numerical_cols].fillna(0)

        # Method 1: Signal processing - detect periodic patterns
        results['periodic_patterns'] = self._detect_periodic_patterns(features)

        # Method 2: Clustering - identify outlier groups
        results['cluster_anomalies'] = self._detect_cluster_anomalies(features)

        # Method 3: Correlation patterns - detect co-occurring risks
        results['correlation_clusters'] = self._detect_correlation_patterns(features)

        # Method 4: Trend analysis - detect escalating patterns
        results['trend_patterns'] = self._detect_trend_patterns(features)

        return results

    def _detect_periodic_patterns(self, features: pd.DataFrame) -> list:
        """Detect periodic patterns using autocorrelation"""
        patterns = []

        for col in features.columns:
            series = features[col].values
            if len(series) < 10:  # Need minimum data points
                continue

            # Compute autocorrelation
            autocorr = signal.correlate(series, series, mode='full')
            autocorr = autocorr[autocorr.size // 2:] / np.max(autocorr)

            # Find peaks in autocorrelation (indicating periodicity)
            peaks, _ = signal.find_peaks(autocorr, height=0.3, distance=5)

            if len(peaks) > 0:
                dominant_period = peaks[0] if len(peaks) > 0 else None
                patterns.append({
                    'feature': col,
                    'period': int(dominant_period),
                    'strength': float(autocorr[dominant_period]) if dominant_period < len(autocorr) else 0,
                    'type': 'periodic'
                })

        return patterns

    def _detect_cluster_anomalies(self, features: pd.DataFrame) -> list:
        """Detect anomalous clusters using DBSCAN"""
        anomalies = []

        # Scale features
        scaled_features = self.scaler.fit_transform(features)

        # Apply DBSCAN clustering
        dbscan = DBSCAN(eps=0.5, min_samples=3)
        clusters = dbscan.fit_predict(scaled_features)

        # Identify noise points (anomalies)
        noise_mask = clusters == -1
        if np.sum(noise_mask) > 0:
            anomaly_indices = np.where(noise_mask)[0]
            anomalies.extend([{
                'case_index': int(idx),
                'cluster_type': 'anomaly',
                'confidence': 0.8
            } for idx in anomaly_indices])

        return anomalies

    def _detect_correlation_patterns(self, features: pd.DataFrame) -> list:
        """Detect highly correlated feature groups"""
        correlation_matrix = features.corr()

        # Find correlation clusters (absolute correlation > 0.7)
        high_corr_pairs = []
        for i in range(len(correlation_matrix.columns)):
            for j in range(i+1, len(correlation_matrix.columns)):
                corr_val = abs(correlation_matrix.iloc[i, j])
                if corr_val > 0.7:
                    high_corr_pairs.append({
                        'features': [correlation_matrix.columns[i], correlation_matrix.columns[j]],
                        'correlation': float(corr_val),
                        'type': 'high_correlation'
                    })

        return high_corr_pairs

    def _detect_trend_patterns(self, features: pd.DataFrame) -> list:
        """Detect escalating or de-escalating trends"""
        trends = []

        for col in features.columns:
            series = features[col].values
            if len(series) < 5:  # Need minimum data points
                continue

            # Calculate trend using linear regression
            x = np.arange(len(series))
            slope, intercept = np.polyfit(x, series, 1)

            # Classify trend
            if abs(slope) > np.std(series) * 0.1:  # Significant trend
                trend_type = 'escalating' if slope > 0 else 'de-escalating'
                trends.append({
                    'feature': col,
                    'trend_type': trend_type,
                    'slope': float(slope),
                    'significance': float(abs(slope) / np.std(series))
                })

        return trends

    def analyze_case_similarity(self, case_data: pd.DataFrame, target_case: dict) -> dict:
        """
        Find cases similar to a target case for pattern matching
        """
        # Convert target case to feature vector
        target_features = pd.DataFrame([target_case])

        # Calculate similarity scores
        similarities = {}
        for idx, row in case_data.iterrows():
            # Euclidean distance
            distance = np.linalg.norm(row.values - target_features.values[0])
            similarities[int(idx)] = float(distance)

        # Sort by similarity (lower distance = more similar)
        sorted_similarities = sorted(similarities.items(), key=lambda x: x[1])

        return {
            'most_similar_cases': sorted_similarities[:5],
            'similarity_method': 'euclidean_distance'
        }