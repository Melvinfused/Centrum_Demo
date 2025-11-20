import React, { useState, useEffect } from "react";
import { useNavigate, Link } from "react-router-dom";

const PasswordResetComplete = () => {
  const [password, setPassword] = useState("");
  const [confirm, setConfirm] = useState("");
  const [email, setEmail] = useState("");
  const [token, setToken] = useState("");

  const [message, setMessage] = useState("");
  const [error, setError] = useState("");

  const navigate = useNavigate();

  useEffect(() => {
    const storedEmail = localStorage.getItem("reset_email");
    const storedToken = localStorage.getItem("reset_token");

    if (!storedEmail || !storedToken) {
      setError("Session expired. Restart the reset process.");
    } else {
      setEmail(storedEmail);
      setToken(storedToken);
    }
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setMessage("");
    setError("");

    if (password !== confirm) {
      return setError("Passwords do not match.");
    }

    try {
      const response = await fetch("http://127.0.0.1:8000/api/password-reset/reset/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          email,
          reset_token: token,
          password
        }),
      });

      const data = await response.json();

      if (response.ok) {
        setMessage("Password updated successfully!");

        // Clean sensitive stored data
        localStorage.removeItem("reset_email");
        localStorage.removeItem("reset_token");

        // Redirect to login after success
        setTimeout(() => navigate("/signin"), 1200);
      } else {
        setError(data.error || "Failed to update password.");
      }

    } catch (err) {
      setError("Server error. Try again later.");
    }
  };

  return (
    <div style={{
      maxWidth: "400px",
      margin: "50px auto",
      padding: "20px",
      border: "1px solid #ccc",
      borderRadius: "8px"
    }}>
      
      <h2>Set New Password</h2>
      <p>Your email: <strong>{email || "Loading..."}</strong></p>

      <form onSubmit={handleSubmit}>
        <input
          type="password"
          placeholder="New password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          required
          style={{
            width: "100%",
            padding: "10px",
            margin: "10px 0",
            borderRadius: "4px",
            border: "1px solid #ccc"
          }}
        />

        <input
          type="password"
          placeholder="Confirm password"
          value={confirm}
          onChange={(e) => setConfirm(e.target.value)}
          required
          style={{
            width: "100%",
            padding: "10px",
            margin: "10px 0",
            borderRadius: "4px",
            border: "1px solid #ccc"
          }}
        />

        <button
          type="submit"
          style={{
            width: "100%",
            padding: "10px",
            backgroundColor: "#4CAF50",
            color: "white",
            border: "none",
            borderRadius: "4px",
            cursor: "pointer"
          }}
        >
          Update Password
        </button>
      </form>

      {message && <p style={{ color: "green", marginTop: "10px" }}>{message}</p>}
      {error && <p style={{ color: "red", marginTop: "10px" }}>{error}</p>}

      <p style={{ marginTop: "20px" }}>
        <Link to="/signin">Back to Signin</Link>
      </p>
    </div>
  );
};

export default PasswordResetComplete;
