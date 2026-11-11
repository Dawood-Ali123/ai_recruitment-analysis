import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";

import {
  ArrowLeft,
  User,
  Briefcase,
  FileText,
  Brain,
  CheckCircle,
  Mail,
  Loader2,
  RefreshCw,
  Clock,
  Eye,
  Download,
  Target,
  Award,
  BriefcaseBusiness,
  AlertCircle,
  BookOpen,
} from "lucide-react";

import {
  getApplicationDetails,
  getApplicationEvaluation,
  processCandidateCV,
  evaluateCandidate,
  submitHRDecision,
  getApplicationEmails,
  previewCandidateCV,
  downloadCandidateCV,
} from "./hrService";

function HRApplicationDetails() {
  const { applicationId } = useParams();
  const navigate = useNavigate();

  const [application, setApplication] = useState<any>(null);
  const [evaluation, setEvaluation] = useState<any>(null);

  const [loading, setLoading] = useState(true);
  const [processing, setProcessing] = useState(false);
  const [evaluating, setEvaluating] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [cvLoading, setCvLoading] = useState(false);

  const [emailHistory, setEmailHistory] = useState<any[]>([]);
  const [emailLoading, setEmailLoading] = useState(false);

  const [decision, setDecision] = useState<
    "Shortlisted" | "Rejected" | "Request Information"
  >("Shortlisted");

  const [notes, setNotes] = useState("");
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  const id = Number(applicationId);

  // Load application details
  const loadApplication = async () => {
    try {
      setLoading(true);
      setError("");

      const data = await getApplicationDetails(id);
      setApplication(data);

      if (data.cv) {
        try {
          const report = await getApplicationEvaluation(id);
          setEvaluation(report);
        } catch {
          setEvaluation(null);
        }
      } else {
        setEvaluation(null);
      }
    } catch (err: any) {
      console.error(err);

      setError(
        err.response?.data?.detail ||
          "Unable to load application details."
      );
    } finally {
      setLoading(false);
    }
  };

  // Load email history
  const loadEmailHistory = async () => {
    try {
      setEmailLoading(true);

      const data = await getApplicationEmails(id);
      setEmailHistory(data);
    } catch (err) {
      console.error("Email History Error:", err);
    } finally {
      setEmailLoading(false);
    }
  };

  // Initial page loading
  useEffect(() => {
    if (Number.isNaN(id) || id <= 0) {
      setError("Invalid application ID.");
      setLoading(false);
      return;
    }

    loadApplication();
    loadEmailHistory();
  }, [id]);

  // Preview CV
  const handlePreviewCV = async () => {
    const previewWindow = window.open("", "_blank");

    if (!previewWindow) {
      setError("Please allow pop-ups to preview the CV.");
      return;
    }

    try {
      setCvLoading(true);
      setError("");

      const blob = await previewCandidateCV(id);

      if (application.cv.mime_type !== "application/pdf") {
        previewWindow.close();

        setError(
          "Preview is available for PDF files only. Please download the DOCX file."
        );
        return;
      }

      const fileBlob = new Blob([blob], {
        type: "application/pdf",
      });

      const fileURL = URL.createObjectURL(fileBlob);

      previewWindow.location.href = fileURL;

      // Release browser memory after a delay
      setTimeout(() => {
        URL.revokeObjectURL(fileURL);
      }, 60000);

    } catch (err: any) {
      previewWindow.close();

      console.error("CV Preview Error:", err);

      setError("Unable to preview CV. Please try again.");
    } finally {
      setCvLoading(false);
    }
  };

  // Download CV
  const handleDownloadCV = async () => {
    try {
      setCvLoading(true);
      setError("");

      const blob = await downloadCandidateCV(id);

      const fileBlob = new Blob([blob], {
        type: application.cv.mime_type,
      });

      const fileURL = URL.createObjectURL(fileBlob);

      const link = document.createElement("a");

      link.href = fileURL;
      link.download = application.cv.filename;

      document.body.appendChild(link);
      link.click();
      link.remove();

      setTimeout(() => {
        URL.revokeObjectURL(fileURL);
      }, 1000);

    } catch (err: any) {
      console.error("CV Download Error:", err);

      setError("Unable to download CV. Please try again.");
    } finally {
      setCvLoading(false);
    }
  };

  // Process CV
  const handleProcessCV = async () => {
    try {
      setProcessing(true);
      setError("");
      setSuccess("");

      await processCandidateCV(id);

      setSuccess("CV processed successfully!");

      await loadApplication();
    } catch (err: any) {
      setError(
        err.response?.data?.detail ||
          "CV processing failed."
      );
    } finally {
      setProcessing(false);
    }
  };

  // AI Evaluation
  const handleEvaluate = async () => {
    try {
      setEvaluating(true);
      setError("");
      setSuccess("");

      await evaluateCandidate(id);

      const report = await getApplicationEvaluation(id);

      setEvaluation(report);

      setSuccess("AI evaluation completed successfully!");
    } catch (err: any) {
      setError(
        err.response?.data?.detail ||
          "AI evaluation failed."
      );
    } finally {
      setEvaluating(false);
    }
  };

  // HR Final Decision
  const handleDecision = async () => {
    try {
      setSubmitting(true);
      setError("");
      setSuccess("");

      await submitHRDecision(id, {
        decision,
        notes: notes.trim() || undefined,
      });

      setSuccess(
        `Decision submitted successfully: ${decision}`
      );

      await loadEmailHistory();
    } catch (err: any) {
      setError(
        err.response?.data?.detail ||
          "Unable to submit HR decision."
      );
    } finally {
      setSubmitting(false);
    }
  };

  // Loading screen
  if (loading) {
    return (
      <div className="min-h-screen bg-[#E5EAF5] flex items-center justify-center">
        <Loader2
          className="animate-spin text-[#8065B5]"
          size={35}
        />
      </div>
    );
  }

  // Application not found
  if (!application) {
    return (
      <div className="min-h-screen bg-[#E5EAF5] p-10">
        <p className="text-red-600">
          {error || "Application not found."}
        </p>

        <button
          onClick={() => navigate("/hr/dashboard")}
          className="mt-5 text-[#8065B5]"
        >
          Back to Dashboard
        </button>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[#E5EAF5] p-6 md:p-10">
      <div className="max-w-6xl mx-auto">

        {/* Back Button */}
        <button
          onClick={() => navigate("/hr/dashboard")}
          className="flex items-center gap-2 text-slate-700 mb-8"
        >
          <ArrowLeft size={20} />
          Back to Dashboard
        </button>

        <h1 className="text-3xl font-bold text-slate-800">
          Application Details
        </h1>

        <p className="text-slate-500 mt-2 mb-8">
          Review candidate information and AI evaluation.
        </p>

        {/* Error Message */}
        {error && (
          <div className="bg-red-50 text-red-600 p-4 rounded-xl mb-5">
            {error}
          </div>
        )}

        {/* Success Message */}
        {success && (
          <div className="bg-green-50 text-green-700 p-4 rounded-xl mb-5">
            {success}
          </div>
        )}

        {/* Information Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">

          {/* Candidate Information */}
          <div className="bg-white rounded-2xl p-6 shadow-sm">

            <div className="flex items-center gap-3 mb-5">
              <User className="text-[#8065B5]" size={25} />

              <h2 className="text-xl font-bold text-slate-800">
                Candidate Information
              </h2>
            </div>

            <p className="text-slate-500 text-sm">
              Full Name
            </p>

            <p className="font-semibold text-slate-800 mb-4">
              {application.candidate.full_name}
            </p>

            <p className="text-slate-500 text-sm">
              Email
            </p>

            <p className="font-semibold text-slate-800 mb-4">
              {application.candidate.email}
            </p>

            <p className="text-slate-500 text-sm">
              Application ID
            </p>

            <p className="font-semibold text-slate-800 mb-4">
              #{application.application_id}
            </p>

            <p className="text-slate-500 text-sm">
              Application Status
            </p>

            <span className="inline-block mt-1 bg-[#E5EAF5] text-[#8065B5] px-4 py-2 rounded-full text-sm font-semibold">
              {application.status}
            </span>

          </div>

          {/* Job Information */}
          <div className="bg-white rounded-2xl p-6 shadow-sm">

            <div className="flex items-center gap-3 mb-5">
              <Briefcase className="text-[#8065B5]" size={25} />

              <h2 className="text-xl font-bold text-slate-800">
                Job Information
              </h2>
            </div>

            <p className="text-slate-500 text-sm">
              Position
            </p>

            <p className="font-semibold text-slate-800 mb-4">
              {application.job.title}
            </p>

            <p className="text-slate-500 text-sm">
              Description
            </p>

            <p className="text-slate-700 leading-relaxed">
              {application.job.description}
            </p>

          </div>

          {/* CV Information */}
          <div className="bg-white rounded-2xl p-6 shadow-sm">

            <div className="flex items-center gap-3 mb-5">
              <FileText className="text-[#8065B5]" size={25} />

              <h2 className="text-xl font-bold text-slate-800">
                Candidate CV
              </h2>
            </div>

            {application.cv ? (
              <>

                <p className="font-semibold text-slate-800 mb-2">
                  {application.cv.filename}
                </p>

                <p className="text-slate-500 text-sm mb-5">
                  Version: {application.cv.version}
                </p>

                {/* Preview and Download */}
                <div className="grid grid-cols-2 gap-3 mb-5">

                  {application.cv.mime_type ===
                    "application/pdf" && (
                    <button
                      onClick={handlePreviewCV}
                      disabled={cvLoading}
                      className="flex items-center justify-center gap-2 bg-[#D0BDF4] hover:opacity-80 disabled:opacity-50 py-3 rounded-xl font-semibold text-slate-800"
                    >
                      {cvLoading ? (
                        <Loader2
                          className="animate-spin"
                          size={18}
                        />
                      ) : (
                        <Eye size={18} />
                      )}

                      Preview CV
                    </button>
                  )}

                  <button
                    onClick={handleDownloadCV}
                    disabled={cvLoading}
                    className="flex items-center justify-center gap-2 bg-[#A0D2EB] hover:bg-[#88C3E2] disabled:opacity-50 py-3 rounded-xl font-semibold text-slate-800"
                  >
                    {cvLoading ? (
                      <Loader2
                        className="animate-spin"
                        size={18}
                      />
                    ) : (
                      <Download size={18} />
                    )}

                    Download CV
                  </button>

                </div>

                {/* Process CV */}
                <button
                  onClick={handleProcessCV}
                  disabled={processing}
                  className="w-full bg-[#A0D2EB] hover:bg-[#88C3E2] disabled:opacity-50 py-3 rounded-xl font-bold text-slate-800 flex justify-center items-center gap-2"
                >
                  {processing ? (
                    <Loader2
                      className="animate-spin"
                      size={18}
                    />
                  ) : (
                    <FileText size={18} />
                  )}

                  {processing
                    ? "Processing CV..."
                    : "Process CV"}
                </button>

              </>
            ) : (
              <p className="text-red-500">
                No CV uploaded for this application.
              </p>
            )}

          </div>

        </div>

        {/* AI Evaluation */}
        <div className="bg-white rounded-2xl p-6 shadow-sm">

          <div className="flex items-center gap-3 mb-5">
            <Brain className="text-[#8065B5]" size={25} />

            <h2 className="text-xl font-bold text-slate-800">
              AI Evaluation Report
            </h2>
          </div>

          <button
            onClick={handleEvaluate}
            disabled={
              evaluating ||
              !application.cv ||
              evaluation?.processing_status === "Completed"
            }
            className="w-full bg-[#D0BDF4] hover:opacity-80 disabled:opacity-50 py-3 rounded-xl font-bold text-slate-800 flex justify-center items-center gap-2"
          >
            {evaluating && (
              <Loader2 className="animate-spin" size={18} />
            )}

            {evaluating
              ? "Evaluating..."
              : evaluation?.processing_status === "Completed"
                ? "Evaluation Completed"
                : "Evaluate with AI"}
          </button>

          {evaluation?.processing_status === "Completed" && (() => {

            const report = evaluation.report || {};

            const recommendationColor =
              report.recommendation === "Strong Match"
                ? "bg-green-100 text-green-700"
                : report.recommendation === "Partial Match"
                  ? "bg-yellow-100 text-yellow-700"
                  : "bg-red-100 text-red-700";

            return (
              <div className="mt-6 space-y-5">

                {/* Score */}
                <div className="bg-[#F8F9FC] rounded-xl p-5">

                  <div className="flex justify-between items-center mb-3">
                    <p className="font-semibold text-slate-700">
                      Overall Match Score
                    </p>

                    <Target className="text-[#8065B5]" />
                  </div>

                  <h3 className="text-4xl font-bold text-[#8065B5]">
                    {evaluation.score ?? report.score ?? 0}%
                  </h3>

                  <div className="w-full bg-slate-200 rounded-full h-3 mt-4">
                    <div
                      className="bg-[#8065B5] h-3 rounded-full"
                      style={{
                        width: `${Math.min(
                          100,
                          Math.max(0, Number(evaluation.score ?? report.score ?? 0))
                        )}%`,
                      }}
                    />
                  </div>

                </div>

                {/* Recommendation */}
                <div className="border border-[#E5EAF5] rounded-xl p-5">

                  <div className="flex items-center gap-2 mb-3">
                    <Award className="text-[#8065B5]" />

                    <h3 className="font-bold text-slate-800">
                      AI Recommendation
                    </h3>
                  </div>

                  <span className={`inline-block px-4 py-2 rounded-full font-semibold text-sm ${recommendationColor}`}>
                    {report.recommendation || "Not Available"}
                  </span>

                </div>

                {/* Skills Matching */}
                <div className="border border-[#E5EAF5] rounded-xl p-5">

                  <h3 className="font-bold text-slate-800 mb-3">
                    Skills Matching
                  </h3>

                  {report.skills_matching?.length > 0 ? (
                    <div className="flex flex-wrap gap-2">
                      {report.skills_matching.map(
                        (skill: string, index: number) => (
                          <span
                            key={index}
                            className="bg-green-100 text-green-700 px-3 py-2 rounded-lg text-sm"
                          >
                            ✓ {skill}
                          </span>
                        )
                      )}
                    </div>
                  ) : (
                    <p className="text-slate-500 text-sm">
                      No matching skills listed.
                    </p>
                  )}

                </div>

                {/* Experience */}
                <div className="border border-[#E5EAF5] rounded-xl p-5">

                  <h3 className="font-bold text-slate-800 mb-3 flex items-center gap-2">
                    <BriefcaseBusiness size={19} />
                    Experience Assessment
                  </h3>

                  <p className="text-slate-600 leading-relaxed">
                    {report.experience_matching || "Not available"}
                  </p>

                </div>

                {/* Missing Requirements */}
                <div className="border border-[#E5EAF5] rounded-xl p-5">

                  <h3 className="font-bold text-slate-800 mb-3 flex items-center gap-2">
                    <AlertCircle size={19} />
                    Missing Requirements
                  </h3>

                  {report.missing_requirements?.length > 0 ? (
                    <ul className="space-y-2">
                      {report.missing_requirements.map(
                        (item: string, index: number) => (
                          <li
                            key={index}
                            className="text-slate-600 text-sm flex gap-2"
                          >
                            <span className="text-amber-600">•</span>
                            {item}
                          </li>
                        )
                      )}
                    </ul>
                  ) : (
                    <p className="text-green-700 text-sm">
                      No missing requirements reported.
                    </p>
                  )}

                </div>

                {/* Evidence */}
                <div className="border border-[#E5EAF5] rounded-xl p-5">

                  <h3 className="font-bold text-slate-800 mb-3 flex items-center gap-2">
                    <BookOpen size={19} />
                    Supporting Evidence
                  </h3>

                  {report.evidence?.length > 0 ? (
                    <ul className="space-y-2">
                      {report.evidence.map(
                        (item: string, index: number) => (
                          <li
                            key={index}
                            className="bg-[#F8F9FC] p-3 rounded-lg text-sm text-slate-600"
                          >
                            {item}
                          </li>
                        )
                      )}
                    </ul>
                  ) : (
                    <p className="text-slate-500 text-sm">
                      No supporting evidence provided.
                    </p>
                  )}

                </div>

                {/* Explanation */}
                <div className="border border-[#E5EAF5] rounded-xl p-5">

                  <h3 className="font-bold text-slate-800 mb-3">
                    AI Explanation
                  </h3>

                  <p className="text-slate-600 leading-relaxed">
                    {report.explanation || "No explanation available."}
                  </p>

                </div>

                <p className="text-xs text-slate-400">
                  AI provides an assessment only. Final hiring decisions
                  remain the responsibility of HR.
                </p>

              </div>
            );

          })()}

        </div>

        {/* HR Final Decision */}
        <div className="bg-white rounded-2xl p-6 shadow-sm mt-6">

          <div className="flex items-center gap-3 mb-5">
            <CheckCircle
              className="text-[#8065B5]"
              size={25}
            />

            <h2 className="text-xl font-bold text-slate-800">
              HR Final Decision
            </h2>
          </div>

          <p className="text-slate-500 mb-5">
            AI provides recommendations. The final hiring decision
            belongs to HR.
          </p>

          <label className="block text-sm font-semibold mb-2">
            Select Decision
          </label>

          <select
            value={decision}
            onChange={(e) =>
              setDecision(
                e.target.value as
                  | "Shortlisted"
                  | "Rejected"
                  | "Request Information"
              )
            }
            className="w-full border border-[#E5EAF5] bg-[#F8F9FC] p-3 rounded-xl mb-5"
          >
            <option value="Shortlisted">
              Shortlisted
            </option>

            <option value="Rejected">
              Rejected
            </option>

            <option value="Request Information">
              Request Information
            </option>
          </select>

          <label className="block text-sm font-semibold mb-2">
            HR Notes
          </label>

          <textarea
            value={notes}
            onChange={(e) => setNotes(e.target.value)}
            placeholder="Enter additional comments..."
            rows={4}
            className="w-full border border-[#E5EAF5] bg-[#F8F9FC] p-3 rounded-xl mb-5"
          />

          <button
            onClick={handleDecision}
            disabled={
              submitting ||
              evaluation?.processing_status !== "Completed"
            }
            className="w-full bg-[#A0D2EB] hover:bg-[#88C3E2] disabled:opacity-50 py-3 rounded-xl font-bold text-slate-800 flex justify-center items-center gap-2"
          >
            {submitting ? (
              <Loader2
                className="animate-spin"
                size={18}
              />
            ) : (
              <Mail size={18} />
            )}

            {submitting
              ? "Submitting Decision..."
              : "Submit HR Decision & Send Email"}
          </button>

          {evaluation?.processing_status !== "Completed" && (
            <p className="text-sm text-amber-600 mt-3">
              Complete AI evaluation before submitting the HR decision.
            </p>
          )}

        </div>

        {/* Email History */}
        <div className="bg-white rounded-2xl p-6 shadow-sm mt-6">

          <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 mb-6">

            <div className="flex items-center gap-3">
              <Mail
                className="text-[#8065B5]"
                size={25}
              />

              <h2 className="text-xl font-bold text-slate-800">
                Email History
              </h2>
            </div>

            <button
              onClick={loadEmailHistory}
              disabled={emailLoading}
              className="flex items-center justify-center gap-2 bg-[#E5EAF5] hover:bg-[#D0BDF4] px-4 py-2 rounded-xl text-slate-700 font-semibold disabled:opacity-50"
            >
              <RefreshCw
                size={17}
                className={emailLoading ? "animate-spin" : ""}
              />

              Refresh
            </button>

          </div>

          {emailLoading ? (
            <div className="flex justify-center py-8">
              <Loader2
                className="animate-spin text-[#8065B5]"
                size={30}
              />
            </div>
          ) : emailHistory.length === 0 ? (
            <div className="text-center py-8 bg-[#F8F9FC] rounded-xl">
              <Mail
                size={35}
                className="mx-auto text-slate-400 mb-3"
              />

              <p className="text-slate-500">
                No email history available.
              </p>
            </div>
          ) : (
            <div className="space-y-4">

              {emailHistory.map((email) => {

                const statusColor =
                  email.delivery_status === "Sent"
                    ? "bg-green-100 text-green-700"
                    : email.delivery_status === "Failed"
                      ? "bg-red-100 text-red-700"
                      : "bg-yellow-100 text-yellow-700";

                return (
                  <div
                    key={email.email_id}
                    className="border border-[#E5EAF5] rounded-xl p-5"
                  >

                    <div className="flex flex-col sm:flex-row sm:justify-between sm:items-center gap-3">

                      <div>
                        <p className="font-bold text-slate-800">
                          {email.email_type}
                        </p>

                        <p className="text-sm text-slate-500 mt-1">
                          To: {email.recipient_email}
                        </p>
                      </div>

                      <span
                        className={`px-4 py-2 rounded-full text-sm font-semibold w-fit ${statusColor}`}
                      >
                        {email.delivery_status}
                      </span>

                    </div>

                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 mt-5 text-sm">

                      <p className="text-slate-600 flex items-center gap-2">
                        <RefreshCw size={15} />
                        Retry Count: {email.retry_count}
                      </p>

                      <p className="text-slate-600 flex items-center gap-2">
                        <Clock size={15} />
                        Created:{" "}
                        {email.created_at
                          ? new Date(email.created_at).toLocaleString()
                          : "N/A"}
                      </p>

                      <p className="text-slate-600 flex items-center gap-2">
                        <CheckCircle size={15} />
                        Sent At:{" "}
                        {email.sent_at
                          ? new Date(email.sent_at).toLocaleString()
                          : "Not sent yet"}
                      </p>

                    </div>

                  </div>
                );
              })}

            </div>
          )}

        </div>

      </div>
    </div>
  );
}

export default HRApplicationDetails;