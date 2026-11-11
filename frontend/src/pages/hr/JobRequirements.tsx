import { useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { ArrowLeft, Plus, Trash2 } from "lucide-react";

import {
  addJobRequirement,
  updateJobStatus,
} from "./hrService";

type RequirementType = "Skill" | "Education" | "Experience";

interface Requirement {
  requirement_type: RequirementType;
  requirement_value: string;
  is_mandatory: boolean;
  minimum_years: number | null;
}

function getErrorMessage(err: any): string {
  const detail = err.response?.data?.detail;

  if (Array.isArray(detail)) {
    return detail
      .map((item: any) => item.msg)
      .join(", ");
  }

  if (typeof detail === "string") {
    return detail;
  }

  return "Something went wrong. Please try again.";
}

function JobRequirements() {
  const { jobId } = useParams();
  const navigate = useNavigate();

  const [requirements, setRequirements] = useState<Requirement[]>([
    {
      requirement_type: "Skill",
      requirement_value: "",
      is_mandatory: true,
      minimum_years: null,
    },
  ]);

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const [savedCount, setSavedCount] = useState(0);

  const requirementsSaved =
    savedCount === requirements.length && savedCount > 0;

  const updateRequirement = (
    index: number,
    field: keyof Requirement,
    value: string | boolean | number | null
  ) => {
    setRequirements((previous) =>
      previous.map((item, i) =>
        i === index ? { ...item, [field]: value } : item
      )
    );

    setSuccess("");
  };

  const addRequirementField = () => {
    setRequirements((previous) => [
      ...previous,
      {
        requirement_type: "Skill",
        requirement_value: "",
        is_mandatory: true,
        minimum_years: null,
      },
    ]);
  };

  const removeRequirement = (index: number) => {
    setRequirements((previous) =>
      previous.filter((_, i) => i !== index)
    );
  };

  const handleSubmit = async () => {
    if (!jobId) {
      setError("Invalid job ID.");
      return;
    }

    if (
      requirements.some(
        (item) => !item.requirement_value.trim()
      )
    ) {
      setError("Please fill in all requirement values.");
      return;
    }

    setLoading(true);
    setError("");
    setSuccess("");

    try {
      // Start from savedCount to avoid resubmitting
      // requirements that were already saved.
      for (let i = savedCount; i < requirements.length; i++) {
        const item = requirements[i];

        await addJobRequirement(Number(jobId), {
          requirement_type: item.requirement_type,
          requirement_value: item.requirement_value.trim(),
          is_mandatory: item.is_mandatory,

          minimum_years:
            item.requirement_type === "Experience"
              ? item.minimum_years
              : null,
        });

        setSavedCount(i + 1);
      }

      setSuccess("All requirements saved successfully!");

    } catch (err: any) {
      console.error("Requirement Error:", err);
      setError(getErrorMessage(err));

    } finally {
      setLoading(false);
    }
  };

  const handlePublish = async () => {
    if (!jobId || !requirementsSaved) {
      setError("Please save all requirements before publishing.");
      return;
    }

    setLoading(true);
    setError("");

    try {
      await updateJobStatus(Number(jobId), "Open");
      navigate("/hr/dashboard");

    } catch (err: any) {
      console.error("Publish Error:", err);
      setError(getErrorMessage(err));

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

          <h1 className="text-3xl font-bold text-slate-800">
            Job Requirements
          </h1>

          <p className="text-slate-500 mt-2 mb-8">
            Define the skills, education and experience
            required for this job.
          </p>

          <div className="space-y-6">

            {requirements.map((item, index) => (
              <div
                key={index}
                className="border border-[#E5EAF5] rounded-xl p-5"
              >

                <div className="flex justify-between items-center mb-4">

                  <h3 className="font-semibold text-slate-800">
                    Requirement {index + 1}
                  </h3>

                  {requirements.length > 1 && savedCount === 0 && (
                    <button
                      type="button"
                      onClick={() => removeRequirement(index)}
                      className="text-red-500"
                    >
                      <Trash2 size={18} />
                    </button>
                  )}

                </div>

                <label className="block text-sm font-semibold mb-2">
                  Requirement Type
                </label>

                <select
                  value={item.requirement_type}
                  disabled={savedCount > 0}
                  onChange={(e) => {
                    const type = e.target.value as RequirementType;

                    updateRequirement(
                      index,
                      "requirement_type",
                      type
                    );

                    if (type !== "Experience") {
                      updateRequirement(
                        index,
                        "minimum_years",
                        null
                      );
                    }
                  }}
                  className="w-full rounded-xl border border-[#E5EAF5] bg-[#F8F9FC] p-3 mb-4"
                >
                  <option value="Skill">Skill</option>
                  <option value="Education">Education</option>
                  <option value="Experience">Experience</option>
                </select>

                <label className="block text-sm font-semibold mb-2">
                  Requirement Value
                </label>

                <input
                  value={item.requirement_value}
                  disabled={savedCount > 0}
                  onChange={(e) =>
                    updateRequirement(
                      index,
                      "requirement_value",
                      e.target.value
                    )
                  }
                  placeholder="e.g. Python, Machine Learning"
                  className="w-full rounded-xl border border-[#E5EAF5] bg-[#F8F9FC] p-3 mb-4"
                />

                {item.requirement_type === "Experience" && (
                  <>
                    <label className="block text-sm font-semibold mb-2">
                      Minimum Experience (Years)
                    </label>

                    <input
                      type="number"
                      min="0"
                      step="any"
                      value={item.minimum_years ?? ""}
                      disabled={savedCount > 0}
                      onChange={(e) =>
                        updateRequirement(
                          index,
                          "minimum_years",
                          e.target.value === ""
                            ? null
                            : Number(e.target.value)
                        )
                      }
                      placeholder="Optional"
                      className="w-full rounded-xl border border-[#E5EAF5] bg-[#F8F9FC] p-3 mb-4"
                    />
                  </>
                )}

                <label className="flex items-center gap-2 text-sm text-slate-700">
                  <input
                    type="checkbox"
                    checked={item.is_mandatory}
                    disabled={savedCount > 0}
                    onChange={(e) =>
                      updateRequirement(
                        index,
                        "is_mandatory",
                        e.target.checked
                      )
                    }
                  />

                  Mandatory Requirement
                </label>

              </div>
            ))}

            {savedCount === 0 && (
              <button
                type="button"
                onClick={addRequirementField}
                className="flex items-center gap-2 text-[#8065B5] font-semibold"
              >
                <Plus size={18} />
                Add Another Requirement
              </button>
            )}

          </div>

          {error && (
            <p className="mt-5 bg-red-50 text-red-600 p-4 rounded-lg">
              {error}
            </p>
          )}

          {success && (
            <p className="mt-5 bg-green-50 text-green-700 p-4 rounded-lg">
              {success}
            </p>
          )}

          <div className="flex flex-col sm:flex-row gap-4 mt-8">

            <button
              onClick={handleSubmit}
              disabled={loading || requirementsSaved}
              className="flex-1 bg-[#A0D2EB] hover:bg-[#88C3E2] disabled:opacity-50 py-3 rounded-xl font-bold text-slate-800"
            >
              {loading
                ? "Saving..."
                : requirementsSaved
                  ? "Requirements Saved"
                  : savedCount > 0
                    ? "Retry Remaining Requirements"
                    : "Save Requirements"}
            </button>

            <button
              onClick={handlePublish}
              disabled={loading || !requirementsSaved}
              className="flex-1 bg-[#D0BDF4] hover:opacity-80 disabled:opacity-50 py-3 rounded-xl font-bold text-slate-800"
            >
              Publish Job
            </button>

          </div>

        </div>
      </div>
    </div>
  );
}

export default JobRequirements;