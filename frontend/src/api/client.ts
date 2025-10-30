import axios, { AxiosError } from "axios";
import { API_BASE_URL, ERROR_MESSAGES } from "@/constants";

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    "Content-Type": "application/json",
  },
});

apiClient.interceptors.response.use(
  (response) => response,
  (error: AxiosError) => {
    if (error.code === "ECONNABORTED") {
      throw new Error(ERROR_MESSAGES.TIMEOUT_ERROR);
    }

    if (!error.response) {
      throw new Error(ERROR_MESSAGES.NETWORK_ERROR);
    }

    const status = error.response.status;
    const data = error.response.data as { detail?: string };

    if (status === 404) {
      throw new Error(data.detail || ERROR_MESSAGES.INVALID_STOCK);
    }

    if (status === 400) {
      throw new Error(data.detail || ERROR_MESSAGES.INVALID_DATE_RANGE);
    }

    if (status >= 500) {
      throw new Error(ERROR_MESSAGES.SERVER_ERROR);
    }

    throw error;
  },
);
