# Dataset untuk Simulasi DES + Monte Carlo

Direktori ini berisi dataset untuk simulasi verifikasi pembayaran digital dengan Discrete Event Simulation (DES) dan Monte Carlo.

## File Dataset

### 1. **sepi_dataset.json**
- **Skenario:** Sepi (Low Traffic)
- **Transaksi:** 20 per iterasi
- **Rata-rata Interarrival Time:** 5.0 detik
- **Karakteristik:** 1 transaksi setiap 5 detik, server banyak menganggur
- **Use Case:** Traffic ringan, baseline performance

### 2. **normal_dataset.json**
- **Skenario:** Normal (Medium Traffic)
- **Transaksi:** 40 per iterasi
- **Rata-rata Interarrival Time:** 2.5 detik
- **Karakteristik:** 2 transaksi setiap 5 detik, utilisasi server normal
- **Use Case:** Traffic normal, expected usage

### 3. **padat_dataset.json**
- **Skenario:** Padat (High Traffic)
- **Transaksi:** 80 per iterasi
- **Rata-rata Interarrival Time:** 1.25 detik
- **Karakteristik:** 4 transaksi setiap 5 detik, sistem mulai congested
- **Use Case:** Traffic tinggi, peak hours

### 4. **sangat_padat_dataset.json**
- **Skenario:** Sangat Padat (Very High Traffic)
- **Transaksi:** 160 per iterasi
- **Rata-rata Interarrival Time:** 0.625 detik
- **Karakteristik:** 8 transaksi setiap 5 detik, sistem stress
- **Use Case:** Traffic sangat tinggi, stress testing

## Struktur JSON

Setiap file JSON memiliki struktur sebagai berikut:

```json
{
  "scenario": "sepi",
  "scenario_name": "Sepi",
  "description": "1 transaksi per 5 detik",
  "metadata": {
    "num_transactions": 20,
    "avg_interarrival_time": 5.0,
    "characteristics": {
      "density": "Low",
      "transactions_per_5sec": 1,
      "server_load": "Light - Banyak server menganggur"
    },
    "verification_time_distribution": {
      "type": "Uniform",
      "min": 2.0,
      "max": 6.0,
      "unit": "seconds"
    },
    "interarrival_time_distribution": {
      "type": "Normal",
      "mean": 5.0,
      "std_dev": 1.5,
      "minimum": 0.1,
      "unit": "seconds"
    }
  },
  "transactions": [
    {
      "transaction_id": "T1",
      "sequence": 1,
      "interarrival_time": 5.0234,
      "arrival_time": 0.0,
      "verification_time": 4.2156
    },
    ...
  ],
  "statistics": {
    "total_transactions": 20,
    "avg_interarrival": 4.9876,
    "min_interarrival": 0.1234,
    "max_interarrival": 7.5432,
    "avg_verification_time": 4.0123,
    "min_verification_time": 2.0456,
    "max_verification_time": 5.9876,
    "total_simulation_time": 95.2345
  }
}
```

## Field Penjelasan

### Root Level
- `scenario`: Kunci scenario (sepi, normal, padat, sangat_padat)
- `scenario_name`: Nama scenario yang readable
- `description`: Deskripsi singkat skenario
- `metadata`: Informasi tentang dataset
- `transactions`: Array berisi semua transaksi
- `statistics`: Statistik agregat dataset

### Metadata
- `num_transactions`: Total jumlah transaksi
- `avg_interarrival_time`: Rata-rata jarak antar kedatangan transaksi
- `characteristics`: Deskripsi karakteristik beban
- `verification_time_distribution`: Spesifikasi distribusi waktu verifikasi
- `interarrival_time_distribution`: Spesifikasi distribusi waktu kedatangan

### Transaction Fields
- `transaction_id`: ID unik transaksi (T1, T2, ...)
- `sequence`: Nomor urut transaksi
- `interarrival_time`: Jarak waktu dari transaksi sebelumnya (detik)
- `arrival_time`: Waktu kedatangan absolut dari awal simulasi (detik)
- `verification_time`: Waktu yang diperlukan untuk verifikasi (detik)

### Statistics
- `total_transactions`: Total transaksi dalam dataset
- `avg_interarrival`: Rata-rata interarrival time
- `min_interarrival`: Interarrival time minimum
- `max_interarrival`: Interarrival time maksimum
- `avg_verification_time`: Rata-rata waktu verifikasi
- `min_verification_time`: Waktu verifikasi minimum
- `max_verification_time`: Waktu verifikasi maksimum
- `total_simulation_time`: Total waktu simulasi sampai transaksi terakhir tiba

## Penggunaan

### Load Dataset dari JSON

```python
import json

# Load dataset untuk skenario Sepi
with open('data/sepi_dataset.json', 'r') as f:
    sepi_data = json.load(f)

# Akses informasi
scenario_name = sepi_data['scenario_name']
transactions = sepi_data['transactions']
stats = sepi_data['statistics']

# Convert ke DataFrame untuk simulasi
import pandas as pd
df = pd.DataFrame([
    {
        'Transaction_ID': tx['transaction_id'],
        'Interarrival_Time': tx['interarrival_time'],
        'Verification_Time': tx['verification_time']
    }
    for tx in transactions
])
```

## Karakteristik Dataset

### Distribusi Interarrival Time
- **Type:** Normal Distribution
- **Mean:** Sesuai spesifikasi skenario (5.0, 2.5, 1.25, 0.625)
- **Std Dev:** 30% dari mean
- **Minimum:** 0.1 detik (hard minimum)

### Distribusi Verification Time
- **Type:** Uniform Distribution
- **Range:** [2.0, 6.0] detik
- **Alasan:** Mencerminkan variabilitas waktu verifikasi di dunia nyata
  - Network delay
  - Server load
  - Payment gateway latency

## Reproducibility

Semua dataset di-generate dengan seed yang konsisten (seed=42) untuk memastikan:
- **Reproducibility:** Dataset dapat di-recreate dengan hasil yang sama
- **Consistency:** Simulasi menghasilkan output yang konsisten
- **Validation:** Memudahkan debugging dan validasi

## Notes

1. **Verification Time Random:** Dalam Monte Carlo simulation, verification time akan di-generate ulang secara acak setiap iterasi (tetap dalam range 2-6 detik)

2. **Interarrival Time Fixed:** Dalam simulasi, interarrival time dari dataset ini digunakan sebagaimana adanya (tidak di-randomize ulang)

3. **Arrival Time Calculated:** Arrival time dihitung dari cumulative sum interarrival times

4. **Total Simulation Time:** Bukan durasi eksekusi simulasi, tetapi waktu virtual total sampai transaksi terakhir tiba

---

Generated: May 31, 2026
Simulation Framework: Discrete Event Simulation (DES) + Monte Carlo
