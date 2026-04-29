# Contributing to SCADA Digital Twin

We welcome contributions! To ensure the stability of the Alberti Steelworks SCADA environment, please follow these guidelines.

## Human Resources & Required Skills (Criterion 6k)
To effectively contribute to this project, developers should possess the following profile:
* **Technical Skills:** Proficiency in Python 3, Object-Oriented Programming (OOP), multithreading, `customtkinter` for UI, and `matplotlib` for real-time data visualization.
* **Domain Knowledge:** Basic understanding of OT/IT convergence, Industrial IoT (IIoT), and Zero-Trust network architectures.
* **Training Strategy:** New contributors should start by reviewing the auto-generated `pdoc` documentation. We recommend fixing minor UI bugs before attempting to modify the background physics engine (OT Simulator) to prevent desynchronization.

## Systems Integration & Interoperability (Criterion 6i)
Currently, the SCADA system uses in-memory RAM data exchange to ensure 30 FPS zero-latency communication between the OT engine and the IT dashboard. 

**Future Integration Goals (Pull Requests Welcome):**
1. **REST APIs:** Transitioning the RAM dictionary to a local REST API or MQTT broker to allow multiple remote IT dashboards to monitor the same OT physical engine.
2. **Cloud Platforms:** Integrating the local *Datalogger* with external SIEM platforms (like Splunk or ELK Stack) or AWS IoT Hub for historical Big Data analysis.
3. **Database Integration:** Replacing the `.txt` log outputs with a lightweight SQLite or PostgreSQL database to improve data persistence and interoperability with third-party ERPs.

## How to Submit Changes
1. Fork the repository and create your feature branch (`git checkout -b feature/AmazingFeature`).
2. Document your changes properly in the code for `pdoc` generation.
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`).
4. Push to the branch (`git push origin feature/AmazingFeature`).
5. Open a Pull Request detailing the strategic business value of your change (Criterion 6j).
