import { Router } from "express";

const router = Router();

const SERVICE_ID = "9ec71862-e3e9-4b72-8824-107807cd974c";
const ENVIRONMENT_ID = "f51434f3-fa8e-4da8-8e06-a05d1f82c78f";
const RAILWAY_API = "https://backboard.railway.app/graphql/v2";

async function railwayQuery(query: string, variables: Record<string, unknown> = {}) {
  const token = process.env.RAILWAY_API_TOKEN;
  if (!token) throw new Error("RAILWAY_API_TOKEN not set");

  const res = await fetch(RAILWAY_API, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${token}`,
    },
    body: JSON.stringify({ query, variables }),
  });

  const json = await res.json() as { data?: unknown; errors?: Array<{ message: string }> };
  if (json.errors?.length) throw new Error(json.errors[0].message);
  return json.data;
}

async function getLatestDeploymentId(): Promise<{ deploymentId: string; status: string; createdAt: string; updatedAt: string }> {
  const data = await railwayQuery(
    `query($serviceId: String!, $environmentId: String!) {
      serviceInstance(serviceId: $serviceId, environmentId: $environmentId) {
        latestDeployment {
          id
          status
          createdAt
          updatedAt
        }
      }
    }`,
    { serviceId: SERVICE_ID, environmentId: ENVIRONMENT_ID }
  ) as { serviceInstance?: { latestDeployment: { id: string; status: string; createdAt: string; updatedAt: string } } };

  const dep = data?.serviceInstance?.latestDeployment;
  if (!dep) throw new Error("No deployment found");
  return { deploymentId: dep.id, status: dep.status, createdAt: dep.createdAt, updatedAt: dep.updatedAt };
}

router.get("/railway/logs", async (req, res) => {
  try {
    const limit = Math.min(Number(req.query.limit) || 200, 500);
    const { deploymentId } = await getLatestDeploymentId();

    const data = await railwayQuery(
      `query($deploymentId: String!, $limit: Int!) {
        deploymentLogs(deploymentId: $deploymentId, limit: $limit) {
          timestamp
          message
          severity
        }
      }`,
      { deploymentId, limit }
    ) as { deploymentLogs?: Array<{ timestamp: string; message: string; severity: string }> };

    const raw = data?.deploymentLogs ?? [];
    const logs = raw.map(l => ({
      ...l,
      message: l.message.replace(/\u001b\[[0-9;]*m/g, ""),
    }));

    res.json({ logs, service: "worker", project: "MINNAL THE GOAT", deploymentId });
  } catch (err) {
    res.status(500).json({ error: (err as Error).message });
  }
});

router.get("/railway/status", async (req, res) => {
  try {
    const dep = await getLatestDeploymentId();
    res.json({
      status: dep.status,
      deploymentId: dep.deploymentId,
      createdAt: dep.createdAt,
      updatedAt: dep.updatedAt,
      service: "worker",
      project: "MINNAL THE GOAT",
    });
  } catch (err) {
    res.status(500).json({ error: (err as Error).message });
  }
});

export default router;
