# Phase 2: Utility and Application Analysis (Use Case: Alberti Steelworks S.A.)

**Criterion 6a) Strategic Objectives:**
The software addresses the company's main strategic objective: **"Reduction of operational costs due to downtime and integral improvement of occupational safety"**. By simulating a real-time SCADA environment, it aligns with the digital transformation strategy, allowing the company to move from purely reactive maintenance (repairing broken machinery) to active control that prevents thermal collapses through automatic lockdowns.

**Criterion 6b) Business and Communications Areas:**
The **Production (Plant/OT)** area directly benefits from an intuitive, real-time visualization of motor and furnace statuses. Concurrently, the **Management and Quality (IT)** area can audit the system using the integrated *Datalogger*. The operational impact is drastic: manual analog readings are eliminated, and the system automatically interrupts production when facing imminent danger, protecting the assets.

**Criterion 6c) Areas Susceptible to Digitalization:**
The critical area chosen is **Heavy Machinery Monitoring (Smelting Furnaces and Main Motors)**. It is highly susceptible to digitalization because, historically, the collection of physical variables (temperature, pressure, load) depended on human inspection. With the Digital Twin, data collection is automated, eliminating human error and allowing for millisecond reaction times.

**Criterion 6d) Alignment of Digitalized Areas (AD):**
The IT control panel (digitalized area) constantly interacts with the plant mechanics (non-digitalized physical area). When the software detects a severe anomaly (e.g., temperature > 1200ºC), it locks the interface and logs the event. The proposal to cohesive these areas is to use this *Datalogger* to issue "Work Tickets" that are automatically printed in the physical workshop, linking the digital alert with the manual repair.

**Criterion 6e) Present and Future Needs:**
* **Present:** Solves the critical need to visualize complex physical data in a simple dashboard for the human operator, preventing breakdowns due to overload.
* **Future:** The system is prepared to scale towards future needs, such as integration with AI models for predictive maintenance and Big Data storage in the cloud (AWS/Azure).

**Criterion 6f) Relationship with Technologies:**
Key enabling technologies such as **Digital Twins (In-memory simulation)** and **Real-Time Data Processing (Python/Matplotlib)** have been used. The direct benefit of this implementation is the ability to inject faults (stress tests) into a virtualized environment without putting million-euro physical equipment at risk, streamlining business decision-making.

**Criterion 6g) Security Breaches:**
When joining OT (factory) networks with IT (control panel) networks, the main breach is a Denial of Service (DoS) attack or malicious data injection that falsifies graphs, preventing safety systems from triggering.
* **Mitigation:** A *Zero-Trust* architecture is proposed, isolating sensor networks in dedicated VLANs, disabling USB ports on terminals, and using encryption for telemetry, ensuring the panel only reads data from authenticated sources.

**Criterion 6h) Data Treatment and Analysis:**
The system manages generated telemetry by simulating real sensors, capturing data at a rate of 30 frames per second in shared memory. To guarantee the quality and consistency of the analysis, raw data is cross-referenced in real-time against static safety thresholds ("Hard Limits"). Critical events are archived with immutable timestamps, allowing for consistent post-incident audits.
