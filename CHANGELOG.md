# Changelog

## [Unreleased]

### ✨ Added - Custom Data Insert Feature

#### New Features
- **Custom Data Input Tab** in Dataset page (`➕ Data Custom`)
  - Simple CSV text format input (no JSON required)
  - 3 required columns: Transaction_ID, Interarrival_Time, Verification_Time
  - Real-time validation with helpful error messages

#### New Components (app.py)
- `parse_custom_data_text()` function - Parse & validate CSV text input
  - Validates format, column count, data types, value ranges
  - Returns DataFrame on success or error message on failure
  
- Dataset Tab - New Tab: `➕ Data Custom`
  - Input instructions with column descriptions
  - Format example & usage rules
  - Text area for data input
  - "✅ Proses Data Custom" button
  - Display KPI cards (Total, Avg Interarrival, Avg Verification, Total Time)
  - Display data table with row numbers
  - Display histograms for Interarrival & Verification time distributions
  - Session state persistence for simulation usage

- Simulation Tab - Enhancement
  - Radio button to select data source (Skenario Preset / Data Custom)
  - Conditional selectbox (show only for Skenario Preset)
  - Status display (show transaksi count for Data Custom)
  - Error handling if Data Custom not available

#### Input Validation Rules
- Minimal 2 baris (1 header + 1 data)
- Header must be exactly: `Transaction_ID,Interarrival_Time,Verification_Time`
- Each row must have exactly 3 columns
- Interarrival_Time & Verification_Time must be numeric (float or int)
- No negative values allowed
- Automatic whitespace trimming

#### Error Messages
- "Minimal 2 baris diperlukan (1 header + 1 data)"
- "Kolom harus: Transaction_ID, Interarrival_Time, Verification_Time"
- "Baris X: Harus ada 3 kolom, ditemukan Y"
- "Baris X: Interarrival_Time dan Verification_Time harus angka"
- "Baris X: Waktu tidak boleh negatif"
- "Tidak ada data ditemukan"

#### Session State
- `st.session_state.custom_df` - Stores DataFrame for simulation usage
- Persists during browser session
- Cleared on page reload/tab close

#### Analytics Tab - Enhancement
- Support for scenario=None (from Data Custom)
- Display "Data Custom" instead of scenario label when None

#### Documentation
- `CUSTOM_DATA_GUIDE.md` - Comprehensive user guide
  - Format specifications
  - Column descriptions
  - Example inputs for different traffic scenarios
  - Error troubleshooting
  - Tips & best practices
  - Use case examples
  - Full workflow walkthrough

- `FEATURE_SUMMARY.md` - Technical overview
  - Feature summary
  - Quick start guide
  - Validation rules
  - Data flow diagram
  - Technical details
  - Future enhancements

### 🔧 Modified Files

#### `app.py`
- Added `parse_custom_data_text()` function (~65 lines)
- Modified Dataset page tab from 2 to 3 tabs (~130 lines added)
- Added custom data input UI (~180 lines)
- Modified Simulation page data source selection (~40 lines)
- Modified Simulation execution to support Data Custom (~20 lines)
- Fixed Analytics page to handle None scenario (~5 lines)
- Total: ~440 lines added/modified

### 📝 New Files
- `CUSTOM_DATA_GUIDE.md` - User documentation
- `FEATURE_SUMMARY.md` - Technical summary
- `CHANGELOG.md` - This file

### ✅ Testing
- Python syntax validation: ✅ Pass
- Parsing function unit tests: ✅ Pass (5 test cases)
  - Valid multi-row input
  - Missing header detection
  - Wrong column count detection
  - Negative value detection
  - Non-numeric value detection

### 🎯 Backwards Compatibility
- ✅ All existing features remain unchanged
- ✅ Existing dataset functionality intact
- ✅ Existing simulation functionality intact
- ✅ Existing analytics functionality intact
- ✅ New feature is additive only

### 📊 Code Quality
- Clean CSV parsing with proper error handling
- Consistent styling with existing codebase
- KPI cards styled identically to existing cards
- Proper session state management
- Clear validation messages for users
- Input sanitization (whitespace trimming)

### 🚀 Performance
- No impact on existing features
- Parsing is lightweight (<100ms for typical inputs)
- DataFrame operations are efficient
- Histogram generation uses existing Plotly utilities

---

## Usage Examples

### Quick Start
```
1. Dataset → ➕ Data Custom
2. Input CSV:
   Transaction_ID,Interarrival_Time,Verification_Time
   TXN001,2.5,3.2
   TXN002,1.8,2.9
3. Click "✅ Proses Data Custom"
4. Simulation → Data Custom (dari tab Dataset)
5. Run simulation
```

### Supported Scenarios
- Low traffic (5-10s interarrival)
- Normal traffic (2-3s interarrival)
- High traffic (1-1.5s interarrival)
- Variable traffic (mixed intervals)
- Custom/test scenarios

---

## Migration Notes

No migration needed. Feature is fully backward compatible.

---

## Known Limitations

1. Data storage is session-based (cleared on browser reload)
2. No direct export to JSON (can copy-paste text)
3. Maximum practical size: ~1000 rows (for UI responsiveness)
4. Verification time is used as-is (not randomized during MC like presets)

---

## Future Enhancements

- [ ] Export custom data to JSON file
- [ ] Load from CSV file upload
- [ ] Edit data in table format (inline editing)
- [ ] Duplicate scenarios
- [ ] Comparison tool for multiple datasets
- [ ] Batch upload
- [ ] Randomization options for custom data

---

**Date:** June 1, 2026
**Version:** 1.0
**Status:** Complete & Tested
