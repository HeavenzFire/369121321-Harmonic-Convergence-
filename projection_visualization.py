#!/usr/bin/env python3
"""
Projection Model Visualization for Sovereign Intelligence Ecosystem

This script generates a 30-cycle projection model comparing baseline institutional
systems vs the sovereign intelligence ecosystem, showing exponential lead growth.
"""

import matplotlib.pyplot as plt
import numpy as np
import hashlib
import json
from datetime import datetime

class ProjectionVisualizer:
    def __init__(self):
        # Initial values from the projection model
        self.baseline_initial = {
            'creation_velocity': 1000,
            'universal_nodes': 20000,
            'resilience_grade': 75,
            'symmetry_coefficient': 0.8
        }

        self.user_initial = {
            'creation_velocity': 9999,
            'universal_nodes': 1000000,
            'resilience_grade': 100,
            'symmetry_coefficient': 1.0
        }

        # Growth rates
        self.baseline_growth = 0.05  # 5% per cycle
        self.user_growth = 0.12      # 12% per cycle

        self.cycles = 30

    def calculate_eo(self, metrics):
        """Calculate Effective Output from metrics"""
        return (metrics['creation_velocity'] *
                metrics['universal_nodes'] *
                metrics['resilience_grade'] *
                metrics['symmetry_coefficient'])

    def project_growth(self, initial_metrics, growth_rate, cycles):
        """Project compounded growth over cycles"""
        projection = []
        current = initial_metrics.copy()

        for cycle in range(cycles + 1):  # Include cycle 0
            eo = self.calculate_eo(current)
            projection.append({
                'cycle': cycle,
                'metrics': current.copy(),
                'eo': eo
            })

            # Apply growth to each metric
            for key in current:
                current[key] *= (1 + growth_rate)

        return projection

    def generate_visualization(self):
        """Generate the projection visualization"""
        # Calculate projections
        baseline_proj = self.project_growth(self.baseline_initial, self.baseline_growth, self.cycles)
        user_proj = self.project_growth(self.user_initial, self.user_growth, self.cycles)

        # Extract data for plotting
        cycles = [p['cycle'] for p in baseline_proj]
        baseline_eo = [p['eo'] for p in baseline_proj]
        user_eo = [p['eo'] for p in user_proj]

        # Calculate relative advantage
        relative_advantage = [user_eo[i] / baseline_eo[i] for i in range(len(cycles))]

        # Create the plot
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))

        # Main EO comparison plot
        ax1.plot(cycles, baseline_eo, 'b-', label='Baseline Institutional System', linewidth=2)
        ax1.plot(cycles, user_eo, 'r-', label='Sovereign Intelligence Ecosystem', linewidth=2)

        ax1.set_yscale('log')
        ax1.set_xlabel('Evolution Cycles')
        ax1.set_ylabel('Effective Output (EO)')
        ax1.set_title('30-Cycle Projection: Sovereign Intelligence vs Institutional Benchmarks')
        ax1.grid(True, alpha=0.3)
        ax1.legend()

        # Add annotations for key points
        ax1.annotate('.0f',
                    xy=(0, user_eo[0]), xytext=(2, user_eo[0]*1.5),
                    arrowprops=dict(arrowstyle='->', color='red', alpha=0.7))
        ax1.annotate('.0f',
                    xy=(self.cycles, user_eo[-1]), xytext=(self.cycles-5, user_eo[-1]*0.7),
                    arrowprops=dict(arrowstyle='->', color='red', alpha=0.7))

        # Relative advantage plot
        ax2.plot(cycles, relative_advantage, 'g-', linewidth=2)
        ax2.set_yscale('log')
        ax2.set_xlabel('Evolution Cycles')
        ax2.set_ylabel('Relative Advantage (×)')
        ax2.set_title('Exponential Lead Growth: Sovereign Intelligence Advantage')
        ax2.grid(True, alpha=0.3)

        # Add final advantage annotation
        final_advantage = relative_advantage[-1]
        ax2.annotate('.0f',
                    xy=(self.cycles, final_advantage), xytext=(self.cycles-8, final_advantage*0.8),
                    arrowprops=dict(arrowstyle='->', color='green', alpha=0.7))

        plt.tight_layout()

        # Save the plot
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"projection_visualization_{timestamp}.png"
        plt.savefig(filename, dpi=300, bbox_inches='tight')
        plt.close()

        # Generate integrity hash
        with open(filename, 'rb') as f:
            file_hash = hashlib.sha256(f.read()).hexdigest()

        # Save projection data
        projection_data = {
            'timestamp': timestamp,
            'cycles': self.cycles,
            'baseline_growth_rate': self.baseline_growth,
            'user_growth_rate': self.user_growth,
            'initial_values': {
                'baseline': self.baseline_initial,
                'user': self.user_initial
            },
            'final_values': {
                'baseline': baseline_proj[-1]['metrics'],
                'user': user_proj[-1]['metrics'],
                'baseline_eo': baseline_eo[-1],
                'user_eo': user_eo[-1],
                'relative_advantage': final_advantage
            },
            'projection_data': {
                'cycles': cycles,
                'baseline_eo': baseline_eo,
                'user_eo': user_eo,
                'relative_advantage': relative_advantage
            },
            'integrity_hash': file_hash
        }

        data_filename = f"projection_data_{timestamp}.json"
        with open(data_filename, 'w') as f:
            json.dump(projection_data, f, indent=2)

        return filename, data_filename, projection_data

def main():
    """Main execution function"""
    print("🧬 Generating Sovereign Intelligence Projection Visualization...")

    visualizer = ProjectionVisualizer()
    plot_file, data_file, data = visualizer.generate_visualization()

    print("✅ Projection visualization generated successfully!")
    print(f"📊 Plot saved as: {plot_file}")
    print(f"📋 Data saved as: {data_file}")
    print(f"🔐 Integrity hash: {data['integrity_hash'][:16]}...")
    print(f"🎯 Final relative advantage: {data['final_values']['relative_advantage']:.0f}x")
    print(f"📈 Baseline EO (cycle {data['cycles']}): {data['final_values']['baseline_eo']:.2e}")
    print(f"🚀 User EO (cycle {data['cycles']}): {data['final_values']['user_eo']:.2e}")

if __name__ == "__main__":
    main()