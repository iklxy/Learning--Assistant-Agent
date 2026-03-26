import axios, { AxiosInstance, AxiosError } from "axios";

export interface ChatRequest {
  query: string;
  use_tools: boolean;
}

export interface ChatResponse {
  response: string;
  stats: Record<string, unknown>;
}

export interface HealthResponse {
  status: "ready" | "initializing";
}

export interface HistoryMessage {
  role: string;
  content: string;
  timestamp: string;
}

export interface HistoryResponse {
  messages: HistoryMessage[];
}

export interface ResetResponse {
  success: boolean;
}

export class AgentClient {
  private client: AxiosInstance;
  private baseURL: string;

  constructor(baseURL: string = "http://127.0.0.1:8765") {
    this.baseURL = baseURL;
    this.client = axios.create({
      baseURL: this.baseURL,
      timeout: 300000,
    });
  }

  async health(): Promise<HealthResponse> {
    try {
      const response = await this.client.get<HealthResponse>("/health");
      return response.data;
    } catch (error) {
      throw this.handleError(error, "health check");
    }
  }

  async chat(query: string, useTools: boolean = true): Promise<ChatResponse> {
    try {
      const response = await this.client.post<ChatResponse>("/chat", {
        query,
        use_tools: useTools,
      });
      return response.data;
    } catch (error) {
      throw this.handleError(error, "chat");
    }
  }

  async reset(): Promise<ResetResponse> {
    try {
      const response = await this.client.post<ResetResponse>("/reset");
      return response.data;
    } catch (error) {
      throw this.handleError(error, "reset");
    }
  }

  async history(): Promise<HistoryResponse> {
    try {
      const response = await this.client.get<HistoryResponse>("/history");
      return response.data;
    } catch (error) {
      throw this.handleError(error, "history");
    }
  }

  private handleError(error: unknown, operation: string): Error {
    if (axios.isAxiosError(error)) {
      const axiosError = error as AxiosError;
      if (axiosError.code === "ECONNREFUSED") {
        return new Error(
          `Could not connect to Agent API at ${this.baseURL}. Is the backend running?`
        );
      }
      if (axiosError.response?.status === 503) {
        return new Error("System is still initializing. Please wait...");
      }
      if (axiosError.response?.data) {
        const data = axiosError.response.data as Record<string, unknown>;
        const detail = data.detail || `${operation} failed`;
        return new Error(`API error: ${detail}`);
      }
      return new Error(`${operation} failed: ${axiosError.message}`);
    }
    return new Error(`${operation} failed: ${error}`);
  }
}
