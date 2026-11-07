import axios, { isAxiosError, type AxiosError, type InternalAxiosRequestConfig } from 'axios'
import type { ApiErrorPayload } from '../types/api'
import { dataSource, getApiBaseUrl } from './apiConfig'

export class ApiClientError extends Error {
  readonly status?: number
  readonly code?: string
  readonly requestId?: string
  readonly details?: unknown

  constructor(
    message: string,
    options: { status?: number; code?: string; requestId?: string; details?: unknown } = {},
  ) {
    super(message)
    this.name = 'ApiClientError'
    this.status = options.status
    this.code = options.code
    this.requestId = options.requestId
    this.details = options.details
  }
}

function getErrorMessage(error: AxiosError<ApiErrorPayload>): string {
  const payload = error.response?.data
  return payload?.message
    ?? payload?.detail
    ?? payload?.error
    ?? error.message
    ?? 'The API request failed.'
}

export function normalizeApiError(error: unknown): ApiClientError {
  if (error instanceof ApiClientError) return error

  if (isAxiosError<ApiErrorPayload>(error)) {
    const headerRequestId = error.response?.headers?.['x-request-id']
    return new ApiClientError(getErrorMessage(error), {
      status: error.response?.status,
      code: error.response?.data?.code ?? error.code,
      requestId: error.response?.data?.requestId
        ?? (typeof headerRequestId === 'string' ? headerRequestId : undefined),
      details: error.response?.data?.details,
    })
  }

  return new ApiClientError(error instanceof Error ? error.message : 'The API request failed.')
}

const api = axios.create({
  baseURL: getApiBaseUrl(),
  timeout: 15_000,
  headers: { Accept: 'application/json' },
})

api.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    if (dataSource === 'api' && !getApiBaseUrl()) {
      throw new ApiClientError('VITE_API_BASE_URL is required when VITE_DATA_SOURCE is "api".', {
        code: 'API_BASE_URL_MISSING',
      })
    }
    return config
  },
  (error: unknown) => Promise.reject(normalizeApiError(error)),
)

api.interceptors.response.use(
  (response) => response,
  (error: unknown) => Promise.reject(normalizeApiError(error)),
)

export default api
