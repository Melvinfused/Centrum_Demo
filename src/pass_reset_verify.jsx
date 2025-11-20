import React, { useState, useEffect } from "react";
import { Link, useNavigate } from "react-router-dom";

const PasswordResetVerification = () => {
  const [otp, setOtp] = useState("");
  const [email, setEmail] = useState("");
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");

  const navigate = useNavigate();

  // Load stored email when page opens
  useEffect(() => {
    const storedEmail = localStorage.getItem("reset_email");
    if (storedEmail) {
      setEmail(storedEmail);
    } else {
      setError("No email found. Restart password reset process.");
    }
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setMessage("");
    setError("");

    try {
      const response = await fetch("http://127.0.0.1:8000/api/password-reset/verify/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, otp }),
      });

      const data = await response.json();

      if (response.ok) {
        setMessage("OTP Verified!");
        
        // Save reset token (optional if backend sends)
        if (data.reset_token) {
          localStorage.setItem("reset_token", data.reset_token);
        }
        navigate("/pass_reset_complete");
      } else {
        setError(data.error || "Invalid OTP.");
      }
    } catch (err) {
      setError("Failed to verify. Try again later.");
    }
  };

  return (
    <div style={{ maxWidth: "400px", margin: "50px auto", padding: "20px", border: "1px solid #ccc", borderRadius: "8px" }}>
      <h2>Verify OTP</h2>
      <p>A verification code was sent to:</p>
      <strong>{email}</strong>

      <form onSubmit={handleSubmit}>
        <input
          type="text"
          placeholder="Enter OTP"
          value={otp}
          onChange={(e) => setOtp(e.target.value)}
          required
          style={{ width: "100%", padding: "10px", margin: "10px 0", borderRadius: "4px", border: "1px solid #ccc" }}
        />

        <button
          type="submit"
          style={{ width: "100%", padding: "10px", backgroundColor: "#4CAF50", color: "white", border: "none", borderRadius: "4px", cursor: "pointer" }}
        >
          Verify OTP
        </button>
      </form>

      {message && <p style={{ color: "green", marginTop: "10px" }}>{message}</p>}
      {error && <p style={{ color: "red", marginTop: "10px" }}>{error}</p>}

      <p style={{ marginTop: "20px" }}>
        <Link to="/signin">Cancel</Link>
      </p>
    </div>
  );
};

export default PasswordResetVerification;
