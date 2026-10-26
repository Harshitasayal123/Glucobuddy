# GlucoBuddy
### Personalized Food and Blood Glucose Monitoring System

GlucoBuddy is a web-based application that integrates food image recognition, meal tracking, blood glucose recording, and glucose history visualization into a single platform. It combines a modern React interface, a Python backend, PostgreSQL storage, and machine-learning components to support food and glucose record management.

## Overview

GlucoBuddy aims to simplify the process of recording meals and blood glucose readings. Users can upload food images, select recognized food items, record meal quantities, log glucose readings with meal context, and visualize recorded readings over time.

## Key Features

- **Food Image Recognition:** Generate candidate food labels from uploaded images using OpenCLIP.
- **Meal Tracking:** Select food items and record meals with quantity information.
- **Blood Glucose Logging:** Store glucose readings with before-meal or after-meal context.
- **Glucose History Visualization:** Display recorded glucose values over time using interactive line charts.
- **Database Integration:** Store and retrieve food, meal, and glucose-related records using PostgreSQL.
- **Backend API:** Connect the frontend to backend functionality through FastAPI.
- **Data Analysis:** Includes an analysis endpoint and an experimental Random Forest model for glucose-related analysis.

## Technology Stack

| Technology | Purpose |
|---|---|
| React | Interactive frontend |
| Vite | Frontend development and build tooling |
| JavaScript and CSS | Application logic and interface styling |
| Python | Backend and machine-learning logic |
| FastAPI | Backend API |
| PostgreSQL | Relational database |
| OpenCLIP (ViT-B-32) | Food image recognition |
| Random Forest | Experimental glucose-related analysis |
| Recharts | Glucose history visualization |

## System Architecture

The application follows a frontend–backend architecture:

1. **Frontend:** React provides the dashboard, food-image upload, meal logging, glucose entry, and chart visualization.
2. **Backend:** FastAPI handles API requests, application logic, food recognition, and data retrieval.
3. **Database:** PostgreSQL stores structured application records.
4. **Machine Learning:** OpenCLIP supports food-image recognition, while the Random Forest component supports experimental glucose-related analysis.

## Machine Learning

### Food Recognition — OpenCLIP

The project uses a pretrained OpenCLIP model with the `ViT-B-32` architecture and `laion2b_s34b_b79k` weights. It compares uploaded images with candidate food labels to generate possible matches.

The model has not been fine-tuned specifically for GlucoBuddy, and its predictions may be incorrect.

### Glucose-Related Analysis — Random Forest

The project includes an experimental Random Forest model associated with the BrisT1D dataset. Its performance requires appropriate evaluation before any accuracy or clinical-performance claims can be made.

## Getting Started

### Prerequisites

- Node.js and npm
- Python
- PostgreSQL
- Git

### 1. Clone the repository

```bash
git clone YOUR_GITHUB_REPOSITORY_URL
cd GlucoBuddy
```

Replace the placeholder with your actual repository URL.

### 2. Configure and run the backend

From the project root:

```cmd
cd backend
venv\Scripts\activate
python -m uvicorn main:app --reload
```

Configure the PostgreSQL database and required environment variables locally before starting the application.

**Backend URL:** `http://127.0.0.1:8000`

**API documentation:** `http://127.0.0.1:8000/docs`

### 3. Install and run the frontend

Open a second terminal from the project root:

```cmd
cd frontend
npm install
npm run dev
```

Open the local URL provided by Vite, usually `http://localhost:5173/`.

## Current Project Status

The following core features have been implemented:

- React dashboard and user interface.
- Food-image upload and candidate recognition workflow.
- Meal recording with food selection and quantity.
- Blood glucose recording with meal context.
- PostgreSQL integration and glucose history retrieval.
- Interactive glucose history chart.
- Backend analysis endpoint and experimental machine-learning components.

The application is currently a development prototype. Authentication, comprehensive evaluation, and production deployment have not yet been established.

## Future Scope

- Improve food recognition and expand supported food labels.
- Evaluate machine-learning components using appropriate metrics.
- Enhance personalized analysis of recorded data.
- Improve user-specific data handling and input validation.
- Strengthen automated testing, security, and reliability.
- Prepare the application for deployment.

## Disclaimer

GlucoBuddy is an academic software project for food and glucose record management. It is not a clinically validated medical device and should not be used for diagnosis or treatment decisions.

## Project Information

**Project Name:** GlucoBuddy  
**Domain:** Web Development, Computer Vision, Database Management, and Machine Learning  
**Status:** Prototype under development

---

*Developed as an academic project to explore the integration of food tracking, glucose monitoring, and machine-learning-assisted analysis.*
