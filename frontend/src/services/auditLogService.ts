import api from "./api";

export interface AuditLog {
  log_id: number;
  application_id: number | null;
  actor_id: number | null;
  action: string;
  entity_type: string;
  entity_id: number | null;
  details: Record<string, any> | null;
  created_at: string;
}

export interface JobAuditLogsResponse {
  job_id: number;
  total_returned: number;
  logs: AuditLog[];
}

export const getJobAuditLogs = async (
  jobId: number,
  limit: number = 50,
  offset: number = 0
): Promise<JobAuditLogsResponse> => {
  const response = await api.get(
    `/audit-logs/jobs/${jobId}`,
    {
      params: {
        limit,
        offset,
      },
    }
  );

  return response.data;
};