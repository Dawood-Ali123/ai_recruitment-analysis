import api from "../../services/api";

// Fetch jobs created by or assigned to HR
export const getHRJobs = async () => {
  const response = await api.get("/jobs/my-jobs");
  return response.data;
};

// Fetch applications for a specific job
export const getJobApplications = async (jobId: number) => {
  const response = await api.get(
    `/applications/jobs/${jobId}/applications`
  );

  return response.data;
};

// Process candidate CV
export const processCandidateCV = async (applicationId: number) => {
  const response = await api.post(
    `/applications/${applicationId}/process-cv`
  );

  return response.data;
};

// Evaluate candidate using AI
export const evaluateCandidate = async (applicationId: number) => {
  const response = await api.post(
    `/applications/${applicationId}/evaluate`
  );

  return response.data;
};

// Create a new job
export const createJob = async (jobData: {
  title: string;
  description: string;
}) => {
  const response = await api.post("/jobs/", jobData);
  return response.data;
};

// Add requirements to a job
export const addJobRequirement = async (
  jobId: number,
  requirementData: {
    requirement_type: "Skill" | "Education" | "Experience";
    requirement_value: string;
    is_mandatory: boolean;
    minimum_years: number | null;
  }
) => {
  const response = await api.post(
    `/jobs/${jobId}/requirements`,
    requirementData
  );

  return response.data;
};

// Update job status
export const updateJobStatus = async (
  jobId: number,
  status: "Draft" | "Open" | "Closed"
) => {
  const response = await api.patch(
    `/jobs/${jobId}/status`,
    { status }
  );

  return response.data;
};

// Fetch complete application details
export const getApplicationDetails = async (
  applicationId: number
) => {
  const response = await api.get(
    `/applications/${applicationId}/details`
  );

  return response.data;
};

// Fetch AI evaluation report
export const getApplicationEvaluation = async (
  applicationId: number
) => {
  const response = await api.get(
    `/applications/${applicationId}/evaluation`
  );

  return response.data;
};

// Submit final HR decision
export const submitHRDecision = async (
  applicationId: number,
  decisionData: {
    decision: "Shortlisted" | "Rejected" | "Request Information";
    notes?: string;
  }
) => {
  const response = await api.post(
    `/applications/${applicationId}/decision`,
    decisionData
  );

  return response.data;
};

// Fetch email history for an application
export const getApplicationEmails = async (
  applicationId: number
) => {
  const response = await api.get(
    `/emails/applications/${applicationId}`
  );

  return response.data;
};

export const getHRDashboardSummary = async () => {
  const response = await api.get("/jobs/dashboard-summary");
  return response.data;
};

// Preview candidate CV
export const previewCandidateCV = async (
  applicationId: number
) => {
  const response = await api.get(
    `/applications/${applicationId}/cv`,
    {
      params: { download: false },
      responseType: "blob",
    }
  );

  return response.data;
};


// Download candidate CV
export const downloadCandidateCV = async (
  applicationId: number
) => {
  const response = await api.get(
    `/applications/${applicationId}/cv`,
    {
      params: { download: true },
      responseType: "blob",
    }
  );

  return response.data;
};