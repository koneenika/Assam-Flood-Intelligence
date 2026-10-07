# Assam Flood Intelligence

**Live Dashboard:** https://assam-flood-intelligence.vercel.app/

A district-level geospatial flood intelligence dashboard for Assam, combining satellite-derived flood extent, rainfall, terrain, land cover, and infrastructure exposure into an interactive decision-support interface.

---

## Overview

**Assam Flood Intelligence** is a geospatial flood assessment project developed to analyze the July 2026 flood event across selected districts of Assam.

The project combines remote sensing, GIS, geospatial analysis, and interactive web visualization to answer three core questions:

- **Where did flooding occur?**
- **How severe was the impact across districts?**
- **What infrastructure, land cover, rainfall, and terrain factors were associated with the affected areas?**

The resulting dashboard transforms the analysis into an interactive district-level flood intelligence platform.

---

## Live Webpage

🌐 **https://assam-flood-intelligence.vercel.app/**

The dashboard allows users to explore the analyzed districts, compare flood extent, inspect district-level impacts, and examine rainfall, terrain, land-cover, infrastructure, and river information.

---

## Key Features

### 🗺️ Assam Flood Overview

- Interactive Assam flood map
- District-level flood extent visualization
- Visual classification of lower and higher flood extent
- District selection and exploration

### 📍 District-Level Flood Intelligence

Each analyzed district includes:

- Total flooded area
- Flood extent percentage
- Flooded cropland
- Flooded forest
- Buildings affected
- Roads affected
- Flood impact classification
- District flood map
- Spatial layers for buildings and roads
- Rainfall analysis
- Terrain information
- Land-cover information
- Risk indicators
- Explanation of major flood factors

### 🌧️ Rainfall Analysis

The project incorporates rainfall information to examine:

- Daily rainfall
- Flood-period rainfall
- Maximum daily rainfall
- Rainfall patterns across analyzed districts

### 🛰️ Satellite-Derived Flood Mapping

Flood extent was derived using satellite remote sensing, with Sentinel-1 SAR used for flood-water detection.

The workflow is designed to work in cloud-based geospatial analysis environments and produce district-level flood statistics and spatial outputs.

### 🏘️ Infrastructure Exposure

The project evaluates flood exposure of:

- Buildings
- Roads
- Agricultural areas
- Forest / tree-cover areas

Spatial outputs are generated for individual districts and integrated into the dashboard.

## Analyzed Districts

The current dashboard analyzes **9 districts**:

1. Biswanath
2. Charaideo
3. Darrang
4. Golaghat
5. Hojai
6. Jorhat
7. Nagaon
8. Sivasagar
9. Sonitpur

---

## Methodology

The project follows a multi-stage geospatial workflow.

```text
Satellite & Geospatial Data
          │
          ▼
   Flood Detection
          │
          ▼
 District-Level Analysis
          │
    ┌─────┼──────────┐
    ▼     ▼          ▼
 Rainfall Terrain  Land Cover
    │     │          │
    └─────┼──────────┘
          ▼
 Infrastructure Exposure
          │
          ▼
   Flood Intelligence
          │
          ▼
 Interactive Live Dashboard
