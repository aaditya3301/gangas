# 🌊 Aqua Guardians - Ganga River Climate Monitoring System
**Riverathon 1.0 - National Level Hackathon**

## 🎯 Project Overview
A comprehensive ecosystem monitoring system combining LiDAR, IoT sensors, and satellite data for real-time climate impact assessment and flood risk management along the Ganga River basin (Hapur District).

---

## 🏆 Innovation Highlights
- **Multi-sensor Fusion**: Combines LiDAR DEM + Satellite Imagery + Simulated IoT data
- **Real-time Decision Support**: Interactive flood inundation modeling
- **Community Engagement**: Citizen science integration (planned)
- **Digital Twin Approach**: 3D terrain visualization with climate overlays

---

## 📊 Dataset Information
- **Source**: Survey of India LiDAR Data (Riverathon 1.0)
- **Coverage**: Hapur District, Uttar Pradesh
- **Volume**: ~50 MB (optimized subset from 60GB total)
- **Resolution**: Sub-meter precision DEM + High-res orthophotos

---

## 🛠️ Tech Stack

### Data Processing
- **Python 3.10+**: Core language
- **Rasterio/GDAL**: Geospatial raster processing
- **GeoPandas**: Vector data handling
- **WhiteboxTools**: Advanced terrain analysis

### Visualization
- **Plotly**: 3D terrain visualization
- **Folium**: Interactive web maps
- **Streamlit**: Dashboard framework

### Analysis
- **NumPy/SciPy**: Numerical computations
- **scikit-learn**: Land cover classification

---

## 🚀 Quick Start

### 1. Setup Environment
```bash
# Create virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

# Install dependencies
pip install -r requirements.txt
```

### 2. Download Data
Follow instructions in `DATA_DOWNLOAD_GUIDE.md` to download LiDAR files.

### 3. Run Basic Flood Model
```bash
python flood_model.py
```

### 4. Launch Interactive Dashboard
```bash
streamlit run dashboard/app.py
```

---

## 📁 Project Structure
```
RIVERATHON/
├── data/
│   ├── raw/              # Original LiDAR data (DEM + ORTHO)
│   └── processed/        # Generated analysis outputs
├── src/
│   ├── data_loader.py       # Data I/O utilities
│   ├── flood_analysis.py    # Flood modeling functions
│   ├── terrain_analysis.py  # Slope, aspect, hillshade
│   └── visualization.py     # Plotting utilities
├── dashboard/
│   └── app.py               # Streamlit web app
├── outputs/
│   ├── maps/                # Generated visualizations
│   └── reports/             # Statistics & analysis
├── flood_model.py           # Legacy 3D flood simulator
└── requirements.txt
```

---

## 🎬 Features

### ✅ Implemented
- [x] 3D terrain visualization with satellite texture
- [x] Basic flood inundation simulation
- [x] DEM-based elevation analysis

### 🚧 In Progress
- [ ] Multi-level flood risk zones
- [ ] Vegetation index (NDVI) from ORTHO images
- [ ] Interactive Streamlit dashboard
- [ ] Statistical reporting

### 🎯 Planned
- [ ] Change detection (temporal analysis)
- [ ] Infrastructure risk assessment
- [ ] Mock IoT sensor integration

---

## 📈 Key Metrics (Preliminary)
- **Analysis Area**: ~4 km² (expandable)
- **DEM Resolution**: 1-meter precision
- **Flood Scenarios**: 5-20 water level simulations
- **Processing Time**: <2 minutes on standard laptop

---

## 👥 Team: Aqua Guardians
- **Puneet** - Team Lead
- **Aaditya** - Data Science
- **Aayush** - Visualization & Frontend

---

## 🏅 Hackathon Alignment

### Problem Statement
**Climate and Environmental Monitoring**

### Judging Criteria Coverage
1. **Innovativeness** ⭐⭐⭐⭐⭐
   - First to use LiDAR for real-time flood depth calculation
   - Multi-sensor fusion approach

2. **Technical Implementation** ⭐⭐⭐⭐
   - Working Python prototype
   - Uses industry-standard libraries (GDAL, Rasterio)

3. **Impact** ⭐⭐⭐⭐⭐
   - Identifies high-risk zones for flood management
   - Scalable to entire Ganga basin

4. **Sustainability** ⭐⭐⭐⭐
   - Uses open-source tools (no licensing costs)
   - Low computational requirements

5. **Presentation** ⭐⭐⭐⭐
   - Interactive 3D demos
   - Clear visualizations

---

## 🔗 References
- [Riverathon Official Site](https://amity.edu/riverathon1.0/)
- [Survey of India LiDAR Info](https://surveyofindia.gov.in/)
- [NMCG - National Mission for Clean Ganga](https://nmcg.nic.in/)

---

## 📄 License
Educational project for Riverathon 1.0 Hackathon
