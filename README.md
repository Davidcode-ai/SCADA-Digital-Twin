# 🏭 SCADA Digital Twin: Real-Time IT/OT Integration

![Status](https://img.shields.io/badge/Status-Active-brightgreen) ![License](https://img.shields.io/badge/License-MIT-blue) ![Language](https://img.shields.io/badge/Language-Python-yellow)

## 📌 Motivation
In the context of Industry 4.0, bridging the gap between Operational Technology (OT) and Information Technology (IT) is crucial. "Alberti Steelworks" faced critical downtime due to unmonitored furnace temperature spikes and motor failures. 

This Open Source SCADA Digital Twin was created to solve this issue. By simulating real-time physical constraints and providing a secure IT dashboard, operators can now monitor telemetry, detect anomalies, and trigger automatic safety lockdowns, thereby preventing catastrophic equipment failures and optimizing the production lifecycle.

## 🚀 Deployment Instructions

### Local Installation
1. Clone the repository: 
   `git clone https://github.com/TU_USUARIO/TU_REPOSITORIO.git`
2. Navigate to the folder: 
   `cd TU_REPOSITORIO`
3. Install the required dependencies: 
   `pip install -r requirements.txt`
4. Run the application: 
   `python panel_fabrica_pro.py`

## 💡 Examples of Use
1. **Normal Operation:** Launch the app, accept the safety guidelines, and click "HORNO DE FUNDICIÓN". Turn on the "Válvula Principal". The system will maintain a nominal temperature automatically.
2. **Stress Test & Auto-Lockdown:** In the "MOTOR" view, click the red switch "Fuga de Aceite". The IT dashboard will detect the sudden heat spike. The background will turn red (DANGER), and the system will automatically lock the interface to simulate a safe shutdown procedure.
3. **Data Logging:** Check the "Registro de Sucesos" (Datalogger) at the bottom of the main map to audit the exact timestamp when the failure occurred.

## 📚 Documentation
You can find the full code documentation generated automatically here: [SCADA Digital Twin Docs](https://scada-digital-twin.vercel.app/)
