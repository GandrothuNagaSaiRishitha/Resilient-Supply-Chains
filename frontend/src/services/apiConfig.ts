import type { DataSource } from '../types/api'

// Live API mode is the safe default. Synthetic records must be explicitly
// opted into with VITE_DATA_SOURCE=mock.
const configuredSource = import.meta.env.VITE_DATA_SOURCE?.trim().toLowerCase() || 'api'

if (configuredSource !== 'mock' && configuredSource !== 'api') {
  throw new Error('VITE_DATA_SOURCE must be either "mock" or "api".')
}

export const dataSource: DataSource = configuredSource
export const isMockMode = dataSource === 'mock'

export function getApiBaseUrl(): string | undefined {
  if (import.meta.env.DEV) return ''
  return import.meta.env.VITE_API_BASE_URL?.trim() || undefined
}
