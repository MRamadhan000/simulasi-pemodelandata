"""
Monte Carlo Simulation Framework
untuk DES Verification System

Menjalankan DES berulang kali dengan verification time yang di-randomize
setiap iterasi untuk menangkap ketidakpastian sistem.

- Distribusi: Verification Time ~ Uniform(2, 6) detik
- Default: 1000 iterasi per skenario
"""

import numpy as np
import pandas as pd
from .des import DESSimulation


class MonteCarloSimulation:
    """Monte Carlo Simulation untuk DES Verification System"""
    
    def __init__(self, num_iterations=1000, num_servers=4):
        self.num_iterations = num_iterations
        self.num_servers = num_servers
        self.iteration_results = []
        
    def run_monte_carlo(self, dataset, vt_min=2, vt_max=6, progress_callback=None):
        """
        Run Monte Carlo simulation
        
        Parameters:
        - dataset: Base dataset dengan struktur (Transaction_ID, Interarrival_Time)
        - vt_min, vt_max: Range untuk random verification time
        - progress_callback: Optional callback(iteration, total) for progress updates
        
        Returns:
        - list of iteration results (dicts)
        """
        self.iteration_results = []
        
        for iteration in range(self.num_iterations):
            # Generate random verification times untuk iterasi ini
            dataset_with_vt = dataset.copy()
            dataset_with_vt['Verification_Time'] = np.random.uniform(vt_min, vt_max, len(dataset))
            
            # Run DES
            des = DESSimulation(num_servers=self.num_servers)
            results = des.run_simulation(dataset_with_vt)
            
            # Calculate metrics for this iteration
            iteration_metrics = {
                'Iteration': iteration + 1,
                'Avg_Waiting_Time': results['Waiting_Time'].mean(),
                'Max_Waiting_Time': results['Waiting_Time'].max(),
                'Min_Waiting_Time': results['Waiting_Time'].min(),
                'Std_Waiting_Time': results['Waiting_Time'].std(),
                'Avg_Verification_Time': results['Verification_Time'].mean(),
                'Total_Completion_Time': results['End_Time'].max(),
                'Num_Transactions': len(results),
                'Avg_Queue_Length': results['Queue_Length_At_Arrival'].mean(),
                'Max_Queue_Length': results['Queue_Length_At_Arrival'].max(),
                'Results_DF': results
            }
            
            # Calculate server utilization
            total_service_time = results['Verification_Time'].sum()
            total_time_span = results['End_Time'].max()
            utilization = (total_service_time / (self.num_servers * total_time_span)) * 100 if total_time_span > 0 else 0
            iteration_metrics['Server_Utilization'] = utilization
            
            self.iteration_results.append(iteration_metrics)
            
            if progress_callback and (iteration + 1) % max(1, self.num_iterations // 20) == 0:
                progress_callback(iteration + 1, self.num_iterations)
        
        return self.iteration_results
    
    def get_aggregated_metrics(self):
        """Aggregate metrics dari semua iterasi"""
        metrics_df = pd.DataFrame([
            {k: v for k, v in r.items() if k != 'Results_DF'}
            for r in self.iteration_results
        ])
        
        aggregated = {
            'Avg_Waiting_Time': metrics_df['Avg_Waiting_Time'].mean(),
            'Std_Waiting_Time': metrics_df['Avg_Waiting_Time'].std(),
            'Min_Waiting_Time': metrics_df['Avg_Waiting_Time'].min(),
            'Max_Waiting_Time': metrics_df['Max_Waiting_Time'].mean(),
            'Avg_Queue_Length': metrics_df['Avg_Queue_Length'].mean(),
            'Max_Queue_Length': metrics_df['Max_Queue_Length'].max(),
            'Avg_Server_Utilization': metrics_df['Server_Utilization'].mean(),
            'Avg_Completion_Time': metrics_df['Total_Completion_Time'].mean(),
            'Std_Completion_Time': metrics_df['Total_Completion_Time'].std(),
            'P95_Waiting_Time': metrics_df['Avg_Waiting_Time'].quantile(0.95),
            'P99_Waiting_Time': metrics_df['Avg_Waiting_Time'].quantile(0.99),
            'Median_Waiting_Time': metrics_df['Avg_Waiting_Time'].median(),
        }
        
        return aggregated, metrics_df
