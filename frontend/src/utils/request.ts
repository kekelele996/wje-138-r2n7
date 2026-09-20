export class ApiError extends Error {
  status: number;
  code: string;

  constructor(status: number, code: string, reason: string) {
    super(reason);
    this.status = status;
    this.code = code;
  }
}

async function readReason(response: Response): Promise<{ code: string; reason: string }> {
  const text = await response.text();
  try {
    const data = JSON.parse(text);
    if (data && typeof data === 'object' && 'reason' in data) {
      return { code: String(data.code ?? 'ERROR'), reason: String(data.reason) };
    }
    return { code: 'ERROR', reason: text || `请求失败（${response.status}）` };
  } catch {
    return { code: 'ERROR', reason: text || `请求失败（${response.status}）` };
  }
}

export async function request<T>(url: string, init?: RequestInit): Promise<T> {
  const response = await fetch(url, {
    headers: { 'Content-Type': 'application/json', ...(init?.headers ?? {}) },
    ...init,
  });
  if (!response.ok) {
    const { code, reason } = await readReason(response);
    throw new ApiError(response.status, code, reason);
  }
  return response.json() as Promise<T>;
}
