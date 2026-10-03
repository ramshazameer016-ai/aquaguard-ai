# AquaGuard AI — Simulated / Demo Data Notice

## CRITICAL NOTICE

All datasets, environmental sensor readings, and citizen reports contained or referenced within this directory are **STRICTLY SIMULATED FOR DEVELOPMENT AND DEMONSTRATION PURPOSES**.

They **MUST NEVER** be presented, cited, or interpreted as real-world sensor measurements, confirmed water quality metrics, or actual pollution events.

---

### Architectural Principles Regarding Simulated Data

1. **Explicit Identification**:
   - Every environmental observation and evidence record stored in AquaGuard AI database models includes a mandatory `is_simulated` boolean flag.
   - For all demo and synthetic data, `is_simulated` is set to `true`.

2. **No False Ground Truth**:
   - AquaGuard AI never invents real-world sensor measurements.
   - Simulated data provides context for testing database spatial queries and evidence aggregation workflows without falsely claiming authority.

3. **User Interface Transparency**:
   - In all current and future interfaces, data marked `is_simulated=true` must be visibly badged:
     ```text
     [ DEMO / SIMULATED DATA ]
     ```
     distinct from:
     ```text
     [ VERIFIED REAL DATA ]
     ```

4. **Environmental Context vs. Causation**:
   - Environmental factors (rainfall, temperature, dissolved oxygen) provide context; they do not automatically establish pollution causation.
