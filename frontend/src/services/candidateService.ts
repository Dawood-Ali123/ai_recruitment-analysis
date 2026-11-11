import api from "./api";

// Fetch all available jobs
export const getAvailableJobs = async () => {
  const response = await api.get("/jobs/");
  return response.data;
};

// Fetch logged-in candidate's applications
export const getMyApplications = async () => {
  const response = await api.get("/applications/");
  return response.data;
};
// Fetch details of a specific job
export const getJobDetails = async (jobId: number) => {
  const response = await api.get(`/jobs/${jobId}`);
  return response.data;
};

// Submit job application
export const applyForJob = async (jobId: number) => {
  const response = await api.post("/applications/", {
    job_id: jobId,
  });

  return response.data;
};

// Upload candidate CV
export const uploadCandidateCV = async (
  applicationId: number,
  file: File
) => {
  const formData = new FormData();

  formData.append("file", file);

  const response = await api.post(
    `/applications/${applicationId}/upload-cv`,
    formData,
    {
      headers: {
        "Content-Type": "multipart/form-data",
      },
    }
  );

  return response.data;
};
export const getMyApplicationTracking = async () => {
  const response = await api.get("/applications/my-tracking");
  return response.data;
};