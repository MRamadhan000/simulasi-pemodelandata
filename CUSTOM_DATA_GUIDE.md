# 📋 Panduan Input Data Custom

## Overview

Fitur **Input Data Custom** memungkinkan Anda memasukkan data transaksi dalam format text CSV sederhana tanpa perlu membuat file JSON. Fitur ini tersedia di tab **📊 Dataset** → **➕ Data Custom**.

---

## Lokasi Fitur

1. **Navigasi ke Tab Dataset**
   - Klik tab **📊 Dataset** di sidebar kiri
   - Scroll ke bawah dan klik tab **➕ Data Custom**

2. **Atau langsung di Simulasi**
   - Klik tab **🚀 Simulation**
   - Pilih sumber data: **Data Custom (dari tab Dataset)**

---

## Format Input Data

### ✅ Format Wajib (CSV Format)

Baris pertama harus berupa **header** dengan 3 kolom:

```
Transaction_ID,Interarrival_Time,Verification_Time
```

Setiap baris berikutnya berisi **1 transaksi** dengan data dipisahkan koma:

```
TXN001,2.5,3.2
TXN002,1.8,2.9
TXN003,3.1,4.5
```

---

## Penjelasan Kolom

| Kolom | Tipe | Deskripsi | Contoh | Catatan |
|-------|------|-----------|--------|---------|
| **Transaction_ID** | Text | ID unik untuk setiap transaksi | TXN001, TX_2024_1, T1 | Boleh menggunakan huruf, angka, underscore |
| **Interarrival_Time** | Angka Desimal | Waktu antar kedatangan transaksi dalam detik | 2.5, 1.8, 3.1 | Harus > 0, desimal diperbolehkan |
| **Verification_Time** | Angka Desimal | Waktu yang diperlukan untuk verifikasi dalam detik | 3.2, 2.9, 4.5 | Harus > 0, desimal diperbolehkan |

---

## Contoh Input Lengkap

### Contoh 1: Traffic Rendah (5 transaksi)

```
Transaction_ID,Interarrival_Time,Verification_Time
TXN001,5.0,3.2
TXN002,4.8,2.9
TXN003,5.2,3.5
TXN004,4.9,3.0
TXN005,5.1,3.3
```

### Contoh 2: Traffic Normal (8 transaksi)

```
Transaction_ID,Interarrival_Time,Verification_Time
TX_001,2.5,3.2
TX_002,2.3,2.8
TX_003,2.7,3.5
TX_004,2.4,3.0
TX_005,2.6,3.3
TX_006,2.5,2.9
TX_007,2.4,3.4
TX_008,2.6,3.1
```

### Contoh 3: Traffic Tinggi (10 transaksi)

```
Transaction_ID,Interarrival_Time,Verification_Time
T1,1.2,3.5
T2,1.1,3.2
T3,1.3,3.4
T4,1.2,3.1
T5,1.1,3.5
T6,1.2,3.3
T7,1.1,3.4
T8,1.3,3.2
T9,1.2,3.3
T10,1.1,3.4
```

---

## ✅ Aturan Input

### Wajib Dipenuhi

1. ✅ **Baris pertama harus header:** `Transaction_ID,Interarrival_Time,Verification_Time`
2. ✅ **Urutan kolom harus sesuai:** Transaction_ID, Interarrival_Time, Verification_Time
3. ✅ **Setiap baris = 1 transaksi** (dipisahkan Enter/NewLine)
4. ✅ **Minimal 1 transaksi** (selain header)
5. ✅ **Interarrival_Time dan Verification_Time harus angka**
   - Boleh desimal (contoh: 2.5, 3.14, 1.0)
   - Boleh tanpa desimal jika bulat (contoh: 3, 5, 2)
6. ✅ **Tidak boleh ada nilai negatif** (-1.5 ❌)
7. ✅ **Tidak boleh ada spasi di sekitar koma** (kalau ada akan dihapus otomatis)

### Catatan

