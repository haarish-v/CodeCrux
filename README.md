    # ATRIVA: Aegis-Omni ICU Telemetry Dashboard 🫀🤖

    A state-of-the-art, multi-modal, federated AI critical care prognosis dashboard. Built for the Codecrux hackathon.

    **ATRIVA** acts as an omniscient digital twin for ICU patients. It ingests high-frequency electrocardiograms (ECG) and continuous vitals, runs them through a live PyTorch Neural Network, calculates Code Blue risk scores in real-time, and generates professional, actionable clinical notes via an embedded Large Language Model.

    ![ATRIVA Dashboard](C:/Users/haari/.gemini/antigravity/brain/5fabebf2-6291-4536-861f-f6eaf2db5098/critical_patient_verification_1772223710233.png)

    ---

    ## 🚀 Key Features

    ### 1. Multi-Modal AI Fusion Pipeline (PyTorch)
    - **ECGNet:** 1D-CNN + BiLSTM architecture extracting 256-D features from high-frequency MIT-BIH Arrhythmia waveforms.
    - **VitalsGRU:** A Recurrent Neural Network projecting real-time BIDMC vitals (HR, SpO2, MAP, RESP) into a 64-D embedding.
    - **Late Fusion:** Concatenates tensors into a fully connected layer to output an extremely accurate real-time **Code Blue Risk Score**.
    - **Federated Capable:** Structurally designed for Federated Averaging (FedAvg) across detached medical nodes without centralizing PII.

    ### 2. Live Cyberpunk Telemetry Dashboard (React)
    - **Real-Time Data Streams:** High-performance HTML Canvas (via Chart.js) acts as an oscilloscope for 360Hz live ECG tracking.
    - **3D Digital Twin:** A dynamic CSS-animated anatomical heart that scales and changes color (Cyan to Red) natively tied to the PyTorch risk score.
    - **Responsive Design:** 3-column layout seamlessly handles widescreen hospital displays while natively scaling to vertically-stacked mobile/tablet WebView formats.

    ### 3. Native Database EHR Integration (MySQL)
    - Reads patient records dynamically from the `atriva_db` SQL database.
    - Hot-swaps demographic info, active medications arrays, and historical medical files seamlessly via the `Stream Source` selector.

    ### 4. Featherless AI LLM Clinical Synthesis
    - Uses the uncensored `NousResearch/Meta-Llama-3-8B-Instruct` model (via Featherless AI) to act as a Virtual Attending Physician.
    - The backend parses PyTorch telemetry numbers and pushes them to the LLM, synthesizing professional, readable clinical notes on-demand.
    - **Native Text-To-Speech (TTS):** A 🔊 READ button utilizes `window.speechSynthesis` to read the LLM's assessment aloud for zero-latency auditory monitoring.

    ---

    ## 🛠️ Architecture Stack

    - **Backend:** Python + FastAPI + Uvicorn + Websockets
    - **AI/ML:** PyTorch + Scikit-Learn + WFDB (PhysioNet Extractors) + Pandas
    - **LLM Engine:** OpenAI Python SDK hitting `api.featherless.ai`
    - **Frontend:** React + Vite + Vanilla CSS
    - **Database:** MySQL Server (via `pymysql` & `sqlalchemy`)

    ---

    ## ⚙️ Installation & Setup

    You will need two separate terminal windows multiplexed (one for Python FastAPI backend, one for React frontend).

    ### Prerequisites
    - Python 3.10+
    - Node.js & npm
    - Local MySQL Server (`root` / no password, running on `localhost:3306`)

    ### 1. Setup the Backend Engine

    ```bash
    cd backend
    python -m venv venv
    # Activate virtual environment
    # Windows:
    .\venv\Scripts\activate
    # Mac/Linux:
    source venv/bin/activate

    # Install requirements
    pip install fastapi uvicorn websockets pydantic openai pymysql sqlalchemy torch torchvision torchaudio wfdb pandas numpy scikit-learn

    # Initialize the Database
    python init_db.py

    # Boot the API Server
    python -m uvicorn main:app --host 0.0.0.0 --port 8000
    ```
    *(Note: `--host 0.0.0.0` ensures the server is accessible on LAN for Mobile APK debugging)*

    ### 2. Setup the Frontend Dashboard

    ```bash
    cd frontend
    npm install
    # Start Vite Development Server
    npm run dev -- --host
    ```

    ### 3. Open in Browser
    Navigate to `http://localhost:5173`. Select different patients from the **STREAM SOURCE** dropdown at the top to watch the AI engine recalculate risks and animate the UI.

    ---

    ## 📱 Mobile APK Note
    This repository natively supports Android wrappers (via Android Studio WebViews). 
    The React frontend dynamically identifies the LAN host using `window.location.hostname`, ensuring full Android connectivity to the Uvicorn web sockets running correctly on mobile devices without any cross-origin blocks.

    ---

    ## 🔒 License & Disclaimer
    This is a prototype hackathon project built for conceptual demonstration purposes. **Not for actual medical diagnosis.** The AI models are trained on limited samples of generalized MIT-BIH sets and should not be used in live critical-care pathways without rigorous FDA clinical trials.
