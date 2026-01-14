#!/usr/bin/env python3
"""
Internet Efficiency Measurement Harness
Measures DNS, HTTP, and QUIC performance to quantify optimization gains
"""

import time
import subprocess
import sys
import statistics
from typing import Dict, List

class EfficiencyMeasurer:
    def __init__(self, domain: str = "example.com", iterations: int = 3):
        self.domain = domain
        self.iterations = iterations
        self.results = {}

    def measure_dns(self) -> Dict:
        """Measure DNS lookup performance"""
        times = []
        for i in range(self.iterations):
            start = time.time()
            try:
                result = subprocess.run(
                    ['dig', '+stats', '+noall', '+answer', self.domain],
                    capture_output=True, text=True, timeout=10
                )
                dns_time = time.time() - start
                times.append(dns_time)
            except Exception as e:
                print(f"DNS measurement {i+1} failed: {e}")
                times.append(float('inf'))

        return {
            'avg_time': statistics.mean([t for t in times if t != float('inf')]) if times else float('inf'),
            'min_time': min([t for t in times if t != float('inf')]) if times else float('inf'),
            'max_time': max([t for t in times if t != float('inf')]) if times else float('inf'),
            'success_rate': len([t for t in times if t != float('inf')]) / len(times)
        }

    def measure_http(self) -> Dict:
        """Measure HTTP/2 performance"""
        times = []
        for i in range(self.iterations):
            start = time.time()
            try:
                result = subprocess.run(
                    ['curl', '-o', '/dev/null', '-s', '-w', '%{time_total}', f'https://{self.domain}'],
                    capture_output=True, text=True, timeout=15
                )
                if result.returncode == 0:
                    total_time = float(result.stdout.strip())
                    times.append(total_time)
                else:
                    times.append(float('inf'))
            except Exception as e:
                print(f"HTTP measurement {i+1} failed: {e}")
                times.append(float('inf'))

        return {
            'avg_time': statistics.mean([t for t in times if t != float('inf')]) if times else float('inf'),
            'min_time': min([t for t in times if t != float('inf')]) if times else float('inf'),
            'max_time': max([t for t in times if t != float('inf')]) if times else float('inf'),
            'success_rate': len([t for t in times if t != float('inf')]) / len(times)
        }

    def measure_quic(self) -> Dict:
        """Measure HTTP/3 (QUIC) performance if supported"""
        times = []
        for i in range(self.iterations):
            start = time.time()
            try:
                result = subprocess.run(
                    ['curl', '--http3', '-o', '/dev/null', '-s', '-w', '%{time_total}', f'https://{self.domain}'],
                    capture_output=True, text=True, timeout=15
                )
                if result.returncode == 0:
                    total_time = float(result.stdout.strip())
                    times.append(total_time)
                else:
                    times.append(float('inf'))
            except Exception as e:
                print(f"QUIC measurement {i+1} failed (HTTP/3 not supported): {e}")
                times.append(float('inf'))

        return {
            'avg_time': statistics.mean([t for t in times if t != float('inf')]) if times else float('inf'),
            'min_time': min([t for t in times if t != float('inf')]) if times else float('inf'),
            'max_time': max([t for t in times if t != float('inf')]) if times else float('inf'),
            'success_rate': len([t for t in times if t != float('inf')]) / len(times)
        }

    def run_measurements(self) -> Dict:
        """Run all measurements and calculate efficiency gains"""
        print(f"🔬 Measuring internet efficiency for {self.domain} ({self.iterations} iterations each)")

        self.results['dns'] = self.measure_dns()
        self.results['http'] = self.measure_http()
        self.results['quic'] = self.measure_quic()

        return self.results

    def print_report(self):
        """Print formatted measurement report"""
        print("\n" + "="*60)
        print("🌐 INTERNET EFFICIENCY MEASUREMENT REPORT")
        print("="*60)
        print(f"Domain: {self.domain}")
        print(f"Iterations: {self.iterations}")
        print()

        for protocol, data in self.results.items():
            print(f"📊 {protocol.upper()} Performance:")
            if data['avg_time'] != float('inf'):
                print(".3f"                print(".3f"                print(".3f"                print(".1%"            else:
                print("  ❌ No successful measurements")
            print()

        # Calculate potential gains
        if self.results['http']['avg_time'] != float('inf') and self.results['quic']['avg_time'] != float('inf'):
            http_time = self.results['http']['avg_time']
            quic_time = self.results['quic']['avg_time']
            if quic_time < http_time:
                gain = ((http_time - quic_time) / http_time) * 100
                print(".1f"        print("\n💡 Recommendations:")
        print("  • Deploy QUIC + ECH for 15-45% faster page loads")
        print("  • Enable FQ_CODEL to reduce bufferbloat by 60-95%")
        print("  • Use Brotli compression for 40-75% payload reduction")
        print("  • Implement predictive prefetch for 40-80% FCP reduction")

if __name__ == '__main__':
    domain = sys.argv[1] if len(sys.argv) > 1 else 'example.com'
    iterations = int(sys.argv[2]) if len(sys.argv) > 2 else 3

    measurer = EfficiencyMeasurer(domain, iterations)
    measurer.run_measurements()
    measurer.print_report()