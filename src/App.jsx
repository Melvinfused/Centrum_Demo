import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import Signup from "./signup";
import Signin from "./signin";
import Dashboard from "./dashboard";
import PasswordResetRequest from "./pass_reset_request";
import PasswordResetVerification from "./pass_reset_verify";
import PasswordResetComplete from "./pass_reset_complete";

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Signup />} />       {/* default route */}
        <Route path="/signin" element={<Signin />} />  {/* login page */}
        <Route path="/pass_reset_request" element={<PasswordResetRequest />} />  {/* password reset request page */}
        <Route path="/pass_reset_verify" element={<PasswordResetVerification />} />  {/* password reset otp verification page */}
        <Route path="/pass_reset_complete" element={<PasswordResetComplete />} />  {/* password reset page */}
        <Route path="/dashboard" element={<Dashboard />} /> {/* dashboard after login */}
      </Routes>
    </Router>
  );
}

export default App;
