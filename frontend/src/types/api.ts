export type DataSource = 'mock' | 'api'

export interface ApiResponseMeta {
  requestId?: string
  page?: number
  pageSize?: number
  total?: number
}

export interface ApiResponse<T> {
  data: T
  meta?: ApiResponseMeta
}

export interface ApiErrorPayload {
  message?: string
  detail?: string
  error?: string
  code?: string
  requestId?: string
  details?: unknown
}

export interface ApiRequestOptions {
  signal?: AbortSignal
  params?: Record<string, string | number | boolean | undefined>
}