- **Tidak perlu** memiliki kolom urutan/sequence (otomatis dibuat)
- **Tidak perlu** arrival_time (otomatis dihitung dari cumulative sum)
- **Transaction_ID** hanya sebagai identifier, boleh sama jika diperlukan (tapi tidak disarankan)

---

## ⚠️ Common Mistakes

| ❌ Salah | ✅ Benar | Masalah |
|---------|---------|--------|
| `TXN001, 2.5, 3.2` | `TXN001,2.5,3.2` | Ada spasi di sekitar koma |
| `TXN001,2.5,3.2,123` | `TXN001,2.5,3.2` | Terlalu banyak kolom |
| `TXN001,2.5` | `TXN001,2.5,3.2` | Kurang kolom |
| `TXN001,-2.5,3.2` | `TXN001,2.5,3.2` | Nilai negatif tidak diperbolehkan |
| `TXN001,abc,3.2` | `TXN001,2.5,3.2` | Interarrival_Time harus angka |
| Header pertama tidak ada | Header wajib ada di baris 1 | System error |

---

## Cara Menggunakan

### Step 1: Buka Tab Data Custom

![Navigation]
- Masuk ke tab **📊 Dataset**
- Klik tab **➕ Data Custom**

### Step 2: Masukkan Data

Di text area yang tersedia, masukkan data dalam format CSV:

```
Transaction_ID,Interarrival_Time,Verification_Time
TXN001,2.5,3.2
TXN002,1.8,2.9
TXN003,3.1,4.5
```

### Step 3: Klik "✅ Proses Data Custom"

Sistem akan:
- ✅ Validasi format dan nilai
- ✅ Tampilkan statistik data (Total, Avg, Min, Max)
- ✅ Tampilkan tabel transaksi
- ✅ Tampilkan distribusi histogram
- ✅ Simpan data di session

### Step 4: Gunakan di Simulasi

Buka tab **🚀 Simulation**:
- Pilih: **Data Custom (dari tab Dataset)**
- Klik: **🚀 Jalankan Simulasi**
- Sistem akan menggunakan data custom Anda

---

## Error Messages & Solutions

### ❌ "Minimal 2 baris diperlukan (1 header + 1 data)"

**Penyebab:** Hanya ada header, tidak ada data transaksi

**Solusi:** Tambahkan minimal 1 baris data di bawah header

---

### ❌ "Kolom harus: Transaction_ID, Interarrival_Time, Verification_Time"

**Penyebab:** Header tidak sesuai atau urutan kolom salah

**Solusi:** 
- Baris pertama harus persis: `Transaction_ID,Interarrival_Time,Verification_Time`
- Jangan tambah/kurangi kolom

---

### ❌ "Baris X: Harus ada 3 kolom, ditemukan Y"

**Penyebab:** Baris memiliki lebih atau kurang dari 3 kolom

**Solusi:** Pastikan setiap baris memiliki tepat 3 nilai dipisahkan koma

---

### ❌ "Baris X: Interarrival_Time dan Verification_Time harus angka"

**Penyebab:** Kolom 2 atau 3 berisi text bukan angka

**Solusi:** 
- Gunakan format angka: `2.5`, `3`, `1.8`
- Jangan gunakan format text: `2,5` (gunakan `.` untuk desimal)

---

### ❌ "Baris X: Waktu tidak boleh negatif"

**Penyebab:** Nilai time negative

**Solusi:** Gunakan nilai positif saja (> 0)

---

### ❌ "Tidak ada data ditemukan"

**Penyebab:** Semua baris data kosong atau hanya ada header

**Solusi:** Tambahkan minimal 1 baris data transaksi

---

## 📊 Statistik yang Ditampilkan

Setelah memproses data custom, sistem akan menampilkan:

### KPI Cards
- **Total Transaksi** — Jumlah baris data
- **Avg Interarrival** — Rata-rata waktu antar kedatangan
- **Avg Verif. Time** — Rata-rata waktu verifikasi
- **Total Waktu** — Total cumulative interarrival time

### Tabel Data
- Menampilkan semua transaksi Anda dalam format tabel

### Visualisasi
- **Distribusi Interarrival Time** — Histogram frekuensi
- **Distribusi Verification Time** — Histogram frekuensi

