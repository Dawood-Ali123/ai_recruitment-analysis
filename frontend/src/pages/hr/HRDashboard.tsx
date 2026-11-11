import { useEffect, useState } from "react";
import {
  BriefcaseBusiness,
  Users,
  FileText,
  CheckCircle,
  LogOut,
  Plus,
  Bell,
  Search,
  History,
} from "lucide-react";

import { useNavigate } from "react-router-dom";

import {
  getHRJobs,
  getJobApplications,
  getHRDashboardSummary,
} from "./hrService";

interface Job {
  job_id: number;
  title: string;
  status: string;
}

interface Application {
  application_id: number;
  candidate_id: number;
  candidate_name: string;
  candidate_email: string;
  job_id: number;
  status: string;
}

interface DashboardSummary {
  total_jobs: number;
  total_applications: number;
  completed_evaluations: number;
  shortlisted_candidates: number;
}

function HRDashboard() {
  const navigate = useNavigate();

  const user = JSON.parse(localStorage.getItem("user") || "{}");

  const [jobs, setJobs] = useState<Job[]>([]);
  const [applications, setApplications] = useState<Application[]>([]);

  const [summary, setSummary] = useState<DashboardSummary>({
    total_jobs: 0,
    total_applications: 0,
    completed_evaluations: 0,
    shortlisted_candidates: 0,
  });

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [search, setSearch] = useState("");

  useEffect(() => {
    const fetchDashboard = async () => {
      try {
        setLoading(true);
        setError("");

        const [jobsData, summaryData] = await Promise.all([
          getHRJobs(),
          getHRDashboardSummary(),
        ]);

        const jobsList: Job[] = Array.isArray(jobsData)
          ? jobsData
          : [];

        setJobs(jobsList);
        setSummary(summaryData);

        const applicationResults = await Promise.all(
          jobsList.map((job) =>
            getJobApplications(job.job_id)
          )
        );

        const allApplications = applicationResults.flat();

        setApplications(allApplications);

      } catch (err) {
        console.error("HR Dashboard Error:", err);
        setError("Failed to load HR dashboard data.");
      } finally {
        setLoading(false);
      }
    };

    fetchDashboard();
  }, []);

  const logout = () => {
    localStorage.removeItem("access_token");
    localStorage.removeItem("user");
    navigate("/");
  };

  const stats = [
    {
      title: "Total Jobs",
      value: summary.total_jobs,
      icon: BriefcaseBusiness,
    },
    {
      title: "Applications",
      value: summary.total_applications,
      icon: Users,
    },
    {
      title: "CV Evaluations",
      value: summary.completed_evaluations,
      icon: FileText,
    },
    {
      title: "Shortlisted",
      value: summary.shortlisted_candidates,
      icon: CheckCircle,
    },
  ];

  const filteredApplications = applications.filter((app) =>
    `${app.candidate_name} ${app.candidate_email}`
      .toLowerCase()
      .includes(search.toLowerCase())
  );

  const getJobTitle = (jobId: number) => {
    return (
      jobs.find((job) => job.job_id === jobId)?.title ||
      "Unknown Job"
    );
  };

  return (
    <div className="min-h-screen bg-[#E5EAF5]">

      {/* Navbar */}
      <nav className="flex items-center justify-between bg-white px-8 py-5 shadow-sm">

        <h1 className="text-2xl font-bold text-slate-800">
          Talent<span className="text-[#8065B5]">Flow</span>
        </h1>

        <div className="flex items-center gap-5">

          <Bell className="text-slate-500" />

          <div className="text-right">
            <p className="font-semibold text-slate-800">
              {user.full_name || "HR Manager"}
            </p>

            <p className="text-xs text-slate-500">
              HR Manager
            </p>
          </div>

          <button onClick={logout}>
            <LogOut className="text-slate-600 hover:text-red-500" />
          </button>

        </div>
      </nav>

      <main className="p-8">

        {/* Welcome */}
        <div className="mb-8 flex items-center justify-between">

          <div>
            <h2 className="text-3xl font-bold text-slate-800">
              HR Dashboard
            </h2>

            <p className="mt-2 text-slate-500">
              Manage jobs, candidates and recruitment activities.
            </p>
          </div>

         

          <div className="flex flex-wrap items-center gap-3">

  <button
    onClick={() => navigate("/hr/audit-logs")}
    className="flex items-center gap-2 rounded-xl bg-[#D0BDF4] px-5 py-3 font-semibold text-[#8065B5] hover:bg-[#C4ADEF]"
  >
    <History size={20} />
    Audit Logs
  </button>

  <button
    onClick={() => navigate("/hr/jobs/create")}
    className="flex items-center gap-2 rounded-xl bg-[#A0D2EB] px-5 py-3 font-semibold text-slate-800 hover:bg-[#88C3E2]"
  >
    <Plus size={20} />
    Create Job
  </button>

</div>

        </div>

        {/* Loading */}
        {loading && (
          <p className="text-slate-600 mb-6">
            Loading dashboard data...
          </p>
        )}

        {/* Error */}
        {error && (
          <div className="bg-red-50 text-red-600 p-4 rounded-xl mb-6">
            {error}
          </div>
        )}

        {!loading && !error && (
          <>

            {/* Statistics */}
            <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4">

              {stats.map((item) => {
                const Icon = item.icon;

                return (
                  <div
                    key={item.title}
                    className="rounded-2xl bg-white p-6 shadow-sm"
                  >

                    <div className="mb-4 flex h-12 w-12 items-center justify-center rounded-xl bg-[#E5EAF5]">
                      <Icon
                        className="text-[#8065B5]"
                        size={24}
                      />
                    </div>

                    <p className="text-sm text-slate-500">
                      {item.title}
                    </p>

                    <h3 className="mt-1 text-3xl font-bold text-slate-800">
                      {item.value}
                    </h3>

                  </div>
                );
              })}

            </div>

            {/* Applications */}
            <div className="mt-8 rounded-2xl bg-white p-6 shadow-sm">

              <div className="mb-6 flex flex-wrap items-center justify-between gap-4">

                <div>
                  <h3 className="text-xl font-bold text-slate-800">
                    Recent Applications
                  </h3>

                  <p className="mt-1 text-sm text-slate-500">
                    Monitor candidate applications.
                  </p>
                </div>

                <div className="flex items-center gap-2 rounded-xl border border-[#E5EAF5] px-4 py-2">

                  <Search
                    size={18}
                    className="text-slate-400"
                  />

                  <input
                    value={search}
                    onChange={(e) => setSearch(e.target.value)}
                    placeholder="Search applications..."
                    className="w-48 outline-none text-sm"
                  />

                </div>

              </div>

              <div className="overflow-x-auto">

                <table className="w-full text-left">

                  <thead>
                    <tr className="border-b border-[#E5EAF5] text-sm text-slate-500">
                      <th className="p-3">Candidate</th>
                      <th className="p-3">Position</th>
                      <th className="p-3">Status</th>
                      <th className="p-3">Action</th>
                    </tr>
                  </thead>

                  <tbody>

                    {filteredApplications.length === 0 ? (
                      <tr>
                        <td
                          colSpan={4}
                          className="p-8 text-center text-slate-400"
                        >
                          No applications found.
                        </td>
                      </tr>
                    ) : (
                      filteredApplications.map((app) => (
                        <tr
                          key={app.application_id}
                          className="border-b border-[#E5EAF5]"
                        >

                          <td className="p-3">
                            <p className="font-semibold text-slate-800">
                              {app.candidate_name}
                            </p>

                            <p className="text-xs text-slate-500">
                              {app.candidate_email}
                            </p>
                          </td>

                          <td className="p-3 text-slate-700">
                            {getJobTitle(app.job_id)}
                          </td>

                          <td className="p-3">
                            <span className="rounded-full bg-[#D0BDF4]/30 px-3 py-1 text-sm">
                              {app.status}
                            </span>
                          </td>

                          <td className="p-3">
                            <button
                              onClick={() =>
                                navigate(
                                  `/hr/applications/${app.application_id}`
                                )
                              }
                              className="text-[#8065B5] font-semibold hover:underline"
                            >
                              View
                            </button>
                          </td>

                        </tr>
                      ))
                    )}

                  </tbody>

                </table>

              </div>
            </div>

          </>
        )}

      </main>
    </div>
  );
}

export default HRDashboard;