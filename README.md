**🏥 CodeCrux**
Federated Multi-Modal ICU Crisis Prediction System

Predicting Code Blue & Septic Shock 6 Hours in Advance

📌 Overview

CodeCrux is an ICU-focused healthcare AI platform designed to predict critical patient deterioration — including Code Blue and Septic Shock — up to 6 hours before onset.

The system integrates multiple ICU data streams into a unified prediction engine and provides early warning scores, explainable insights, risk forecasting, and interactive clinical assistance.

Developed by **Team CodeCrux.**

🎯** Problem Statement**

Modern ICUs continuously generate high-frequency medical data:

ECG / PPG waveforms

Vital signs (HR, BP, RR, SpO₂)

Medication and intervention logs

Clinical notes

This leads to cognitive overload, making early detection of deterioration difficult.

CodeCrux addresses this by delivering:

Early deterioration prediction

Clear and interpretable AI explanations

Future risk projection

Privacy-preserving learning simulation

**🚀 Key Features**
1. Multi-Modal Data Fusion

Processes waveforms, vitals, events, and notes independently

Combines all modalities into a unified prediction model

2. 6-Hour Early Warning Prediction

Risk score (0–100)

Probability of deterioration

Estimated time-to-event

3. Federated Learning Simulation

Simulated multi-hospital nodes

Local training per node

No raw data sharing

Model aggregation using FedAvg

4. Counterfactual Explanation Engine

“What-if” clinical reasoning

Identifies contributing risk factors

Simulates intervention impact

5. ICU Risk Trajectory Curve

Displays past risk

Shows current risk

Forecasts risk for the next 6 hours

6. Digital Twin Patient Simulation

Simulates future vital progression

Projects deterioration trajectory

Models potential intervention outcomes

7. ICU Voice Chatbot

Answers clinical queries

Explains rising risk

Identifies unstable parameters

Supports optional voice output

8. Concept Drift Detection

Detects sensor anomalies

Identifies data distribution shifts

Flags monitoring inconsistencies

**🧠 Architecture Summary**

CodeCrux follows a modular architecture:

1.Input Layer
Waveforms, vitals, events, clinical notes

2.Preprocessing Layer
Cleaning, normalization, temporal alignment

3.Model Layer

CNN + LSTM for waveforms

Transformer models for vitals

BERT embeddings for clinical notes

4.Fusion Layer
Combines embeddings into unified risk prediction

5.Dashboard Layer
Risk curve, digital twin, chatbot interface

6.Federated Layer
Multi-node training and aggregation

**🛠 Tech Stack**
**Backend**

FastAPI

Python

PyTorch

XGBoost

AI Models

1D CNN + LSTM

Transformer models

BERT embeddings

**Frontend**

Streamlit

Tools

Docker

Postman

**Git & GitHub**

⚙️ Setup (Prototype Stage)
git clone https://github.com/haarish-v/CodeCrux.git
cd codecrux
pip install -r requirements.txt
uvicorn api.main:app --reload

Open in browser:

http://127.0.0.1:8000
📊 Project Status

Hackathon Prototype

Core backend implemented

Dashboard integration in progress

Federated simulation under development

**👥 Team**

Team Name: CodeCrux
Healthcare AI Hackathon Project
