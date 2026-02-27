**🏥 CodeCrux: Federated Multi-Modal ICU Crisis Prediction System**

Predicting Code Blue & Septic Shock 6 Hours in Advance

**📌 OVERVIEW**

• CodeCrux is an ICU-focused healthcare AI platform designed to predict critical patient deterioration.

• Predicts events like Code Blue and Septic Shock up to 6 hours before onset.

• Integrates multiple ICU data streams into a unified prediction engine.

• Developed by Team CodeCrux.

**🎯 PROBLEM STATEMENT**

Modern ICUs generate high-frequency data (ECG, Vitals, Notes), leading to cognitive overload. 

CodeCrux addresses this by delivering:

• Early deterioration prediction.

• Clear and interpretable AI explanations.

• Future risk projection and trajectory modeling.

• Privacy-preserving learning simulations.

**🚀 KEY FEATURES**

• **Multi-Modal Data Fusion**: Processes waveforms, vitals, events, and notes independently.

• **6-Hour Early Warning**: Risk score (0–100), probability metrics, and time-to-event estimates.

• **Federated Learning Simulation**: Simulated multi-hospital nodes using FedAvg for data privacy.

• **Counterfactual Explanation Engine**: "What-if" reasoning to identify contributing risk factors.

• **ICU Risk Trajectory Curve**: Displays past, current, and 6-hour forecasted risk.

• **Digital Twin Patient Simulation**: Projects vital progression and intervention outcomes.

• **ICU Voice Chatbot**: Answers clinical queries and explains unstable parameters.

• **Concept Drift Detection**: Flags sensor anomalies and data distribution shifts.

**🧠 ARCHITECTURE SUMMARY**

1. **Input Layer**: Waveforms, vitals, events, and clinical notes.
2. **Preprocessing Layer**: Cleaning, normalization, and temporal alignment.
3. **Model Layer**: 
   - CNN + LSTM (Waveforms)
   - Transformers (Vitals)
   - BERT Embeddings (Notes)
4. **Fusion Layer**: Combines embeddings into a unified risk prediction.
5. **Dashboard Layer**: Risk curve, digital twin, and chatbot interface.
6. **Federated Layer**: Multi-node training and aggregation.

**🛠 TECH STACK**

• **Backend**: FastAPI, Python, PyTorch, XGBoost.

• **AI Models**: 1D CNN, LSTM, Transformers, BERT.

• **Frontend**: Streamlit.

• **Tools**: Docker, Postman, Git & GitHub.

**⚙️ SETUP (PROTOTYPE STAGE)**
1. git clone https://github.com/haarish-v/CodeCrux.git
2. cd codecrux
3. pip install -r requirements.txt
4. uvicorn api.main:app --reload
5. Open: http://127.0.0.1:8000

**📊 PROJECT STATUS**

• Hackathon Prototype.

• Core backend fully implemented.

• Dashboard integration currently in progress.

• Federated simulation under development.

👥 TEAM
• Team Name: CodeCrux

• **Project**: Aurelion Hackathon (2026)

• **Team Members**:

1. Haarish

2. Elaine Jose

3.  Denila Jeslena

4.  Nitharshana



