import {
  learnedInsights,
  memoryCrisisTypes,
  memoryLifecycle,
  memoryOverviewStats,
  memoryRecords,
} from '../data/memoryMockData'
import api from './api'
import { apiEndpoints } from './apiEndpoints'
import { isMockMode } from './apiConfig'
import type { ApiResponse } from '../types/api'
import type {
  MemoryCentreResponse,
  MemoryDetailResponse,
  MemoryFilters,
  MemorySearchResponse,
} from '../types/memory'

const memoryRequestTimeout = Number(import.meta.env.VITE_MEMORY_API_TIMEOUT_MS) || 180_000

export async function getMemoryCentreData(): Promise<MemoryCentreResponse> {
  if (!isMockMode) {
    const { data } = await api.get<ApiResponse<MemoryCentreResponse['data']>>(apiEndpoints.memoryOverview, { timeout: memoryRequestTimeout })
    return data
  }
  const suppliers = [...new Set(memoryRecords.map((memory) => memory.supplier))].sort()

  return {
    data: {
      stats: memoryOverviewStats,
      memories: memoryRecords,
      insights: learnedInsights,
      lifecycle: memoryLifecycle,
      crisisTypes: [...memoryCrisisTypes],
      suppliers,
    },
  }
}

export async function searchMemories(
  filters: MemoryFilters,
): Promise<MemorySearchResponse> {
  if (!isMockMode) {
    const params = Object.fromEntries(
      Object.entries(filters).filter(([, value]) => value !== ''),
    )
    const { data } = await api.get<ApiResponse<MemorySearchResponse['data']>>(apiEndpoints.memorySearch, { params, timeout: memoryRequestTimeout })
    return data
  }
  const data = memoryRecords.filter((memory) => {
    if (filters.crisisType && memory.crisisType !== filters.crisisType) return false
    if (filters.supplier && memory.supplier !== filters.supplier) return false
    if (filters.outcome && memory.outcome !== filters.outcome) return false
    if (filters.dateFrom && memory.incidentDate < filters.dateFrom) return false
    if (filters.dateTo && memory.incidentDate > filters.dateTo) return false
    return true
  })

  return { data }
}

export async function getMemoryDetail(
  memoryId: string,
): Promise<MemoryDetailResponse> {
  if (!isMockMode) {
    const { data } = await api.get<ApiResponse<MemoryDetailResponse['data']>>(apiEndpoints.memoryDetail(memoryId), { timeout: memoryRequestTimeout })
    return data
  }
  const memory = memoryRecords.find(({ id }) => id === memoryId)
  if (!memory) {
    throw new Error(`No illustrative demo memory found for incident ${memoryId}.`)
  }

  return { data: memory }
}
