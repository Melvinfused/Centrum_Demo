import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import Signup from "./signup";
import Signin from "./signin";
import Dashboard from "./dashboard";
import PasswordResetRequest from "./pass_reset_request";

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Signup />} />       {/* default route */}
        <Route path="/signin" element={<Signin />} />  {/* login page */}
        <Route path="/reset-password-request" element={<PasswordResetRequest />} />  {/* password reset request page */}
        <Route path="/dashboard" element={<Dashboard />} /> {/* dashboard after login */}
      </Routes>
    </Router>
  );
}

export default App;
