import { useState } from "react";
import {
  Routes,
  Route,
  Navigate,
  useNavigate,
  useLocation,
} from "react-router-dom";

import api from "./services/api";
import { loginUser } from "./services/authService";

import HRDashboard from "./pages/hr/HRDashboard";
import CandidateDashboard from "./pages/candidate/CandidateDashboard";
import JobDetails from "./pages/candidate/JobDetails";
import ApplyJob from "./pages/candidate/ApplyJob";

import CreateJob from "./pages/hr/CreateJob";
import JobRequirements from "./pages/hr/JobRequirements";
import HRApplicationDetails from "./pages/hr/HRApplicationDetails";
import AuditLogs from "./pages/hr/AuditLogs";

// ================= LOGIN PAGE =================

function LoginPage() {
  const navigate = useNavigate();
  const location = useLocation();

  const [role, setRole] = useState<"candidate" | "hr">("candidate");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const registrationSuccess = location.state?.registrationSuccess;

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();

    setError("");
    setLoading(true);

    try {
      const user = await loginUser({ email, password });

      if (user.role.toLowerCase() !== role) {
        localStorage.removeItem("access_token");
        localStorage.removeItem("user");

        setError("Selected role does not match your account.");
        return;
      }

      navigate(
        role === "hr"
          ? "/hr/dashboard"
          : "/candidate/dashboard"
      );

    } catch (err: any) {
      setError(
        err.response?.data?.detail ||
          "Login failed. Please try again."
      );

    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#E5EAF5] flex items-center justify-center p-6">

      <div className="w-full max-w-md">

        {/* Branding */}

        <div className="text-center mb-8">

          <div className="mx-auto mb-4 flex h-16 w-16 items-center justify-center rounded-2xl bg-[#A0D2EB] text-2xl font-bold text-slate-800">
            TF
          </div>

          <h1 className="text-3xl font-bold text-slate-800">
            Talent<span className="text-[#8065B5]">Flow</span>
          </h1>

          <p className="mt-2 text-slate-600">
            Smarter hiring. Better opportunities.
          </p>

        </div>

        {/* Login Card */}

        <div className="rounded-3xl border border-white bg-white p-8 shadow-xl">

          <h2 className="text-2xl font-bold text-slate-800">
            Welcome Back!
          </h2>

          <p className="mt-2 text-sm text-slate-500">
            Sign in to continue.
          </p>

          {/* Registration Success */}

          {registrationSuccess && (
            <p className="mt-5 rounded-lg bg-green-50 p-3 text-sm text-green-700">
              {registrationSuccess}
            </p>
          )}

          {/* Role Selection */}

          <div className="mt-7 grid grid-cols-2 gap-3 rounded-xl bg-[#E5EAF5] p-1">

            <button
              type="button"
              onClick={() => {
                setRole("candidate");
                setError("");
              }}
              className={`rounded-lg py-3 text-sm font-semibold ${
                role === "candidate"
                  ? "bg-[#A0D2EB] text-slate-800"
                  : "text-slate-600"
              }`}
            >
              Candidate
            </button>

            <button
              type="button"
              onClick={() => {
                setRole("hr");
                setError("");
              }}
              className={`rounded-lg py-3 text-sm font-semibold ${
                role === "hr"
                  ? "bg-[#D0BDF4] text-slate-800"
                  : "text-slate-600"
              }`}
            >
              HR
            </button>

          </div>

          {/* Login Form */}

          <form onSubmit={handleLogin} className="mt-7 space-y-5">

            <div>

              <label className="mb-2 block text-sm font-semibold text-slate-700">
                Email Address
              </label>

              <input
                type="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="name@example.com"
                className="w-full rounded-xl border border-[#E5EAF5] bg-[#F8F9FC] px-4 py-3.5 outline-none focus:border-[#A0D2EB]"
              />

            </div>

            <div>

              <label className="mb-2 block text-sm font-semibold text-slate-700">
                Password
              </label>

              <input
                type="password"
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="Enter your password"
                className="w-full rounded-xl border border-[#E5EAF5] bg-[#F8F9FC] px-4 py-3.5 outline-none focus:border-[#D0BDF4]"
              />

            </div>

            {/* Error Message */}

            {error && (
              <p className="rounded-lg bg-red-50 p-3 text-sm text-red-600">
                {error}
              </p>
            )}

            {/* Submit */}

            <button
              type="submit"
              disabled={loading}
              className="w-full rounded-xl bg-[#A0D2EB] py-3.5 font-bold text-slate-800 transition hover:bg-[#88C3E2] disabled:opacity-60"
            >
              {loading ? "Signing In..." : "Sign In"}
            </button>

          </form>

          {/* Registration Link */}

          {role === "candidate" && (
            <p className="mt-6 text-center text-sm text-slate-500">

              Don't have an account?{" "}

              <button
                type="button"
                onClick={() => navigate("/register")}
                className="font-semibold text-[#8065B5] hover:underline"
              >
                Create Account
              </button>

            </p>
          )}

        </div>

        <p className="mt-7 text-center text-xs text-slate-500">
          © 2026 TalentFlow AI. All rights reserved.
        </p>

      </div>

    </div>
  );
}


