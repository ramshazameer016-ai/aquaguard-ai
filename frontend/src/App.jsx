import { useEffect, useState } from "react";
import "./App.css";

const API_BASE_URL = "http://127.0.0.1:8001";

const DASHBOARD_REFRESH_INTERVAL = 30000;
const AI_REQUEST_TIMEOUT = 15000;

// =========================================================
// Inline SVG Icons (Clean, crisp, zero external dependencies)
// =========================================================

const ICONS = {
  drop: <path d="M12 3s6 6.3 6 10.5A6 6 0 0 1 6 13.5C6 9.3 12 3 12 3z" />,
  pin: (
    <>
      <path d="M12 21s-7-6.2-7-11a7 7 0 1 1 14 0c0 4.8-7 11-7 11z" />
      <circle cx="12" cy="10" r="2.5" />
    </>
  ),
  compass: (
    <>
      <circle cx="12" cy="12" r="9" />
      <path d="M15.5 8.5l-2 5-5 2 2-5z" />
    </>
  ),
  tag: (
    <>
      <path d="M3 12V4h8l10 10-8 8z" />
      <circle cx="7.5" cy="8.5" r="1.2" />
    </>
  ),
  file: (
    <>
      <path d="M6 3h8l4 4v14H6z" />
      <path d="M14 3v4h4M9 12h6M9 16h6" />
    </>
  ),
  calendar: (
    <>
      <rect x="4" y="5" width="16" height="15" rx="2" />
      <path d="M4 10h16M9 3v4M15 3v4" />
    </>
  ),
  image: (
    <>
      <rect x="3" y="4" width="18" height="16" rx="2" />
      <circle cx="9" cy="10" r="1.6" />
      <path d="M4 18l5-5 4 4 3-3 4 4" />
    </>
  ),
  send: <path d="M21 3L10 14M21 3l-7 18-4-7-7-4z" />,
  shield: (
    <>
      <path d="M12 3l8 3v6c0 5-3.5 8-8 9-4.5-1-8-4-8-9V6z" />
      <path d="M8.5 12l2.5 2.5 4.5-5" />
    </>
  ),
  brain: (
    <>
      <path d="M9 4a3 3 0 0 0-3 3 3 3 0 0 0-2 5 3 3 0 0 0 2 5 3 3 0 0 0 6 1V4a3 3 0 0 0-3 0z" />
      <path d="M15 4a3 3 0 0 1 3 3 3 3 0 0 1 2 5 3 3 0 0 1-2 5 3 3 0 0 1-6 1" />
    </>
  ),
  bulb: (
    <>
      <path d="M9 18h6M10 21h4" />
      <path d="M12 3a6 6 0 0 0-3.5 10.9c.7.6 1 1.3 1 2.1h5c0-.8.3-1.5 1-2.1A6 6 0 0 0 12 3z" />
    </>
  ),
  check: (
    <>
      <circle cx="12" cy="12" r="9" />
      <path d="M8 12.5l2.7 2.7L16 9.5" />
    </>
  ),
  alert: (
    <>
      <path d="M12 3l10 18H2z" />
      <path d="M12 10v5M12 18v.5" />
    </>
  ),
  info: (
    <>
      <circle cx="12" cy="12" r="9" />
      <path d="M12 11v5M12 8v.5" />
    </>
  ),
  chart: <path d="M5 20V10M12 20V4M19 20v-7" />,
  cloud: <path d="M7 18a4 4 0 0 1-.5-8A6 6 0 0 1 18 11a3.5 3.5 0 0 1-.5 7z" />,
  chevron: <path d="M9 6l6 6-6 6" />,
  leaf: <path d="M5 19C5 10 10 5 20 4c0 10-5 15-13 15zM5 19l8-8" />,
};

function Icon({ name, size = 18 }) {
  return (
    <svg
      viewBox="0 0 24 24"
      width={size}
      height={size}
      fill="none"
      stroke="currentColor"
      strokeWidth="1.8"
      strokeLinecap="round"
      strokeLinejoin="round"
      aria-hidden="true"
    >
      {ICONS[name] || ICONS.drop}
    </svg>
  );
}

function Logo() {
  return (
    <svg
      className="logo-mark"
      viewBox="0 0 64 64"
      width="46"
      height="46"
      aria-hidden="true"
    >
      <defs>
        <linearGradient id="agDrop" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stopColor="#7fe3da" />
          <stop offset="100%" stopColor="#0ea59a" />
        </linearGradient>
      </defs>
      <path
        d="M32 4s14 15 14 26a14 14 0 0 1-28 0C18 19 32 4 32 4z"
        fill="url(#agDrop)"
      />
      <path
        d="M6 44c8-6 14 4 22-1s14 3 30-3c-4 12-14 20-26 20S10 58 6 44z"
        fill="#2cc4b7"
        opacity="0.9"
      />
      <path
        d="M10 50c8-4 14 3 22-1s14 2 22-2"
        stroke="#e9fffd"
        strokeWidth="2"
        fill="none"
        strokeLinecap="round"
        opacity="0.8"
      />
    </svg>
  );
}

