import { useEffect, useMemo, useState } from 'react'
import {
  getMemoryCentreData,
  getMemoryDetail,
  searchMemories,
} from '../services/memoryService'
import type {
  HistoricalIncidentMemory,
  MemoryCentreData,
  MemoryFilters,
} from '../types/memory'
import type { CrisisType } from '../types/crisisReport'

const initialFilters: MemoryFilters = {
  crisisType: '',
  supplier: '',
  outcome: '',
  dateFrom: '',
  dateTo: '',
}

export function useMemoryCentre() {
  const [data, setData] = useState<MemoryCentreData | null>(null)
  const [memories, setMemories] = useState<HistoricalIncidentMemory[]>([])
  const [filters, setFilters] = useState<MemoryFilters>(initialFilters)
  const [selectedCrisisType, setSelectedCrisisType] = useState<CrisisType | ''>('')
  const [loading, setLoading] = useState(true)
  const [searching, setSearching] = useState(false)
  const [error, setError] = useState(false)
  const [detail, setDetail] = useState<HistoricalIncidentMemory | null>(null)
  const [detailLoading, setDetailLoading] = useState(false)
  const [detailError, setDetailError] = useState(false)
  const [detailOpen, setDetailOpen] = useState(false)
  const [retryKey, setRetryKey] = useState(0)

  useEffect(() => {
    let active = true
    getMemoryCentreData()
      .then(({ data: response }) => {
        if (active) {
          setData(response)
          setMemories(response.memories)
        }
      })
      .catch(() => { if (active) setError(true) })
      .finally(() => { if (active) setLoading(false) })
    return () => { active = false }
  }, [retryKey])

  const updateFilter = async (nextFilters: MemoryFilters) => {
    setFilters(nextFilters)
    setSearching(true)
    try {
      const { data: results } = await searchMemories(nextFilters)
      setMemories(results)
      setError(false)
    } catch {
      setError(true)
    } finally {
      setSearching(false)
    }
  }

  const setFilter = <K extends keyof MemoryFilters>(
    key: K,
    value: MemoryFilters[K],
  ) => {
    const nextFilters = { ...filters, [key]: value }
    if (key === 'dateFrom' && nextFilters.dateTo && value && value > nextFilters.dateTo) {
      nextFilters.dateTo = ''
    }
    if (key === 'dateTo' && nextFilters.dateFrom && value && value < nextFilters.dateFrom) return
    void updateFilter(nextFilters)
    if (key === 'crisisType') setSelectedCrisisType(value as CrisisType | '')
  }

  const resetFilters = () => {
    void updateFilter(initialFilters)
    setSelectedCrisisType('')
  }

  const openDetail = async (memoryId: string) => {
    setDetailOpen(true)
    setDetail(null)
    setDetailLoading(true)
    setDetailError(false)
    try {
      const { data: memory } = await getMemoryDetail(memoryId)
      setDetail(memory)
    } catch {
      setDetailError(true)
    } finally {
      setDetailLoading(false)
    }
  }

  const closeDetail = () => {
    setDetailOpen(false)
    setDetail(null)
    setDetailError(false)
  }

  const retrievedMemories = useMemo(() => {
    if (!selectedCrisisType) return memories
    return memories.filter((memory) => memory.crisisType === selectedCrisisType)
  }, [memories, selectedCrisisType])

  const retry = () => {
    setError(false)
    setLoading(true)
    setRetryKey((key) => key + 1)
  }

  return {
    data,
    memories,
    filters,
    selectedCrisisType,
    setSelectedCrisisType,
    setFilter,
    resetFilters,
    retrievedMemories,
    loading,
    searching,
    error,
    detail,
    detailLoading,
    detailError,
    detailOpen,
    openDetail,
    closeDetail,
    retry,
  }
}
