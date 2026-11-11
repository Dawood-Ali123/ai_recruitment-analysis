import { useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { Upload, FileText, ArrowLeft, CheckCircle } from "lucide-react";
import {
  applyForJob,
  uploadCandidateCV,
} from "../../services/candidateService";

const ApplyJob = () => {
  const { jobId } = useParams();
  const navigate = useNavigate();

  const [file, setFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const [applicationId, setApplicationId] = useState<number | null>(null);
  const [success, setSuccess] = useState("");
  const [error, setError] = useState("");

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = e.target.files?.[0];

    setError("");
    setSuccess("");

    if (!selectedFile) return;

    const extension = selectedFile.name.split(".").pop()?.toLowerCase();

    if (!["pdf", "docx"].includes(extension || "")) {
      setError("Only PDF and DOCX files are allowed.");
      e.target.value = "";
      setFile(null);
      return;
    }

    if (selectedFile.size > 5 * 1024 * 1024) {
      setError("File size must not exceed 5 MB.");
      e.target.value = "";
      setFile(null);
      return;
    }

    setFile(selectedFile);
  };

  const handleApplication = async () => {
    if (!jobId || !file) {
      setError("Please select your CV before applying.");
      return;
    }

    setLoading(true);
    setError("");
    setSuccess("");

    try {
      let currentApplicationId = applicationId;

      // Step 1: Create application
      if (!currentApplicationId) {
        const application = await applyForJob(Number(jobId));

        currentApplicationId = application.application_id;
        setApplicationId(currentApplicationId);
      }

      // Step 2: Upload CV
      if (currentApplicationId === null) {
  throw new Error("Application ID is missing.");
}

await uploadCandidateCV(currentApplicationId, file);

      setSuccess("Application submitted and CV uploaded successfully!");

      setTimeout(() => {
        navigate("/candidate/dashboard");
      }, 2000);

    } catch (err: any) {
      console.error("Application Error:", err);

      setError(
        err.response?.data?.detail ||
        "Application failed. Please try again."
      );

    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#E5EAF5] p-6 md:p-10">

      <div className="max-w-3xl mx-auto">

        <button
          onClick={() => navigate(`/candidate/jobs/${jobId}`)}
          className="flex items-center gap-2 text-slate-700 mb-8"
        >
          <ArrowLeft size={20} />
          Back to Job Details
        </button>

        <div className="bg-white rounded-2xl shadow-sm p-8">

          <h1 className="text-3xl font-bold text-slate-800">
            Submit Your Application
          </h1>

          <p className="text-slate-500 mt-2">
            Upload your latest CV to apply for this position.
          </p>

          <div className="mt-8">

            <label className="block text-sm font-semibold text-slate-700 mb-3">
              Upload Your CV
            </label>

            <div className="border-2 border-dashed border-[#A0D2EB] rounded-xl p-8 text-center bg-[#F8F9FC]">

              <Upload
                size={40}
                className="mx-auto text-[#8065B5] mb-4"
              />

              <p className="font-semibold text-slate-700">
                Select your CV
              </p>

              <p className="text-sm text-slate-500 mt-2">
                PDF or DOCX (Maximum 5 MB)
              </p>

              <input
                type="file"
                accept=".pdf,.docx"
                onChange={handleFileChange}
                className="mt-5 block w-full text-sm text-slate-600 file:mr-4 file:rounded-lg file:border-0 file:bg-[#A0D2EB] file:px-4 file:py-2 file:font-semibold file:text-slate-800"
              />

            </div>

            {file && (
              <div className="mt-4 flex items-center gap-3 bg-[#E5EAF5] p-4 rounded-lg">

                <FileText className="text-[#8065B5]" />

                <div>
                  <p className="font-semibold text-slate-800">
                    {file.name}
                  </p>

                  <p className="text-sm text-slate-500">
                    {(file.size / 1024).toFixed(2)} KB
                  </p>
                </div>

              </div>
            )}

          </div>

          {error && (
            <div className="mt-5 bg-red-50 text-red-600 p-4 rounded-lg">
              {error}
            </div>
          )}

          {success && (
            <div className="mt-5 bg-green-50 text-green-700 p-4 rounded-lg flex items-center gap-2">
              <CheckCircle size={20} />
              {success}
            </div>
          )}

          <button
            onClick={handleApplication}
            disabled={loading || !file}
            className="mt-8 w-full bg-[#A0D2EB] hover:bg-[#88C3E2] disabled:opacity-50 text-slate-800 font-bold py-4 rounded-xl"
          >
            {loading
              ? "Submitting Application..."
              : applicationId
                ? "Retry CV Upload"
                : "Submit Application"}
          </button>

        </div>

      </div>

    </div>
  );
};

export default ApplyJob;