---

## 💡 Tips & Best Practices

### Untuk Traffic Rendah (Skenario Sepi)
```
- Interarrival Time: 4-6 detik
- Verification Time: 2-4 detik
- Contoh: 5.0, 4.8, 5.2
```

### Untuk Traffic Normal (Skenario Normal)
```
- Interarrival Time: 2-3 detik
- Verification Time: 2.5-3.5 detik
- Contoh: 2.5, 2.3, 2.7
```

### Untuk Traffic Tinggi (Skenario Padat)
```
- Interarrival Time: 1-1.5 detik
- Verification Time: 3-4 detik
- Contoh: 1.2, 1.1, 1.3
```

### Untuk Traffic Sangat Tinggi (Skenario Sangat Padat)
```
- Interarrival Time: 0.5-1 detik
- Verification Time: 3-5 detik
- Contoh: 0.8, 0.7, 0.9
```

---

## 🔄 Workflow Lengkap

```
1. Buka Tab Dataset → Data Custom
   ↓
2. Siapkan data dalam format CSV
   ↓
3. Copy-paste ke text area
   ↓
4. Klik "✅ Proses Data Custom"
   ↓
5. Verifikasi statistik & visualisasi
   ↓
6. Buka Tab Simulation
   ↓
7. Pilih "Data Custom (dari tab Dataset)"
   ↓
8. Atur parameter: Jumlah Server, Iterasi MC
   ↓
9. Klik "🚀 Jalankan Simulasi"
   ↓
10. Lihat hasil di tab Analytics
```

---

## 📝 Catatan Penting

1. **Data disimpan dalam session** — Jika browser ditutup, data hilang
2. **Format strict** — Sistem tidak mentolerir format yang tidak sesuai
3. **Validasi realtime** — Error ditampilkan segera saat klik "Proses"
4. **Gunakan untuk testing** — Format ini bagus untuk quick testing dengan custom scenarios
5. **Besar data** — Cocok untuk 1-1000 transaksi (lebih dari itu gunakan file JSON)

---

## 🚀 Contoh Use Case

### Use Case 1: Test Traffic Spike
```
Transaction_ID,Interarrival_Time,Verification_Time
T1,1.0,3.5
T2,0.8,3.2
T3,1.2,3.4
T4,0.9,3.3
T5,1.1,3.5
T6,0.7,3.2
T7,1.0,3.4
T8,0.8,3.3
T9,1.2,3.5
T10,0.9,3.2
```
→ Simulasikan performa saat traffic spike

### Use Case 2: Test Slow Verification
```
Transaction_ID,Interarrival_Time,Verification_Time
T1,2.5,5.5
T2,2.3,5.2
T3,2.7,5.4
T4,2.4,5.3
T5,2.6,5.5
```
→ Simulasikan performa saat verification time lambat

### Use Case 3: Test Variable Traffic
```
Transaction_ID,Interarrival_Time,Verification_Time
T1,3.0,3.0
T2,1.5,3.2
T3,0.8,3.5
T4,2.5,3.1
T5,0.9,3.3
```
→ Simulasikan traffic yang tidak konsisten/variable

---

## 📞 Troubleshooting

**Q: Bagaimana jika saya ingin gunakan lebih dari 1000 transaksi?**
A: Gunakan file JSON di folder `data/` atau split data menjadi beberapa batch

**Q: Bisa edit data setelah proses?**
A: Ya, edit di text area dan klik "Proses" lagi

**Q: Data custom bisa disimpan ke file?**
A: Belum ada fitur export, tapi Anda bisa copy-paste text area ke file txt

**Q: Berapa lama data tetap tersimpan?**
A: Selama session browser aktif. Jika tab ditutup/refresh, data hilang

---

## 📚 Related Documentation

- **Dataset Preset:** Lihat `data/README.md`
- **Simulasi:** Lihat tab **🚀 Simulation**
- **Analytics:** Lihat tab **📈 Analytics**

---

**Last Updated:** June 1, 2026
**Version:** 1.0
