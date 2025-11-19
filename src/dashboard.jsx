import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";

function Dashboard() {
  const [user, setUser] = useState(null);
  const navigate = useNavigate();

  // Function to refresh access token
  const refreshAccessToken = async () => {
    const refresh = localStorage.getItem("refresh_token");
    if (!refresh) return null;

    try {
      const res = await fetch("http://127.0.0.1:8000/api/accounts/token/refresh/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ refresh }),
      });

      if (!res.ok) return null;

      const data = await res.json();
      localStorage.setItem("access_token", data.access);
      return data.access;
    } catch (err) {
      console.error("Refresh token failed", err);
      return null;
    }
  };

  const fetchDashboard = async () => {
    let accessToken = localStorage.getItem("access_token");
    if (!accessToken) {
      navigate("/signin");
      return;
    }

    try {
      let res = await fetch("http://127.0.0.1:8000/api/dashboard/", {
        method: "GET",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${accessToken}`,
        },
      });

      // If access token expired, try refreshing
      if (res.status === 401) {
        accessToken = await refreshAccessToken();
        if (!accessToken) {
          navigate("/signin");
          return;
        }

        // Retry dashboard request with new token
        res = await fetch("http://127.0.0.1:8000/api/dashboard/", {
          method: "GET",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${accessToken}`,
          },
        });
      }

      if (!res.ok) {
        navigate("/signin");
        return;
      }

      const data = await res.json();
      setUser(data);
    } catch (err) {
      console.error(err);
      navigate("/signin");
    }
  };

  useEffect(() => {
    fetchDashboard();
  }, []); // run once on mount

  const handleLogout = () => {
    localStorage.removeItem("access_token");
    localStorage.removeItem("refresh_token");
    navigate("/signin");
  };

  if (!user) return <p>Loading...</p>;

  return (
    <div style={{ maxWidth: "400px", margin: "auto", padding: "2rem" }}>
      <h1>Welcome, {user.fullname}!</h1>
      <p>Email: {user.email}</p>
      <button onClick={handleLogout}>Logout</button>
    </div>
  );
}

export default Dashboard;
