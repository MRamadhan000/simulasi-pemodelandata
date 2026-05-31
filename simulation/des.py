"""
Discrete Event Simulation (DES) Engine
untuk Verifikasi Pembayaran Digital

ATURAN TRANSISI SISTEM (System Transition Rules):
================================================

1. STATE TRANSITIONS:
   Waiting → Verifying: Transaksi berpindah ke state Verifying ketika ada server tersedia
   Verifying → Completed: Transaksi selesai setelah durasi verifikasi berakhir

2. PERSAMAAN MATEMATIS:
   a) Start_i = max(Arrival_i, AvailableServer_j)
   b) End_i = Start_i + VT_i
   c) Waiting_i = Start_i - Arrival_i
   d) Queue_Length_At_Arrival_i = jumlah transaksi j (j < i) dimana End_Time_j > Arrival_Time_i

3. SERVER ALLOCATION: Earliest Available Server (FCFS)
"""

import numpy as np
import pandas as pd
from collections import deque


class VerificationServer:
    """Class untuk menyimpan status server verifikasi"""
    def __init__(self):
        self.available_until = 0.0
        self.busy = False


class DESSimulation:
    """
    Discrete Event Simulation Engine untuk Verifikasi Pembayaran Digital
    
    Mengimplementasikan:
    - Start_i = max(Arrival_i, AvailableServer_j)
    - End_i = Start_i + VT_i
    - Waiting_i = Start_i - Arrival_i
    - Queue Length Dynamics
    - Earliest Available Server allocation
    """
    
    def __init__(self, num_servers=4):
        self.num_servers = num_servers
        self.servers = [VerificationServer() for _ in range(num_servers)]
        self.queue = deque()
        self.results = []
        self.queue_length_history = []
        self.current_time = 0.0
        
    def run_simulation(self, dataset):
        """
        Run DES untuk dataset yang diberikan
        
        Parameters:
        - dataset: DataFrame dengan kolom Transaction_ID, Interarrival_Time, Verification_Time
        
        Returns:
        - DataFrame dengan hasil simulasi
        """
        # Reset state
        self.servers = [VerificationServer() for _ in range(self.num_servers)]
        self.queue = deque()
        self.results = []
        self.queue_length_history = []
        self.current_time = 0.0
        
        # Calculate Arrival Time
        dataset = dataset.copy()
        dataset['Arrival_Time'] = dataset['Interarrival_Time'].cumsum() - dataset['Interarrival_Time'].iloc[0]
        dataset['Arrival_Time'] = dataset['Arrival_Time'].shift(fill_value=0)
        
        # PASS 1: Calculate Start_Time dan End_Time untuk semua transaksi
        for idx, row in dataset.iterrows():
            transaction_id = row['Transaction_ID']
            arrival_time = row['Arrival_Time']
            verification_time = row['Verification_Time']
            
            # Cari server yang tersedia paling cepat
            available_server_idx = self._find_available_server()
            available_server_time = self.servers[available_server_idx].available_until
            
            # Calculate Start Time dan End Time
            start_time = max(arrival_time, available_server_time)
            end_time = start_time + verification_time
            waiting_time = start_time - arrival_time
            
            # Update server status
            self.servers[available_server_idx].available_until = end_time
            
            # Simpan hasil
            self.results.append({
                'Transaction_ID': transaction_id,
                'Arrival_Time': arrival_time,
                'Start_Time': start_time,
                'End_Time': end_time,
                'Verification_Time': verification_time,
                'Waiting_Time': waiting_time,
                'Server_ID': available_server_idx + 1,
                'Queue_Length_At_Arrival': 0  # Will be updated in pass 2
            })
        
        # PASS 2: Calculate Queue_Length_At_Arrival
        for i, result_i in enumerate(self.results):
            queue_length = 0
            arrival_time_i = result_i['Arrival_Time']
            
            for j in range(i):
                end_time_j = self.results[j]['End_Time']
                if end_time_j > arrival_time_i:
                    queue_length += 1
            
            result_i['Queue_Length_At_Arrival'] = queue_length
            
            self.queue_length_history.append({
                'Time': arrival_time_i,
                'Event': 'Arrival',
                'Queue_Length': queue_length
            })
        
        results_df = pd.DataFrame(self.results)
        return results_df
    
    def _find_available_server(self):
        """Cari index server yang tersedia paling cepat (earliest available server)"""
        min_available_time = float('inf')
        best_server_idx = 0
        
        for i, server in enumerate(self.servers):
            if server.available_until < min_available_time:
                min_available_time = server.available_until
                best_server_idx = i
                
        return best_server_idx


def get_server_timeline(results_df, num_servers=4):
    """
    Generate timeline data untuk setiap server
    Digunakan untuk animasi real-time di dashboard
    
    Returns:
    - list of events sorted by time
    """
    events = []
    
    for _, row in results_df.iterrows():
        events.append({
            'time': row['Start_Time'],
            'type': 'start',
            'transaction_id': row['Transaction_ID'],
            'server_id': int(row['Server_ID']),
            'end_time': row['End_Time']
        })
        events.append({
            'time': row['End_Time'],
            'type': 'end',
            'transaction_id': row['Transaction_ID'],
            'server_id': int(row['Server_ID']),
        })
    
    events.sort(key=lambda x: (x['time'], 0 if x['type'] == 'end' else 1))
    return events


def get_server_state_at_time(results_df, t, num_servers=4):
    """
    Dapatkan state server dan antrian pada waktu t
    
    Returns:
    - dict dengan server status dan queue
    """
    server_status = {}
    for s in range(1, num_servers + 1):
        server_status[s] = {'status': 'Idle', 'transaction': None}
    
    queue = []
    
    for _, row in results_df.iterrows():
        tx_id = row['Transaction_ID']
        arrival = row['Arrival_Time']
        start = row['Start_Time']
        end = row['End_Time']
        server_id = int(row['Server_ID'])
        
        if arrival <= t < start:
            # Transaksi sudah tiba tapi belum mulai diproses (menunggu)
            queue.append(tx_id)
        elif start <= t < end:
            # Transaksi sedang diproses di server
            server_status[server_id] = {
                'status': 'Busy',
                'transaction': tx_id,
                'progress': (t - start) / (end - start) * 100
            }
    
    return server_status, queue
