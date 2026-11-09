import axios, { isAxiosError, type AxiosError, type InternalAxiosRequestConfig } from 'axios'
import type { ApiErrorPayload } from '../types/api'
import { dataSource, getApiBaseUrl } from './apiConfig'
import { getAccessToken } from './authService'

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
  if (error.code === 'ERR_CANCELED') return 'The API request was cancelled before it completed.'
  if (error.code === 'ECONNABORTED' || error.code === 'ETIMEDOUT') {
    return 'The API request timed out. Check that the backend is running and try again.'
  }
  if (!error.response) {
    return 'Could not reach the API. Check the backend connection and CORS configuration, then try again.'
  }
  return payload?.message
    ?? payload?.detail
    ?? payload?.error
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
  timeout: Number(import.meta.env.VITE_API_TIMEOUT_MS) || 15_000,
  headers: { Accept: 'application/json' },
})

api.interceptors.request.use(
  async (config: InternalAxiosRequestConfig) => {
    if (dataSource === 'api' && !getApiBaseUrl() && !import.meta.env.DEV) {
      throw new ApiClientError('VITE_API_BASE_URL is required when VITE_DATA_SOURCE is "api".', {
        code: 'API_BASE_URL_MISSING',
      })
    }
    if (dataSource === 'api') {
      const accessToken = await getAccessToken()
      config.headers.set('Authorization', `Bearer ${accessToken}`)
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