function evidenceIconName(type) {
  const t = String(type || "").toLowerCase();
  if (t.includes("weather")) return "cloud";
  if (t.includes("season")) return "calendar";
  if (t.includes("histor") || t.includes("pattern")) return "chart";
  if (t.includes("location") || t.includes("proximity")) return "pin";
  if (t.includes("image") || t.includes("visual")) return "image";
  return "drop";
}

function bandClass(band) {
  const b = String(band || "").toLowerCase();
  if (b.includes("low")) return "low";
  if (b.includes("high")) return "high";
  if (b.includes("med") || b.includes("moder")) return "medium";
  return "neutral";
}

function App() {
  const [formData, setFormData] = useState({
    latitude: "",
    longitude: "",
    category: "water_discoloration",
    description: "",
    observed_at: "",
    image_path: "",
  });

  const [message, setMessage] = useState("");
  const [error, setError] = useState("");
  const [submitting, setSubmitting] = useState(false);

  const [reportId, setReportId] = useState(null);
  const [explanation, setExplanation] = useState(null);
  const [explanationError, setExplanationError] = useState("");
  const [loadingExplanation, setLoadingExplanation] = useState(false);

  const [dashboard, setDashboard] = useState(null);
  const [dashboardError, setDashboardError] = useState("");
  const [loadingDashboard, setLoadingDashboard] = useState(false);

  const [selectedEventId, setSelectedEventId] = useState(null);

  const [verificationHistory, setVerificationHistory] = useState(null);
  const [verificationError, setVerificationError] = useState("");
  const [loadingVerificationHistory, setLoadingVerificationHistory] =
    useState(false);

  const [verifierId, setVerifierId] = useState("reviewer_demo");
  const [verificationNotes, setVerificationNotes] = useState("");
  const [verificationBasis, setVerificationBasis] =
    useState("field_inspection");
  const [verificationMessage, setVerificationMessage] = useState("");
  const [verificationAction, setVerificationAction] = useState("");

  const [riskOutlook, setRiskOutlook] = useState(null);
  const [riskHistory, setRiskHistory] = useState([]);
  const [riskOutlookError, setRiskOutlookError] = useState("");
  const [loadingRiskOutlook, setLoadingRiskOutlook] = useState(false);

  const [recommendedActions, setRecommendedActions] = useState([]);
  const [recommendedActionsError, setRecommendedActionsError] = useState("");
  const [loadingRecommendedActions, setLoadingRecommendedActions] =
    useState(false);

  // =========================================================
  // Form Handling
  // =========================================================

  const handleChange = (event) => {
    const { name, value } = event.target;
    setFormData((previous) => ({
      ...previous,
      [name]: value,
    }));
  };

  // =========================================================
  // AI Evidence Assessment
  // =========================================================

  const loadExplanation = async (id, eventId = null) => {
    if (!id) {
      console.error("AquaGuard AI: no report ID supplied to loadExplanation.");
      setExplanationError("No report ID was returned by the server.");
      setLoadingExplanation(false);
      return;
    }

    setExplanationError("");
    setLoadingExplanation(true);
    setExplanation(null);

    const controller = new AbortController();
    const timeoutId = window.setTimeout(() => {
      controller.abort();
    }, AI_REQUEST_TIMEOUT);

    try {
      let explanationUrl = `${API_BASE_URL}/api/ai/explanation/report/${id}`;
      if (eventId) {
        explanationUrl += `?event_id=${encodeURIComponent(eventId)}`;
      }

      console.log(
        `AquaGuard AI: loading explanation for report ${id}, event ${
          eventId ?? "not supplied"
        }`
      );

      const response = await fetch(explanationUrl, {
        method: "GET",
        signal: controller.signal,
      });

      const responseText = await response.text();
      let data;
      try {
        data = JSON.parse(responseText);
      } catch {
        throw new Error(
          `AI assessment returned an invalid response. HTTP ${response.status}.`
        );
      }

      if (!response.ok) {
        throw new Error(data.detail || "Failed to load AI assessment.");
      }

      if (!data.assessment) {
        throw new Error("AI assessment response was missing assessment data.");
      }

      console.log("AquaGuard AI explanation received:", data);

      if (data.stored_evidence_score) {
        console.log(
          "AquaGuard AI: Evidence Confidence stored for event:",
          data.stored_evidence_score
        );
      } else if (eventId) {
        console.warn(
          "AquaGuard AI: explanation succeeded, but no stored evidence score was returned."
        );
      }

      setExplanation(data);
    } catch (err) {
      if (err.name === "AbortError") {
        setExplanationError(
          "The AI assessment request timed out. Please try again."
        );
      } else {
        console.error("AquaGuard AI explanation error:", err);
        setExplanationError(err.message || "Failed to load AI assessment.");
      }
      setExplanation(null);
    } finally {
      window.clearTimeout(timeoutId);
      setLoadingExplanation(false);
    }
  };

  // =========================================================
  // Authority Dashboard
  // =========================================================

  const loadDashboard = async () => {
    setDashboardError("");
    setLoadingDashboard(true);

    try {
      console.log("AquaGuard AI: refreshing dashboard...");
      const response = await fetch(`${API_BASE_URL}/api/dashboard/summary`, {
        method: "GET",
        cache: "no-store",
      });

      const data = await response.json();
      if (!response.ok) {
        throw new Error(data.detail || "Failed to load dashboard.");
      }

      console.log("AquaGuard AI: dashboard refreshed:", data);
      setDashboard(data);
    } catch (err) {
      console.error("Dashboard loading error:", err);
      setDashboardError(err.message || "Failed to load dashboard.");
    } finally {
      setLoadingDashboard(false);
    }
  };

  useEffect(() => {
    loadDashboard();
    const intervalId = window.setInterval(() => {
      loadDashboard();
    }, DASHBOARD_REFRESH_INTERVAL);

    return () => {
      window.clearInterval(intervalId);
    };
  }, []);

  // =========================================================
  // Risk Outlook
  // =========================================================

  const loadRiskOutlook = async (eventId) => {
    if (!eventId) return;

    setRiskOutlookError("");
    setLoadingRiskOutlook(true);
    setRiskOutlook(null);
    setRiskHistory([]);

    try {
      const outlookResponse = await fetch(
        `${API_BASE_URL}/api/events/${eventId}/risk-outlook`
      );
      const outlookData = await outlookResponse.json();

      if (!outlookResponse.ok) {
        throw new Error(outlookData.detail || "Failed to load risk outlook.");
      }
      setRiskOutlook(outlookData);

      const historyResponse = await fetch(
        `${API_BASE_URL}/api/events/${eventId}/risk-outlook/history`
      );
      const historyData = await historyResponse.json();

      if (!historyResponse.ok) {
        throw new Error(
          historyData.detail || "Failed to load risk outlook history."
        );
      }
      setRiskHistory(Array.isArray(historyData) ? historyData : []);
    } catch (err) {
      console.error("Risk outlook loading error:", err);
      setRiskOutlookError(err.message || "Failed to load risk outlook.");
      setRiskOutlook(null);
      setRiskHistory([]);
    } finally {
      setLoadingRiskOutlook(false);
    }
  };

  // =========================================================
  // Recommended Actions
  // =========================================================

  const loadRecommendedActions = async (eventId) => {
    if (!eventId) return;

    setRecommendedActionsError("");
    setLoadingRecommendedActions(true);
    setRecommendedActions([]);

    try {
      const response = await fetch(
        `${API_BASE_URL}/api/events/${eventId}/recommended-actions`
      );
      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || "Failed to load recommended actions.");
      }
      const actions = Array.isArray(data) ? data : data.actions || [];
      setRecommendedActions(actions);
    } catch (err) {
      console.error("Recommended actions loading error:", err);
      setRecommendedActionsError(
        err.message || "Failed to load recommended actions."
      );
      setRecommendedActions([]);
    } finally {
      setLoadingRecommendedActions(false);
    }
  };

  // =========================================================
  // Selected Event Data
  // =========================================================

  const loadSelectedEventData = async (eventId) => {
    if (!eventId) return;

    setSelectedEventId(eventId);
    setVerificationError("");
    setVerificationHistory(null);
    setVerificationMessage("");
    setRiskOutlookError("");
    setRiskOutlook(null);
    setRiskHistory([]);
    setRecommendedActionsError("");
    setRecommendedActions([]);
    setLoadingVerificationHistory(true);

    try {
      const response = await fetch(
        `${API_BASE_URL}/api/events/${eventId}/verification-history`
      );
      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || "Failed to load verification history.");
      }
      setVerificationHistory(data);
    } catch (err) {
      console.error("Verification history loading error:", err);
      setVerificationError(
        err.message || "Failed to load verification history."
      );
    } finally {
      setLoadingVerificationHistory(false);
    }

    await Promise.all([
      loadRiskOutlook(eventId),
      loadRecommendedActions(eventId),
    ]);
  };

  // =========================================================
  // Human Verification
  // =========================================================

  const submitVerification = async (action) => {
    if (!selectedEventId) {
      setVerificationError("Please select an event first.");
      return;
    }

    setVerificationError("");
    setVerificationMessage("");
    setVerificationAction(action);

    try {
      const body = {
        verifier_id: verifierId,
        action,
        notes: verificationNotes || null,
        verification_basis: action === "confirm" ? verificationBasis : null,
      };

      const response = await fetch(
        `${API_BASE_URL}/api/events/${selectedEventId}/verify`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify(body),
        }
      );

      const data = await response.json();
      if (!response.ok) {
        throw new Error(data.detail || "Verification action failed.");
      }

      setVerificationMessage(
        `Action "${action}" completed. Event status changed from "${data.previous_status}" to "${data.new_status}".`
      );
      setVerificationNotes("");

      await loadSelectedEventData(selectedEventId);
      await loadDashboard();
    } catch (err) {
      console.error("Verification action error:", err);
      setVerificationError(err.message || "Verification action failed.");
    } finally {
      setVerificationAction("");
    }
  };

  // =========================================================
  // Citizen Report Submission
  // =========================================================

  const handleSubmit = async (event) => {
    event.preventDefault();

    setMessage("");
    setError("");
    setExplanation(null);
    setExplanationError("");
    setLoadingExplanation(false);
    setReportId(null);
    setSelectedEventId(null);
    setVerificationHistory(null);
    setRiskOutlook(null);
    setRiskHistory([]);
    setRecommendedActions([]);
    setSubmitting(true);

    try {
      const response = await fetch(`${API_BASE_URL}/api/reports`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          ...formData,
          latitude: Number(formData.latitude),
          longitude: Number(formData.longitude),
        }),
      });

      const responseText = await response.text();
      let data;
      try {
        data = JSON.parse(responseText);
      } catch {
        throw new Error(
          `Report submission returned an invalid response. HTTP ${response.status}.`
        );
      }

      if (!response.ok) {
        throw new Error(data.detail || "Failed to submit report.");
      }

      console.log("AquaGuard AI report submission response:", data);

      const newReportId =
        data.report_id ?? data.id ?? data.report?.report_id ?? data.report?.id;
      const newEventId = data.event_id ?? data.event?.id;

      if (!newReportId) {
        throw new Error(
          "Report was submitted, but the server response did not contain a usable report ID."
        );
      }

      if (!newEventId) {
        throw new Error(
          "Report was submitted, but the server response did not contain a usable event ID."
        );
      }

      setMessage(`Report #${newReportId} registered. Linked to Anomaly Event #${newEventId}.`);
      setReportId(newReportId);
      setSelectedEventId(newEventId);

      setFormData({
        latitude: "",
        longitude: "",
        category: "water_discoloration",
        description: "",
        observed_at: "",
        image_path: "",
      });

      await loadExplanation(newReportId, newEventId);
      await loadDashboard();
      await loadSelectedEventData(newEventId);
    } catch (err) {
      console.error("AquaGuard AI report submission error:", err);
      setError(err.message || "Failed to submit report.");
      setLoadingExplanation(false);
    } finally {
      setSubmitting(false);
    }
  };

  // =========================================================
  // Formatting Helpers
  // =========================================================

  const formatEvidenceName = (name) => {
    if (!name || typeof name !== "string") {
      return "Unknown Evidence";
    }
    return name
      .replaceAll("_", " ")
      .replace(/\b\w/g, (char) => char.toUpperCase());
  };

  const formatActionName = (name) => {
    if (!name || typeof name !== "string") {
      return "Unknown Action";
    }
    return name
      .replaceAll("_", " ")
      .replace(/\b\w/g, (char) => char.toUpperCase());
  };

  // =========================================================
  // Selected Event Computations
  // =========================================================

  const selectedEvent = dashboard?.recent_events?.find(
    (event) => event.id === selectedEventId
  );

  const currentVerificationStatus =
    verificationHistory?.current_status || selectedEvent?.status || null;

  const canOpen =
    currentVerificationStatus === "potential" ||
    currentVerificationStatus === "monitor" ||
    currentVerificationStatus === "caution" ||
    currentVerificationStatus === "investigation_recommended";

  const canRequestTesting = currentVerificationStatus === "under_review";

  const canConfirm =
    currentVerificationStatus === "under_review" ||
    currentVerificationStatus === "testing_requested";

  // =========================================================
  // Render Output
  // =========================================================

  return (
    <div className="app">
      {/* =====================================================
          EXECUTIVE HERO HEADER
      ====================================================== */}
      <header className="header">
        <div className="header-inner">
          <div className="brand-section">
            <div className="brand">
              <div className="logo-wrapper">
                <Logo />
              </div>
              <div className="brand-text">
                <h1>
                  Aqua<strong>Guard</strong> <em>AI</em>
                </h1>
                <div className="header-status-pill">
                  <span className="pulse-dot"></span>
                  Explainable Evidence Fusion Active
                </div>
              </div>
            </div>
          </div>

          <div className="header-tagline-box">
            <p className="header-tagline">
              See it. Understand it. <strong>Verify it.</strong> Act on it.
            </p>
            <div className="hackathon-chip">One Health Command</div>
          </div>
        </div>
      </header>

      {/* =====================================================
          TWO-COLUMN COMMAND CENTER CONTAINER
      ====================================================== */}
      <main className="container">
        <div className="command-deck-grid">
          {/* =================================================
              LEFT COLUMN: Citizen Ingestion & AI Evidence
          ================================================== */}
          <div className="deck-column">
            {/* Mission Statement Banner */}
            <div className="intro-banner">
              <div className="intro-content">
                <div className="intro-icon">
                  <Icon name="drop" size={22} />
                </div>
                <div className="intro-text">
                  <h2>Citizen Water Observation</h2>
                  <p>
                    Submit real-time water conditions. Evidence items are fused
                    with contextual metrics to prioritize human investigation.
                  </p>
                </div>
              </div>
            </div>

            {/* Citizen Submission Form Card */}
            <div className="glass-card">
              <div className="card-header-bar">
                <div className="card-title-group">
                  <div className="card-badge-icon">
                    <Icon name="file" size={18} />
                  </div>
                  <div>
                    <h3>Observation Terminal</h3>
                    <div className="card-subtitle">
                      Record location & environmental anomalies
                    </div>
                  </div>
                </div>
              </div>

              <form className="report-form" onSubmit={handleSubmit}>
                <div className="form-stack">
                  <div className="form-row-duo">
                    <div className="form-field">
                      <label htmlFor="latitude">
                        <span className="label-title">
                          <Icon name="pin" size={14} /> Latitude
                        </span>
                      </label>
                      <div className="input-container">
                        <span className="input-icon-slot">
                          <Icon name="pin" size={16} />
                        </span>
                        <input
                          id="latitude"
                          name="latitude"
                          type="number"
                          step="any"
                          value={formData.latitude}
                          onChange={handleChange}
                          placeholder="e.g. 17.3850"
                          required
                        />
                      </div>
                    </div>

                    <div className="form-field">
                      <label htmlFor="longitude">
                        <span className="label-title">
                          <Icon name="compass" size={14} /> Longitude
                        </span>
                      </label>
                      <div className="input-container">
                        <span className="input-icon-slot">
                          <Icon name="compass" size={16} />
                        </span>
                        <input
                          id="longitude"
                          name="longitude"
                          type="number"
                          step="any"
                          value={formData.longitude}
                          onChange={handleChange}
                          placeholder="e.g. 78.4867"
                          required
                        />
                      </div>
                    </div>
                  </div>

                  <div className="form-field">
                    <label htmlFor="category">
                      <span className="label-title">
                        <Icon name="tag" size={14} /> Observation Category
                      </span>
                    </label>
                    <div className="input-container">
                      <span className="input-icon-slot">
                        <Icon name="drop" size={16} />
                      </span>
                      <select
                        id="category"
                        name="category"
                        value={formData.category}
                        onChange={handleChange}
                        required
                      >
                        <option value="water_discoloration">
                          Water Discoloration
                        </option>
                        <option value="fish_mortality">Fish Mortality</option>
                        <option value="foam_surface_material">
                          Foam / Surface Material
                        </option>
                        <option value="unusual_odor">Unusual Odor</option>
                        <option value="wildlife_activity">
                          Wildlife Activity
                        </option>
                        <option value="other">Other</option>
                      </select>
                    </div>
                  </div>

                  <div className="form-field">
                    <label htmlFor="description">
                      <span className="label-title">
                        <Icon name="file" size={14} /> Field Description
                      </span>
                    </label>
                    <textarea
                      id="description"
                      name="description"
                      rows="3"
                      value={formData.description}
                      onChange={handleChange}
                      placeholder="Describe water color, odor, dead organisms, or surface film..."
                      required
                    />
                  </div>

                  <div className="form-row-duo">
                    <div className="form-field">
                      <label htmlFor="observed_at">
                        <span className="label-title">
                          <Icon name="calendar" size={14} /> Time
                        </span>
                      </label>
                      <input
                        id="observed_at"
                        name="observed_at"
                        type="datetime-local"
                        value={formData.observed_at}
                        onChange={handleChange}
                        required
                      />
                    </div>

                    <div className="form-field">
                      <label htmlFor="image_path">
                        <span className="label-title">
                          <Icon name="image" size={14} /> Photo Ref
                        </span>
                        <span className="optional-tag">Optional</span>
                      </label>
                      <div className="input-container">
                        <span className="input-icon-slot">
                          <Icon name="image" size={16} />
                        </span>
                        <input
                          id="image_path"
                          name="image_path"
                          type="text"
                          value={formData.image_path}
                          onChange={handleChange}
                          placeholder="water_sample.jpg"
                        />
                      </div>
                    </div>
                  </div>
                </div>

                <div className="form-action-footer">
                  <button
                    type="submit"
                    className="submit-btn"
                    disabled={submitting}
                  >
                    <Icon name="send" size={18} />
                    {submitting ? "Analyzing & Storing..." : "Submit Observation"}
                  </button>

                  <div className="form-disclaimer">
                    <Icon name="info" size={14} />
                    Observations generate evidence confidence for human review. Not a pollution confirmation.
                  </div>
                </div>
              </form>
            </div>

            {message && <div className="alert-box success">{message}</div>}
            {error && <div className="alert-box error">{error}</div>}

            {/* AI Evidence Assessment Card */}
            {reportId && (
              <div className="glass-card assessment-wrapper">
                <div className="card-header-bar">
                  <div className="card-title-group">
                    <div className="card-badge-icon">
                      <Icon name="brain" size={18} />
                    </div>
                    <div>
                      <h3>AI Evidence Assessment</h3>
                      <div className="card-subtitle">
                        Report Reference: #{reportId}
                      </div>
                    </div>
                  </div>
                </div>

                {loadingExplanation && (
                  <div style={{ padding: "20px", fontSize: "0.88rem" }}>
                    Generating evidence fusion & belief models...
                  </div>
                )}

                {explanationError && (
                  <div className="alert-box error" style={{ margin: "14px" }}>
                    {explanationError}
                  </div>
                )}

                {explanation && (
                  <>
                    <div className="metrics-summary-bar">
                      <div className="metric-gauge-card">
                        <div className="metric-gauge-icon">
                          <Icon name="shield" size={20} />
                        </div>
                        <div className="metric-gauge-data">
                          <span className="metric-label-small">
                            Evidence Confidence
                          </span>
                          <div className="metric-number-group">
                            <strong>
                              {Number(
                                explanation.assessment.evidence_confidence
                              ).toFixed(1)}
                            </strong>
                            <span>/100</span>
                          </div>
                          <span
                            className={`band-pill band-${bandClass(
                              explanation.assessment.confidence_band
                            )}`}
                          >
                            {explanation.assessment.confidence_band}
                          </span>
                        </div>
                      </div>

                      <div className="metric-gauge-card">
                        <div className="metric-gauge-icon blue">
                          <Icon name="brain" size={20} />
                        </div>
                        <div className="metric-gauge-data">
                          <span className="metric-label-small">AI Belief</span>
                          <div className="metric-number-group">
                            <strong>
                              {Number(
                                explanation.assessment.ai_belief
                              ).toFixed(1)}
                            </strong>
                            <span>/100</span>
                          </div>
                          <span
                            className={`band-pill band-${bandClass(
                              explanation.assessment.belief_band
                            )}`}
                          >
                            {explanation.assessment.belief_band}
                          </span>
                        </div>
                      </div>
                    </div>

                    <div className="assessment-body">
                      <div className="assessment-subcard">
                        <h3>
                          <Icon name="bulb" size={16} /> Synthesis Reasoning
                        </h3>
                        <ul style={{ paddingLeft: "18px", fontSize: "0.82rem", lineHeight: "1.5" }}>
                          {(explanation.why?.reasoning || []).map(
                            (reason, idx) => (
                              <li key={idx} style={{ marginBottom: "6px" }}>
                                {reason}
                              </li>
                            )
                          )}
                        </ul>
                      </div>

                      <div className="assessment-subcard">
                        <h3>
                          <Icon name="check" size={16} /> Supporting vs Conflicting
                        </h3>
                        <div className="evidence-items-flow">
                          {(explanation.supporting_evidence || []).map(
                            (item, idx) => (
                              <div
                                className="evidence-item-row supporting"
                                key={idx}
                              >
                                <span className="evidence-type-tag">
                                  <Icon
                                    name={evidenceIconName(item.evidence_type)}
                                    size={14}
                                  />
                                  {formatEvidenceName(item.evidence_type)}
                                </span>
                                <span className="evidence-score-delta">
                                  +{Number(item.contribution).toFixed(1)} pts
                                </span>
                              </div>
                            )
                          )}

                          {(explanation.conflicting_evidence || []).map(
                            (item, idx) => (
                              <div
                                className="evidence-item-row conflicting"
                                key={idx}
                              >
                                <span className="evidence-type-tag">
                                  <Icon
                                    name={evidenceIconName(item.evidence_type)}
                                    size={14}
                                  />
                                  {formatEvidenceName(item.evidence_type)}
                                </span>
                                <span className="evidence-score-delta">
                                  {Number(item.contribution).toFixed(1)} pts
                                </span>
                              </div>
                            )
                          )}
                        </div>
                      </div>

                      <div className="assessment-subcard">
                        <h3>
                          <Icon name="chart" size={16} /> Belief Factors
                        </h3>
                        <div className="factors-micro-grid">
                          <div className="factor-chip">
                            <span>Evidence Quality</span>
                            <strong>
                              {explanation.why?.belief_factors
                                ?.evidence_quality ?? 0}
                              %
                            </strong>
                          </div>
                          <div className="factor-chip">
                            <span>Agreement</span>
                            <strong>
                              {explanation.why?.belief_factors
                                ?.evidence_agreement ?? 0}
                              %
                            </strong>
                          </div>
                          <div className="factor-chip">
                            <span>Independence</span>
                            <strong>
                              {explanation.why?.belief_factors
                                ?.source_independence ?? 0}
                              %
                            </strong>
                          </div>
                          <div className="factor-chip">
                            <span>Completeness</span>
                            <strong>
                              {explanation.why?.belief_factors
                                ?.evidence_completeness ?? 0}
                              %
                            </strong>
                          </div>
                        </div>
                      </div>

                      <div className="review-advisory-box">
                        <div className="advisory-header">
                          <Icon name="info" size={16} /> Human Verification
                          Required
                        </div>
                        <p>
                          Evidence calibration:{" "}
                          <strong>
                            {explanation.assessment.calibration_status}
                          </strong>
                          . This score assists in triage and does not confirm
                          toxicity or legal causation.
                        </p>
                      </div>
                    </div>
                  </>
                )}
              </div>
            )}
          </div>

          {/* =================================================
              RIGHT COLUMN: Authority Surveillance & Verification Deck
          ================================================== */}
          <div className="deck-column">
            {/* Authority Command Deck */}
            <div className="glass-card">
              <div className="card-header-bar">
                <div className="card-title-group">
                  <div className="card-badge-icon">
                    <Icon name="shield" size={18} />
                  </div>
                  <div>
                    <h2>Authority Surveillance Dashboard</h2>
                    <div className="card-subtitle">
                      Live Anomaly Cluster Monitor (30s Polling)
                    </div>
                  </div>
                </div>

                <button
                  type="button"
                  className="refresh-trigger-btn"
                  onClick={loadDashboard}
                  disabled={loadingDashboard}
                >
                  <Icon name="chart" size={14} />
                  {loadingDashboard ? "Refreshing..." : "Sync Deck"}
                </button>
              </div>

              <div className="dashboard-hero-deck">
                {dashboardError && (
                  <div className="alert-box error" style={{ marginBottom: "16px" }}>
                    {dashboardError}
                  </div>
                )}

                {dashboard && (
                  <>
                    <div className="deck-metrics-row">
                      <div className="stat-kpi-card kpi-total">
                        <span className="stat-kpi-label">Total Events</span>
                        <strong>{dashboard.total_events}</strong>
                      </div>
                      <div className="stat-kpi-card kpi-potential">
                        <span className="stat-kpi-label">Potential</span>
                        <strong>{dashboard.status_counts?.potential || 0}</strong>
                      </div>
                      <div className="stat-kpi-card kpi-confirmed">
                        <span className="stat-kpi-label">Confirmed</span>
                        <strong>
                          {dashboard.status_counts?.confirmed_anomaly || 0}
                        </strong>
                      </div>
                      <div className="stat-kpi-card kpi-review">
                        <span className="stat-kpi-label">Under Review</span>
                        <strong>
                          {dashboard.status_counts?.under_review || 0}
                        </strong>
                      </div>
                    </div>

                    <div className="deck-controls-bar">
                      <span className="section-tag">
                        Active Spatial Anomaly Events
                      </span>
                    </div>

                    <div className="events-scrollable-stream">
                      {dashboard.recent_events?.length > 0 ? (
                        dashboard.recent_events.map((event) => (
                          <div
                            className={`event-dossier-card ${
                              selectedEventId === event.id
                                ? "active-selected"
                                : ""
                            }`}
                            key={event.id}
                          >
                            <div className="event-meta-block">
                              <div className="event-header-row">
                                <strong>Event #{event.id}</strong>
                                <span
                                  className={`event-status-pill ${event.status}`}
                                >
                                  {event.status}
                                </span>
                              </div>
                              <p className="event-title-line">{event.title}</p>
                            </div>

                            <div className="event-actions-block">
                              <span className="event-coordinates">
                                {Number(event.latitude).toFixed(4)},{" "}
                                {Number(event.longitude).toFixed(4)}
                              </span>
                              <button
                                type="button"
                                className="select-event-btn"
                                onClick={() => loadSelectedEventData(event.id)}
                              >
                                Review Event
                              </button>
                            </div>
                          </div>
                        ))
                      ) : (
                        <p className="muted" style={{ padding: "10px" }}>
                          No stored events are currently recorded.
                        </p>
                      )}
                    </div>
                  </>
                )}
              </div>
            </div>

            {/* Selected Event Dossier & Human-In-The-Loop Verification */}
            {selectedEventId && (
              <div className="glass-card event-workspace-panel">
                <div className="selected-event-bar">
                  <div className="event-context-summary">
                    <strong>Event #{selectedEventId}</strong>
                    <span className="status-badge-lg">
                      {currentVerificationStatus || "Unknown Status"}
                    </span>
                  </div>
                  <span className="card-subtitle">
                    Human-in-the-Loop Authority Verification Desk
                  </span>
                </div>

                <div className="workspace-content-grid">
                  {loadingVerificationHistory && (
                    <div style={{ fontSize: "0.85rem" }}>
                      Loading verification records & telemetry...
                    </div>
                  )}

                  {verificationError && (
                    <div className="alert-box error">{verificationError}</div>
                  )}

                  {verificationMessage && (
                    <div className="alert-box success">
                      {verificationMessage}
                    </div>
                  )}

                  {/* Risk Outlook Section */}
                  <div className="workspace-subsegment">
                    <h3>
                      <Icon name="chart" size={16} /> Short-Term Risk Outlook
                    </h3>

                    {loadingRiskOutlook && (
                      <p className="muted">Calculating risk forecast...</p>
                    )}

                    {riskOutlookError && (
                      <div className="alert-box error">{riskOutlookError}</div>
                    )}

                    {riskOutlook && (
                      <div className="risk-kpi-shelf">
                        <div className="risk-kpi-item">
                          <span>Risk Score</span>
                          <strong>
                            {Number(riskOutlook.risk_outlook_score).toFixed(1)}
                            /100
                          </strong>
                          <small>{riskOutlook.risk_band}</small>
                        </div>
                        <div className="risk-kpi-item">
                          <span>Trajectory</span>
                          <strong>{riskOutlook.outlook_direction}</strong>
                          <small>{riskOutlook.outlook_window}</small>
                        </div>
                        <div className="risk-kpi-item">
                          <span>Confidence</span>
                          <strong>
                            {Number(
                              riskOutlook.current_evidence_confidence
                            ).toFixed(1)}
                          </strong>
                          <small>Current baseline</small>
                        </div>
                        <div className="risk-kpi-item">
                          <span>Momentum</span>
                          <strong>
                            {Number(riskOutlook.evidence_momentum) >= 0 ? "+" : ""}
                            {Number(riskOutlook.evidence_momentum).toFixed(2)}
                          </strong>
                          <small>Shift index</small>
                        </div>
                      </div>
                    )}
                  </div>

                  {/* Recommended Actions */}
                  <div className="workspace-subsegment">
                    <h4>
                      <Icon name="check" size={16} /> Recommended Field Actions
                    </h4>

                    {loadingRecommendedActions && (
                      <p className="muted">Evaluating recommended actions...</p>
                    )}

                    {recommendedActionsError && (
                      <div className="alert-box error">
                        {recommendedActionsError}
                      </div>
                    )}

                    {!loadingRecommendedActions &&
                      !recommendedActionsError &&
                      recommendedActions.length === 0 && (
                        <p className="muted">
                          No recommended actions recorded for this event.
                        </p>
                      )}

                    {recommendedActions.length > 0 && (
                      <div className="stream-list">
                        {recommendedActions.map((action) => (
                          <div className="stream-card" key={action.id}>
                            <div
                              style={{
                                display: "flex",
                                justifyContent: "space-between",
                                marginBottom: "2px",
                              }}
                            >
                              <strong>
                                {formatActionName(action.action_type)}
                              </strong>
                              <span
                                style={{
                                  fontSize: "0.75rem",
                                  fontWeight: 700,
                                  color: "var(--ag-teal-600)",
                                }}
                              >
                                Priority: {action.priority}
                              </span>
                            </div>
                            <p>{action.description}</p>
                            <small>
                              Logged: {new Date(action.created_at).toLocaleString()}
                            </small>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>

                  {/* Verification Form Terminal */}
                  <div className="verification-terminal">
                    <div className="form-field">
                      <label htmlFor="verifier_id">Reviewer Identifier</label>
                      <input
                        id="verifier_id"
                        type="text"
                        value={verifierId}
                        onChange={(e) => setVerifierId(e.target.value)}
                        placeholder="e.g. reviewer_expert_01"
                      />
                    </div>

                    <div className="form-field">
                      <label htmlFor="verification_notes">
                        Field Review Notes
                      </label>
                      <textarea
                        id="verification_notes"
                        rows="2"
                        value={verificationNotes}
                        onChange={(e) => setVerificationNotes(e.target.value)}
                        placeholder="Log observations, lab findings, or inspection rationale..."
                      />
                    </div>

                    {canConfirm && (
                      <div className="form-field">
                        <label htmlFor="verification_basis">
                          Confirmation Basis
                        </label>
                        <select
                          id="verification_basis"
                          value={verificationBasis}
                          onChange={(e) => setVerificationBasis(e.target.value)}
                        >
                          <option value="field_inspection">
                            Field Inspection
                          </option>
                          <option value="lab_result">Laboratory Result</option>
                          <option value="visual_review">Visual Review</option>
                          <option value="community_consistency">
                            Community Consistency
                          </option>
                          <option value="other">Other</option>
                        </select>
                      </div>
                    )}

                    <div className="verification-actions-row">
                      {canOpen && (
                        <button
                          type="button"
                          className="action-btn btn-open"
                          onClick={() => submitVerification("open")}
                          disabled={verificationAction !== ""}
                        >
                          {verificationAction === "open"
                            ? "Opening..."
                            : "Open for Review"}
                        </button>
                      )}

                      {canRequestTesting && (
                        <button
                          type="button"
                          className="action-btn btn-test"
                          onClick={() => submitVerification("request_testing")}
                          disabled={verificationAction !== ""}
                        >
                          {verificationAction === "request_testing"
                            ? "Requesting..."
                            : "Request Testing"}
                        </button>
                      )}

                      {canConfirm && (
                        <button
                          type="button"
                          className="action-btn btn-confirm"
                          onClick={() => submitVerification("confirm")}
                          disabled={verificationAction !== ""}
                        >
                          {verificationAction === "confirm"
                            ? "Confirming..."
                            : "Confirm Anomaly"}
                        </button>
                      )}
                    </div>
                  </div>

                  {/* Verification History & Audit Trail */}
                  {verificationHistory && (
                    <div className="workspace-subsegment">
                      <h4>
                        <Icon name="calendar" size={16} /> Audit Trail & History
                      </h4>

                      {verificationHistory.verification_events?.length > 0 ? (
                        <div className="stream-list">
                          {verificationHistory.verification_events.map(
                            (item) => (
                              <div className="stream-card" key={item.id}>
                                <div
                                  style={{
                                    display: "flex",
                                    justifyContent: "space-between",
                                  }}
                                >
                                  <strong>{item.decision}</strong>
                                  <span style={{ fontSize: "0.75rem" }}>
                                    Officer: {item.verifier_id}
                                  </span>
                                </div>
                                <p>{item.notes || "No notes logged."}</p>
                                <small>
                                  {new Date(item.created_at).toLocaleString()}
                                </small>
                              </div>
                            )
                          )}
                        </div>
                      ) : (
                        <p className="muted">
                          No human verification events recorded yet.
                        </p>
                      )}
                    </div>
                  )}
                </div>
              </div>
            )}
          </div>
        </div>
      </main>
    </div>
  );
}

export default App;