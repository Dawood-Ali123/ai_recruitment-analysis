import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { ArrowLeft, BriefcaseBusiness } from "lucide-react";
import { createJob } from "./hrService";

function CreateJob() {
  const navigate = useNavigate();

  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    setLoading(true);
    setError("");

    try {
      const newJob = await createJob({
        title: title.trim(),
        description: description.trim(),
      });

      // Open requirements page using newly created job ID
      navigate(`/hr/jobs/${newJob.job_id}/requirements`);

    } catch (err: any) {
      console.error("Create Job Error:", err);

      setError(
        err.response?.data?.detail ||
        "Unable to create job. Please try again."
      );

    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#E5EAF5] p-6 md:p-10">

      <div className="max-w-3xl mx-auto">

        <button
          onClick={() => navigate("/hr/dashboard")}
          className="flex items-center gap-2 text-slate-700 mb-8"
        >
          <ArrowLeft size={20} />
          Back to Dashboard
        </button>

        <div className="bg-white rounded-2xl shadow-sm p-8">

          <div className="flex items-center gap-4 mb-8">

            <div className="bg-[#A0D2EB] p-3 rounded-xl">
              <BriefcaseBusiness size={28} />
            </div>

            <div>
              <h1 className="text-3xl font-bold text-slate-800">
                Create New Job
              </h1>

              <p className="text-slate-500 mt-1">
                Add a new job opportunity.
              </p>
            </div>

          </div>

          <form onSubmit={handleSubmit} className="space-y-6">

            <div>
              <label className="block text-sm font-semibold text-slate-700 mb-2">
                Job Title
              </label>

              <input
                type="text"
                required
                maxLength={200}
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                placeholder="e.g. Machine Learning Engineer"
                className="w-full rounded-xl border border-[#E5EAF5] bg-[#F8F9FC] px-4 py-3 outline-none focus:border-[#A0D2EB]"
              />
            </div>

            <div>
              <label className="block text-sm font-semibold text-slate-700 mb-2">
                Job Description
              </label>

              <textarea
                required
                rows={7}
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                placeholder="Describe the job responsibilities and expectations..."
                className="w-full rounded-xl border border-[#E5EAF5] bg-[#F8F9FC] px-4 py-3 outline-none focus:border-[#A0D2EB] resize-none"
              />
            </div>

            {error && (
              <div className="bg-red-50 text-red-600 p-4 rounded-lg">
                {error}
              </div>
            )}

            <button
              type="submit"
              disabled={loading || !title.trim() || !description.trim()}
              className="w-full rounded-xl bg-[#A0D2EB] hover:bg-[#88C3E2] disabled:opacity-50 py-3.5 font-bold text-slate-800"
            >
              {loading ? "Creating Job..." : "Create Job & Add Requirements"}
            </button>

          </form>

        </div>

      </div>

    </div>
  );
}

export default CreateJob;