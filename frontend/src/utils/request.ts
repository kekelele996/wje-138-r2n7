/** 后端业务错误：保留 HTTP 状态码、错误码与可读原因（中文 message 直接用于页面提示）。 */
export class ApiError extends Error {
  status: number;
  code: string;

  constructor(message: string, status: number, code: string) {
    super(message);
    this.name = 'ApiError';
    this.status = status;
    this.code = code;
  }
}

async function extractMessage(response: Response): Promise<{ code: string; message: string }> {
  try {
    const data = await response.json();
    if (data && typeof data === 'object' && 'message' in data) {
      return { code: String(data.code ?? 'http_error'), message: String(data.message) };
    }
    return { code: 'http_error', message: `请求失败（${response.status}）` };
  } catch {
    return { code: 'http_error', message: `请求失败（${response.status}）` };
  }
}

export async function request<T>(url: string, init?: RequestInit): Promise<T> {
  const response = await fetch(url, {
    headers: { 'Content-Type': 'application/json', ...(init?.headers ?? {}) },
    ...init,
  });
  if (!response.ok) {
    const { code, message } = await extractMessage(response);
    throw new ApiError(message, response.status, code);
  }
  return response.json() as Promise<T>;
}
