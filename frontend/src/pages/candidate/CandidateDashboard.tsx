import { useEffect, useState } from "react";
import {
  BriefcaseBusiness,
  FileText,
  Clock,
  LogOut,
  MapPin,
  CheckCircle,
  AlertCircle,
  Eye,
  BrainCircuit,
  Upload,
  UserCheck,
} from "lucide-react";
import { useNavigate } from "react-router-dom";

import {
  getAvailableJobs,
  getMyApplicationTracking,
} from "../../services/candidateService";

interface Job {
  job_id: number;
  title: string;
  description?: string;
  location?: string;
  status?: string;
}

interface ApplicationTracking {
  application_id: number;
  job_id: number;
  job_title: string;
  application_status: string;
  applied_at?: string;

  cv: {
    uploaded: boolean;
    filename?: string | null;
    version?: number | null;
  };

  ai_evaluation: {
    status: string;
    score?: number | null;
    recommendation?: string | null;
  };

  hr_decision: {
    decision?: string | null;
    decision_date?: string | null;
  };
}

interface User {
  full_name: string;
}

const CandidateDashboard = () => {
  const navigate = useNavigate();

  const [user] = useState<User | null>(() => {
    try {
      return JSON.parse(localStorage.getItem("user") || "null");
    } catch {
      return null;
    }
  });

  const [jobs, setJobs] = useState<Job[]>([]);
  const [applications, setApplications] = useState<ApplicationTracking[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    const fetchDashboardData = async () => {
      try {
        setLoading(true);
        setError("");

        const [jobsData, trackingData] = await Promise.all([
          getAvailableJobs(),
          getMyApplicationTracking(),
        ]);

        setJobs(
          Array.isArray(jobsData)
            ? jobsData
            : jobsData.items ?? jobsData.jobs ?? []
        );

        setApplications(
          Array.isArray(trackingData)
            ? trackingData
            : trackingData.items ?? trackingData.applications ?? []
        );
      } catch (err) {
        console.error("Dashboard API Error:", err);
        setError("Failed to load dashboard data.");
      } finally {
        setLoading(false);
      }
    };

    fetchDashboardData();
  }, []);

  const handleLogout = () => {
    localStorage.removeItem("access_token");
    localStorage.removeItem("user");
    navigate("/");
  };

  const getStatusStyle = (status: string) => {
    const normalized = status.toLowerCase();

    if (
      normalized.includes("shortlist") ||
      normalized.includes("accept")
    ) {
      return "bg-green-100 text-green-700";
    }

    if (normalized.includes("reject")) {
      return "bg-red-100 text-red-700";
    }

    if (
      normalized.includes("review") ||
      normalized.includes("process")
    ) {
      return "bg-blue-100 text-blue-700";
    }

    if (
      normalized.includes("pending") ||
      normalized.includes("submitted") ||
      normalized.includes("applied")
    ) {
      return "bg-yellow-100 text-yellow-700";
    }

    return "bg-slate-100 text-slate-700";
  };

  const pendingApplications = applications.filter((app) => {
    const status = app.application_status?.toLowerCase() || "";

    return (
      status === "pending" ||
      status === "applied" ||
      status === "submitted" ||
      status === "needs review" ||
      status === "processing"
    );
  }).length;

  const stats = [
    {
      title: "Available Jobs",
      value: jobs.length,
      icon: BriefcaseBusiness,
    },
    {
      title: "My Applications",
      value: applications.length,
      icon: FileText,
    },
    {
      title: "Pending Applications",
      value: pendingApplications,
      icon: Clock,
    },
  ];

  const formatDate = (date?: string | null) => {
    if (!date) return "Not available";

    const parsedDate = new Date(date);

    if (isNaN(parsedDate.getTime())) return "Not available";

    return parsedDate.toLocaleDateString();
  };

  return (
    <div className="min-h-screen bg-[#E5EAF5]">

      {/* Header */}
      <header className="bg-white px-8 py-5 shadow-sm flex justify-between items-center">

        <h1 className="text-2xl font-bold text-slate-800">
          TalentFlow <span className="text-[#8065B5]">AI</span>
        </h1>

        <div className="flex items-center gap-5">
          <span className="text-slate-700 font-medium">
            {user?.full_name || "Candidate"}
          </span>

          <button
            onClick={handleLogout}
            className="flex items-center gap-2 text-red-500 hover:text-red-700"
          >
            <LogOut size={18} />
            Logout
          </button>
        </div>

      </header>

      {/* Main */}
      <main className="p-8 max-w-7xl mx-auto">

        <div className="mb-8">
          <h2 className="text-3xl font-bold text-slate-800">
            Candidate Dashboard
          </h2>

          <p className="text-slate-500 mt-2">
            Explore opportunities and track your applications.
          </p>
        </div>

        {error && (
          <div className="bg-red-50 text-red-600 p-4 rounded-xl mb-6">
            {error}
          </div>
        )}

        {loading ? (
          <p className="text-slate-600">
            Loading dashboard...
          </p>
        ) : (
          <>

            {/* Statistics */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-10">

              {stats.map((stat) => {
                const Icon = stat.icon;

                return (
                  <div
                    key={stat.title}
                    className="bg-white rounded-xl p-6 shadow-sm"
                  >
                    <div className="flex justify-between items-center">

                      <div>
                        <p className="text-slate-500">
                          {stat.title}
                        </p>

                        <h3 className="text-3xl font-bold text-slate-800 mt-2">
                          {stat.value}
                        </h3>
                      </div>

                      <div className="bg-[#D0BDF4]/30 p-4 rounded-lg">
                        <Icon
                          size={25}
                          className="text-[#8065B5]"
                        />
                      </div>

                    </div>
                  </div>
                );
              })}

            </div>

            {/* Available Jobs */}
            <div className="bg-white rounded-xl p-6 shadow-sm">

              <h3 className="text-xl font-bold text-slate-800 mb-6">
                Available Jobs
              </h3>

              {jobs.length === 0 ? (
                <p className="text-slate-500">
                  No jobs available right now.
                </p>
              ) : (
                <div className="space-y-4">

                  {jobs.map((job) => (
                    <div
                      key={job.job_id}
                      className="border border-[#E5EAF5] rounded-xl p-5 hover:border-[#A0D2EB] transition"
                    >

                      <div className="flex flex-col sm:flex-row sm:justify-between sm:items-center gap-4">

                        <div>
                          <h4 className="text-lg font-semibold text-slate-800">
                            {job.title}
                          </h4>

                          {job.location && (
                            <p className="flex items-center gap-2 text-sm text-slate-500 mt-2">
                              <MapPin size={15} />
                              {job.location}
                            </p>
                          )}

                          {job.description && (
                            <p className="text-sm text-slate-600 mt-2 line-clamp-2">
                              {job.description}
                            </p>
                          )}
                        </div>

                        <button
                          type="button"
                          className="bg-[#A0D2EB] hover:bg-[#88C3E2] px-5 py-2.5 rounded-lg font-semibold text-slate-800"
                          onClick={() =>
                            navigate(`/candidate/jobs/${job.job_id}`)
                          }
                        >
                          View Job
                        </button>

                      </div>
                    </div>
                  ))}

                </div>
              )}

            </div>

            {/* Application Tracking */}
            <div className="bg-white rounded-xl p-6 shadow-sm mt-8">

              <div className="flex items-center gap-3 mb-6">

                <FileText
                  size={25}
                  className="text-[#8065B5]"
                />

                <div>
                  <h3 className="text-xl font-bold text-slate-800">
                    Application Tracking
                  </h3>

                  <p className="text-sm text-slate-500 mt-1">
                    Monitor your CV, AI evaluation and HR decisions.
                  </p>
                </div>

              </div>

              {applications.length === 0 ? (
                <div className="text-center py-10 bg-[#F8F9FC] rounded-xl">

                  <AlertCircle
                    size={40}
                    className="mx-auto text-slate-400 mb-3"
                  />

                  <p className="text-slate-600 font-medium">
                    No applications yet.
                  </p>

                  <p className="text-sm text-slate-500 mt-2">
                    Apply for a job to start tracking your application.
                  </p>

                </div>
              ) : (
                <div className="space-y-6">

                  {applications.map((app) => (

                    <div
                      key={app.application_id}
                      className="border border-[#E5EAF5] rounded-xl p-5 hover:border-[#A0D2EB] transition"
                    >

                      {/* Application Header */}
                      <div className="flex flex-col md:flex-row md:justify-between md:items-start gap-4">

                        <div>
                          <h4 className="text-lg font-bold text-slate-800">
                            {app.job_title || `Job #${app.job_id}`}
                          </h4>

                          <p className="text-sm text-slate-500 mt-2">
                            Application ID: #{app.application_id}
                          </p>

                          <p className="text-sm text-slate-500 mt-1">
                            Applied: {formatDate(app.applied_at)}
                          </p>
                        </div>

                        <span
                          className={`px-4 py-2 rounded-full text-sm font-semibold ${getStatusStyle(
                            app.application_status || "Unknown"
                          )}`}
                        >
                          {app.application_status || "Unknown"}
                        </span>

                      </div>

                      {/* Tracking Details */}
                      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-6">

                        {/* CV Status */}
                        <div className="bg-[#F8F9FC] rounded-xl p-4">

                          <div className="flex items-center gap-2 mb-3">
                            <Upload
                              size={19}
                              className="text-[#8065B5]"
                            />

                            <h5 className="font-semibold text-slate-800">
                              CV Status
                            </h5>
                          </div>

                          {app.cv?.uploaded ? (
                            <>
                              <p className="text-sm text-green-700 font-medium">
                                <CheckCircle
                                  size={15}
                                  className="inline mr-1"
                                />
                                CV Uploaded
                              </p>

                              <p className="text-xs text-slate-500 mt-2 break-all">
                                {app.cv.filename}
                              </p>

                              <p className="text-xs text-slate-500 mt-1">
                                Version: {app.cv.version ?? "N/A"}
                              </p>
                            </>
                          ) : (
                            <p className="text-sm text-yellow-700">
                              CV not uploaded
                            </p>
                          )}

                        </div>

                        {/* AI Evaluation */}
                        <div className="bg-[#F8F9FC] rounded-xl p-4">

                          <div className="flex items-center gap-2 mb-3">
                            <BrainCircuit
                              size={19}
                              className="text-[#8065B5]"
                            />

                            <h5 className="font-semibold text-slate-800">
                              AI Evaluation
                            </h5>
                          </div>

                          <span
                            className={`inline-block px-3 py-1 rounded-full text-xs font-semibold ${getStatusStyle(
                              app.ai_evaluation?.status || "Not Started"
                            )}`}
                          >
                            {app.ai_evaluation?.status || "Not Started"}
                          </span>

                          <p className="text-sm text-slate-600 mt-3">
                            Score:{" "}
                            <span className="font-bold text-slate-800">
                              {app.ai_evaluation?.score != null
                                ? `${app.ai_evaluation.score}/100`
                                : "Not available"}
                            </span>
                          </p>

                          <p className="text-xs text-slate-500 mt-2">
                            Recommendation:
                          </p>

                          <p className="text-sm font-semibold text-[#8065B5] mt-1">
                            {app.ai_evaluation?.recommendation || "Pending"}
                          </p>

                        </div>

                        {/* HR Decision */}
                        <div className="bg-[#F8F9FC] rounded-xl p-4">

                          <div className="flex items-center gap-2 mb-3">
                            <UserCheck
                              size={19}
                              className="text-[#8065B5]"
                            />

                            <h5 className="font-semibold text-slate-800">
                              HR Decision
                            </h5>
                          </div>

                          {app.hr_decision?.decision ? (
                            <>
                              <span
                                className={`inline-block px-3 py-1 rounded-full text-xs font-semibold ${getStatusStyle(
                                  app.hr_decision.decision
                                )}`}
                              >
                                {app.hr_decision.decision}
                              </span>

                              <p className="text-xs text-slate-500 mt-3">
                                Decision Date:
                              </p>

                              <p className="text-sm text-slate-700 mt-1">
                                {formatDate(app.hr_decision.decision_date)}
                              </p>
                            </>
                          ) : (
                            <p className="text-sm text-slate-500">
                              Awaiting HR decision
                            </p>
                          )}

                        </div>

                      </div>

                      {/* View Job */}
                      <div className="mt-5 pt-4 border-t border-[#E5EAF5] flex justify-end">

                        <button
                          onClick={() =>
                            navigate(`/candidate/jobs/${app.job_id}`)
                          }
                          className="flex items-center gap-2 text-[#8065B5] hover:text-[#60449A] font-semibold text-sm"
                        >
                          <Eye size={17} />
                          View Job
                        </button>

                      </div>

                    </div>

                  ))}

                </div>
              )}

            </div>

          </>
        )}

      </main>
    </div>
  );
};

export default CandidateDashboard;