// ================= REGISTRATION PAGE =================

function RegisterPage() {

  const navigate = useNavigate();

  const [fullName, setFullName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleRegister = async (e: React.FormEvent) => {

    e.preventDefault();

    setError("");

    // Password confirmation

    if (password !== confirmPassword) {
      setError("Passwords do not match.");
      return;
    }

    setLoading(true);

    try {

      // Backend registration API

      await api.post("/auth/register", {
        full_name: fullName.trim(),
        email: email.trim(),
        password: password,
      });

      // Redirect to login after successful registration

      navigate("/", {
        state: {
          registrationSuccess:
            "Account created successfully! Please sign in."
        }
      });

    } catch (err: any) {

      const detail = err.response?.data?.detail;

      setError(
        typeof detail === "string"
          ? detail
          : "Registration failed. Please try again."
      );

    } finally {

      setLoading(false);

    }

  };

  return (

    <div className="min-h-screen bg-[#E5EAF5] flex items-center justify-center p-6">

      <div className="w-full max-w-md">

        {/* Branding */}

        <div className="text-center mb-8">

          <div className="mx-auto mb-4 flex h-16 w-16 items-center justify-center rounded-2xl bg-[#A0D2EB] text-2xl font-bold text-slate-800">
            TF
          </div>

          <h1 className="text-3xl font-bold text-slate-800">
            Talent<span className="text-[#8065B5]">Flow</span>
          </h1>

          <p className="mt-2 text-slate-600">
            Start your career journey with us.
          </p>

        </div>

        {/* Registration Card */}

        <div className="rounded-3xl border border-white bg-white p-8 shadow-xl">

          <h2 className="text-2xl font-bold text-slate-800">
            Create Account
          </h2>

          <p className="mt-2 text-sm text-slate-500">
            Register as a candidate to explore opportunities.
          </p>

          {/* Registration Form */}

          <form
            onSubmit={handleRegister}
            className="mt-7 space-y-5"
          >

            {/* Full Name */}

            <div>

              <label className="mb-2 block text-sm font-semibold text-slate-700">
                Full Name
              </label>

              <input
                type="text"
                required
                value={fullName}
                onChange={(e) => setFullName(e.target.value)}
                placeholder="Enter your full name"
                className="w-full rounded-xl border border-[#E5EAF5] bg-[#F8F9FC] px-4 py-3.5 outline-none focus:border-[#A0D2EB]"
              />

            </div>

            {/* Email */}

            <div>

              <label className="mb-2 block text-sm font-semibold text-slate-700">
                Email Address
              </label>

              <input
                type="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="name@example.com"
                className="w-full rounded-xl border border-[#E5EAF5] bg-[#F8F9FC] px-4 py-3.5 outline-none focus:border-[#A0D2EB]"
              />

            </div>

            {/* Password */}

            <div>

              <label className="mb-2 block text-sm font-semibold text-slate-700">
                Password
              </label>

              <input
                type="password"
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="Create a password"
                className="w-full rounded-xl border border-[#E5EAF5] bg-[#F8F9FC] px-4 py-3.5 outline-none focus:border-[#D0BDF4]"
              />

            </div>

            {/* Confirm Password */}

            <div>

              <label className="mb-2 block text-sm font-semibold text-slate-700">
                Confirm Password
              </label>

              <input
                type="password"
                required
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
                placeholder="Confirm your password"
                className="w-full rounded-xl border border-[#E5EAF5] bg-[#F8F9FC] px-4 py-3.5 outline-none focus:border-[#D0BDF4]"
              />

            </div>

            {/* Error Message */}

            {error && (

              <p className="rounded-lg bg-red-50 p-3 text-sm text-red-600">
                {error}
              </p>

            )}

            {/* Register Button */}

            <button
              type="submit"
              disabled={loading}
              className="w-full rounded-xl bg-[#A0D2EB] py-3.5 font-bold text-slate-800 transition hover:bg-[#88C3E2] disabled:opacity-60"
            >

              {loading
                ? "Creating Account..."
                : "Create Account"}

            </button>

          </form>

          {/* Login Link */}

          <p className="mt-6 text-center text-sm text-slate-500">

            Already have an account?{" "}

            <button
              type="button"
              onClick={() => navigate("/")}
              className="font-semibold text-[#8065B5] hover:underline"
            >
              Sign In
            </button>

          </p>

        </div>

        <p className="mt-7 text-center text-xs text-slate-500">
          © 2026 TalentFlow AI. All rights reserved.
        </p>

      </div>

    </div>

  );

}


// ================= PROTECTED ROUTE =================

function ProtectedRoute({
  allowedRole,
  children,
}: {
  allowedRole: "hr" | "candidate";
  children: React.ReactNode;
}) {

  const token = localStorage.getItem("access_token");

  let user = null;

  try {
    user = JSON.parse(localStorage.getItem("user") || "null");
  } catch {
    user = null;
  }

  if (!token || !user) {
    return <Navigate to="/" replace />;
  }

  if (user.role?.toLowerCase() !== allowedRole) {
    return <Navigate to="/" replace />;
  }

  return <>{children}</>;
}


// ================= MAIN APP ROUTES =================

function App() {

  return (

    <Routes>

      {/* LOGIN */}

      <Route
        path="/"
        element={<LoginPage />}
      />

      {/* CANDIDATE REGISTRATION */}

      <Route
        path="/register"
        element={<RegisterPage />}
      />

      {/* HR ROUTES */}

      <Route
        path="/hr/dashboard"
        element={
          <ProtectedRoute allowedRole="hr">
            <HRDashboard />
          </ProtectedRoute>
        }
      />

      <Route
        path="/hr/jobs/create"
        element={
          <ProtectedRoute allowedRole="hr">
            <CreateJob />
          </ProtectedRoute>
        }
      />

      <Route
        path="/hr/jobs/:jobId/requirements"
        element={
          <ProtectedRoute allowedRole="hr">
            <JobRequirements />
          </ProtectedRoute>
        }
      />

      <Route
        path="/hr/applications/:applicationId"
        element={
          <ProtectedRoute allowedRole="hr">
            <HRApplicationDetails />
          </ProtectedRoute>
        }
      />

      <Route
        path="/hr/audit-logs"
        element={
          <ProtectedRoute allowedRole="hr">
            <AuditLogs />
          </ProtectedRoute>
        }
      />

      {/* CANDIDATE ROUTES */}

      <Route
        path="/candidate/dashboard"
        element={
          <ProtectedRoute allowedRole="candidate">
            <CandidateDashboard />
          </ProtectedRoute>
        }
      />

      <Route
        path="/candidate/jobs/:jobId"
        element={
          <ProtectedRoute allowedRole="candidate">
            <JobDetails />
          </ProtectedRoute>
        }
      />

      <Route
        path="/candidate/jobs/:jobId/apply"
        element={
          <ProtectedRoute allowedRole="candidate">
            <ApplyJob />
          </ProtectedRoute>
        }
      />

      {/* INVALID ROUTES */}

      <Route
        path="*"
        element={<Navigate to="/" replace />}
      />

    </Routes>

  );

}

export default App;