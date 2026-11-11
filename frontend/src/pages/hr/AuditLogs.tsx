import { useEffect, useState } from "react";
import {
  ArrowLeft,
  History,
  RefreshCw,
  ChevronLeft,
  ChevronRight,
  Activity,
  FileText,
  AlertCircle,
} from "lucide-react";
import { useNavigate } from "react-router-dom";

import { getHRJobs } from "./hrService";
import { getJobAuditLogs } from "../../services/auditLogService";

interface Job {
  job_id: number;
  title: string;
  status: string;
}

interface AuditLog {
  log_id: number;
  application_id: number | null;
  actor_id: number | null;
  action: string;
  entity_type: string;
  entity_id: number | null;
  details: Record<string, any> | null;
  created_at: string;
}

const PAGE_SIZE = 50;

function AuditLogs() {
  const navigate = useNavigate();

  const [jobs, setJobs] = useState<Job[]>([]);
  const [selectedJob, setSelectedJob] = useState("");

  const [logs, setLogs] = useState<AuditLog[]>([]);

  const [loadingJobs, setLoadingJobs] = useState(true);
  const [loadingLogs, setLoadingLogs] = useState(false);

  const [error, setError] = useState("");

  const [offset, setOffset] = useState(0);

  // Fetch HR jobs
  const fetchJobs = async () => {
    try {
      setLoadingJobs(true);
      setError("");

      const data = await getHRJobs();

      const jobsList: Job[] = Array.isArray(data) ? data : [];

      setJobs(jobsList);

      if (jobsList.length > 0) {
        setSelectedJob(String(jobsList[0].job_id));
      }
    } catch (err: any) {
      console.error("Jobs Fetch Error:", err);

      setError(
        err.response?.data?.detail ||
          "Failed to load jobs."
      );
    } finally {
      setLoadingJobs(false);
    }
  };

  // Fetch audit logs
  const fetchLogs = async (
    jobId: number,
    currentOffset: number
  ) => {
    try {
      setLoadingLogs(true);
      setError("");

      const data = await getJobAuditLogs(
        jobId,
        PAGE_SIZE,
        currentOffset
      );

      setLogs(data.logs || []);
    } catch (err: any) {
      console.error("Audit Logs Error:", err);

      setLogs([]);

      setError(
        err.response?.data?.detail ||
          "Failed to load audit logs."
      );
    } finally {
      setLoadingLogs(false);
    }
  };

  // Initial jobs loading
  useEffect(() => {
    fetchJobs();
  }, []);

  // Fetch logs whenever job or page changes
  useEffect(() => {
    if (!selectedJob) {
      setLogs([]);
      return;
    }

    fetchLogs(Number(selectedJob), offset);
  }, [selectedJob, offset]);

  // Change selected job
  const handleJobChange = (
    e: React.ChangeEvent<HTMLSelectElement>
  ) => {
    setSelectedJob(e.target.value);
    setOffset(0);
  };

  // Format date
  const formatDate = (date: string) => {
    return new Date(date).toLocaleString();
  };

  // Action badge colors
  const getActionColor = (action: string) => {
    switch (action) {
      case "APPLICATION_SUBMITTED":
        return "bg-blue-100 text-blue-700";

      case "CV_UPLOADED":
        return "bg-purple-100 text-purple-700";

      case "HR_DECISION_RECORDED":
        return "bg-green-100 text-green-700";

      default:
        return "bg-slate-100 text-slate-700";
    }
  };

  // Refresh logs
  const handleRefresh = () => {
    if (selectedJob) {
      fetchLogs(Number(selectedJob), offset);
    }
  };

  // Pagination
  const handlePrevious = () => {
    setOffset((prev) => Math.max(0, prev - PAGE_SIZE));
  };

  const handleNext = () => {
    if (logs.length === PAGE_SIZE) {
      setOffset((prev) => prev + PAGE_SIZE);
    }
  };

  return (
    <div className="min-h-screen bg-[#E5EAF5]">

      {/* Navbar */}
      <nav className="flex items-center justify-between bg-white px-8 py-5 shadow-sm">

        <h1 className="text-2xl font-bold text-slate-800">
          Talent<span className="text-[#8065B5]">Flow</span>
        </h1>

        <button
          onClick={() => navigate("/hr/dashboard")}
          className="flex items-center gap-2 rounded-xl border border-[#E5EAF5] px-4 py-2 font-semibold text-slate-700 hover:bg-[#E5EAF5]"
        >
          <ArrowLeft size={18} />
          Dashboard
        </button>

      </nav>

      <main className="p-8">

        {/* Page Heading */}
        <div className="mb-8">

          <div className="flex items-center gap-3">

            <div className="flex h-14 w-14 items-center justify-center rounded-2xl bg-[#D0BDF4]/40">
              <History
                size={28}
                className="text-[#8065B5]"
              />
            </div>

            <div>
              <h2 className="text-3xl font-bold text-slate-800">
                Audit Logs
              </h2>

              <p className="mt-1 text-slate-500">
                Track recruitment activities and system history.
              </p>
            </div>

          </div>

        </div>

        {/* Error Message */}
        {error && (
          <div className="mb-6 flex items-center gap-3 rounded-xl bg-red-50 p-4 text-red-600">
            <AlertCircle size={20} />
            {error}
          </div>
        )}

        {/* Job Selection */}
        <div className="mb-6 rounded-2xl bg-white p-6 shadow-sm">

          <div className="flex flex-wrap items-center justify-between gap-4">

            <div>
              <h3 className="text-lg font-bold text-slate-800">
                Select Job
              </h3>

              <p className="mt-1 text-sm text-slate-500">
                View activity history for a specific job.
              </p>
            </div>

            <div className="flex flex-wrap items-center gap-3">

              <select
                value={selectedJob}
                onChange={handleJobChange}
                disabled={loadingJobs || jobs.length === 0}
                className="min-w-64 rounded-xl border border-[#E5EAF5] bg-[#F8F9FC] px-4 py-3 text-slate-700 outline-none focus:border-[#A0D2EB]"
              >
                {loadingJobs ? (
                  <option>Loading jobs...</option>
                ) : jobs.length === 0 ? (
                  <option value="">
                    No jobs available
                  </option>
                ) : (
                  jobs.map((job) => (
                    <option
                      key={job.job_id}
                      value={job.job_id}
                    >
                      {job.title}
                    </option>
                  ))
                )}
              </select>

              <button
                onClick={handleRefresh}
                disabled={!selectedJob || loadingLogs}
                className="flex items-center gap-2 rounded-xl bg-[#A0D2EB] px-4 py-3 font-semibold text-slate-800 hover:bg-[#88C3E2] disabled:opacity-50"
              >
                <RefreshCw
                  size={18}
                  className={loadingLogs ? "animate-spin" : ""}
                />
                Refresh
              </button>

            </div>

          </div>

        </div>

        {/* Audit Logs Section */}
        <div className="rounded-2xl bg-white p-6 shadow-sm">

          <div className="mb-6 flex items-center justify-between">

            <div>
              <h3 className="text-xl font-bold text-slate-800">
                Activity History
              </h3>

              <p className="mt-1 text-sm text-slate-500">
                Recruitment events recorded in the system.
              </p>
            </div>

            <div className="flex items-center gap-2 rounded-xl bg-[#E5EAF5] px-4 py-2">
              <Activity
                size={18}
                className="text-[#8065B5]"
              />

              <span className="text-sm font-semibold text-slate-700">
                {logs.length} Records
              </span>
            </div>

          </div>

          {/* Loading */}
          {loadingLogs && (
            <div className="py-12 text-center text-slate-500">
              <RefreshCw
                className="mx-auto mb-3 animate-spin text-[#8065B5]"
                size={30}
              />

              Loading audit logs...
            </div>
          )}

          {/* No Jobs */}
          {!loadingJobs && jobs.length === 0 && !error && (
            <div className="py-12 text-center">

              <FileText
                size={42}
                className="mx-auto mb-3 text-slate-300"
              />

              <p className="font-semibold text-slate-600">
                No jobs available.
              </p>

              <p className="mt-1 text-sm text-slate-400">
                Create a job to start tracking activities.
              </p>

            </div>
          )}

          {/* Logs Table */}
          {!loadingLogs && selectedJob && (

            <div className="overflow-x-auto">

              <table className="w-full text-left">

                <thead>
                  <tr className="border-b border-[#E5EAF5] text-sm text-slate-500">

                    <th className="p-4">
                      Log ID
                    </th>

                    <th className="p-4">
                      Application
                    </th>

                    <th className="p-4">
                      Action
                    </th>

                    <th className="p-4">
                      Entity
                    </th>

                    <th className="p-4">
                      Actor ID
                    </th>

                    <th className="p-4">
                      Date & Time
                    </th>

                    <th className="p-4">
                      Details
                    </th>

                  </tr>
                </thead>

                <tbody>

                  {logs.length === 0 ? (

                    <tr>
                      <td
                        colSpan={7}
                        className="p-10 text-center text-slate-400"
                      >
                        No audit activities found for this job.
                      </td>
                    </tr>

                  ) : (

                    logs.map((log) => (

                      <tr
                        key={log.log_id}
                        className="border-b border-[#E5EAF5] hover:bg-[#F8F9FC]"
                      >

                        <td className="p-4 font-semibold text-slate-700">
                          #{log.log_id}
                        </td>

                        <td className="p-4 text-slate-600">
                          {log.application_id
                            ? `#${log.application_id}`
                            : "N/A"}
                        </td>

                        <td className="p-4">

                          <span
                            className={`rounded-full px-3 py-1 text-xs font-semibold ${getActionColor(
                              log.action
                            )}`}
                          >
                            {log.action.replaceAll("_", " ")}
                          </span>

                        </td>

                        <td className="p-4 text-slate-600">
                          {log.entity_type}
                          {log.entity_id
                            ? ` #${log.entity_id}`
                            : ""}
                        </td>

                        <td className="p-4 text-slate-600">
                          {log.actor_id ?? "System"}
                        </td>

                        <td className="p-4 text-sm text-slate-500">
                          {formatDate(log.created_at)}
                        </td>

                        <td className="p-4">

                          <details className="max-w-xs">

                            <summary className="cursor-pointer font-semibold text-[#8065B5] hover:underline">
                              View Details
                            </summary>

                            <pre className="mt-2 whitespace-pre-wrap break-words rounded-lg bg-[#E5EAF5] p-3 text-xs text-slate-700">
                              {JSON.stringify(
                                log.details,
                                null,
                                2
                              )}
                            </pre>

                          </details>

                        </td>

                      </tr>

                    ))

                  )}

                </tbody>

              </table>

            </div>

          )}

          {/* Pagination */}
          {!loadingLogs && selectedJob && (

            <div className="mt-6 flex items-center justify-between border-t border-[#E5EAF5] pt-5">

              <p className="text-sm text-slate-500">
                Showing {logs.length} records
              </p>

              <div className="flex items-center gap-3">

                <button
                  onClick={handlePrevious}
                  disabled={offset === 0}
                  className="flex items-center gap-2 rounded-lg border border-[#E5EAF5] px-4 py-2 text-sm font-semibold text-slate-700 hover:bg-[#E5EAF5] disabled:cursor-not-allowed disabled:opacity-40"
                >
                  <ChevronLeft size={18} />
                  Previous
                </button>

                <span className="text-sm font-semibold text-slate-600">
                  Page {Math.floor(offset / PAGE_SIZE) + 1}
                </span>

                <button
                  onClick={handleNext}
                  disabled={logs.length < PAGE_SIZE}
                  className="flex items-center gap-2 rounded-lg border border-[#E5EAF5] px-4 py-2 text-sm font-semibold text-slate-700 hover:bg-[#E5EAF5] disabled:cursor-not-allowed disabled:opacity-40"
                >
                  Next
                  <ChevronRight size={18} />
                </button>

              </div>

            </div>

          )}

        </div>

      </main>

    </div>
  );
}

export default AuditLogs;