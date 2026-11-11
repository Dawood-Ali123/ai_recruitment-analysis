import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import {
  ArrowLeft,
  Briefcase,
  MapPin,
  CheckCircle2,
  Clock,
  GraduationCap,
} from "lucide-react";

import { getJobDetails } from "../../services/candidateService";

interface Requirement {
  requirement_id: number;
  requirement_type: string;
  requirement_value: string;
  is_mandatory: boolean;
  minimum_years?: string | null;
}

interface Job {
  job_id: number;
  title: string;
  description?: string;
  location?: string;
  experience_required?: number;
  requirements?: Requirement[];
}

export default function JobDetails() {
  const { jobId } = useParams();
  const navigate = useNavigate();

  const [job, setJob] = useState<Job | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    const fetchJob = async () => {
      try {
        if (!jobId) {
          setError("Invalid job ID.");
          return;
        }

        const data = await getJobDetails(Number(jobId));
        setJob(data);

      } catch (err) {
        console.error(err);
        setError("Unable to load job details.");

      } finally {
        setLoading(false);
      }
    };

    fetchJob();
  }, [jobId]);

  const skillRequirements =
    job?.requirements?.filter(
      (req) => req.requirement_type?.toLowerCase() === "skill"
    ) || [];

  const experienceRequirements =
    job?.requirements?.filter(
      (req) => req.requirement_type?.toLowerCase() === "experience"
    ) || [];

  const otherRequirements =
    job?.requirements?.filter(
      (req) =>
        !["skill", "experience"].includes(
          req.requirement_type?.toLowerCase()
        )
    ) || [];

  return (
    <div className="min-h-screen bg-[#E5EAF5] p-6 md:p-10">

      <div className="max-w-4xl mx-auto">

        {/* Back Button */}

        <button
          onClick={() => navigate("/candidate/dashboard")}
          className="flex items-center gap-2 text-slate-700 mb-8 hover:text-[#8065B5]"
        >
          <ArrowLeft size={20} />
          Back to Dashboard
        </button>

        {loading ? (

          <p className="text-slate-600">
            Loading job details...
          </p>

        ) : error ? (

          <p className="text-red-600">{error}</p>

        ) : job ? (

          <div className="bg-white rounded-2xl shadow-sm p-6 md:p-8">

            {/* Job Header */}

            <div className="flex items-center gap-4 mb-6">

              <div className="bg-[#A0D2EB] p-4 rounded-xl">
                <Briefcase size={28} />
              </div>

              <h1 className="text-2xl md:text-3xl font-bold text-slate-800">
                {job.title}
              </h1>

            </div>

            {/* Location */}

            {job.location && (
              <p className="flex items-center gap-2 text-slate-500 mb-6">
                <MapPin size={18} />
                {job.location}
              </p>
            )}

            {/* Job Description */}

            <section className="mb-8">

              <h2 className="text-xl font-semibold mb-3 text-slate-800">
                Job Description
              </h2>

              <p className="text-slate-600 whitespace-pre-line leading-relaxed">
                {job.description || "No description available."}
              </p>

            </section>

            {/* Experience Requirements */}

            {experienceRequirements.length > 0 && (

              <section className="mb-8">

                <h2 className="text-xl font-semibold mb-4 text-slate-800 flex items-center gap-2">
                  <Clock size={21} className="text-[#8065B5]" />
                  Experience Requirements
                </h2>

                <div className="space-y-3">

                  {experienceRequirements.map((req) => (

                    <div
                      key={req.requirement_id}
                      className="rounded-xl border border-[#D0BDF4] bg-[#F8F6FD] p-4"
                    >

                      <div className="flex justify-between items-start gap-3">

                        <div>

                          <p className="font-semibold text-slate-800">
                            {req.requirement_value}
                          </p>

                          {req.minimum_years && (
                            <p className="mt-2 text-sm text-slate-600">
                              Minimum {req.minimum_years} years of experience
                            </p>
                          )}

                        </div>

                        {req.is_mandatory && (
                          <span className="text-xs font-semibold bg-purple-100 text-[#8065B5] px-3 py-1 rounded-full">
                            Required
                          </span>
                        )}

                      </div>

                    </div>

                  ))}

                </div>

              </section>

            )}

            {/* Skills */}

            <section className="mb-8">

              <h2 className="text-xl font-semibold mb-4 text-slate-800 flex items-center gap-2">
                <GraduationCap size={22} className="text-[#8065B5]" />
                Required Skills
              </h2>

              {skillRequirements.length > 0 ? (

                <div className="flex flex-wrap gap-3">

                  {skillRequirements.map((req) => (

                    <div
                      key={req.requirement_id}
                      className="flex items-center gap-2 rounded-xl bg-[#E5EAF5] border border-[#A0D2EB] px-4 py-3"
                    >

                      <CheckCircle2
                        size={17}
                        className="text-[#8065B5]"
                      />

                      <span className="font-semibold text-slate-800">
                        {req.requirement_value}
                      </span>

                      {req.is_mandatory && (
                        <span className="text-xs text-[#8065B5]">
                          *
                        </span>
                      )}

                    </div>

                  ))}

                </div>

              ) : (

                <p className="text-slate-500">
                  No specific skills listed.
                </p>

              )}

            </section>

            {/* Other Requirements */}

            {otherRequirements.length > 0 && (

              <section className="mb-8">

                <h2 className="text-xl font-semibold mb-4 text-slate-800">
                  Other Requirements
                </h2>

                <div className="space-y-3">

                  {otherRequirements.map((req) => (

                    <div
                      key={req.requirement_id}
                      className="bg-[#E5EAF5] rounded-xl p-4"
                    >

                      <p className="font-semibold text-slate-800">
                        {req.requirement_value}
                      </p>

                      <span className="text-sm text-[#8065B5]">
                        {req.requirement_type}
                      </span>

                    </div>

                  ))}

                </div>

              </section>

            )}

            {/* Apply Button */}

            <button
              type="button"
              onClick={() =>
                navigate(`/candidate/jobs/${job.job_id}/apply`)
              }
              className="bg-[#A0D2EB] hover:bg-[#88C3E2] text-slate-800 font-bold px-8 py-3 rounded-xl transition"
            >
              Apply Now
            </button>

          </div>

        ) : (

          <p className="text-slate-500">
            Job not found.
          </p>

        )}

      </div>

    </div>
  );
}