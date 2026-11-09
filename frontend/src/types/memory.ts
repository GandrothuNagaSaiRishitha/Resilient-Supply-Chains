import type { ApiResponse } from './api'
import type { CrisisType } from './crisisReport'

export type MemoryOutcome = 'Successful' | 'Ineffective'

export interface HistoricalIncidentMemory {
  id: string
  incidentDate: string
  crisisType: CrisisType
  supplier: string
  title: string
  description: string
  decisionTaken: string
  expectedResult: string
  actualOutcome: string
  outcome: MemoryOutcome
  lessonLearned: string
  demoRecord?: boolean
  sourceType?: string | null
  verified?: boolean | null
  confidence?: number | null
}

export interface MemoryOverviewStats {
  totalHistoricalIncidents: number
  successfulStrategies: number
  ineffectiveStrategies: number
  lessonsRetained: number
  demo?: boolean
}

export interface LearnedInsight {
  id: string
  category: 'Recurring pattern' | 'Successful strategy' | 'Ineffective approach' | 'Lesson learned'
  title: string
  description: string
  evidenceCount: number
}

export interface MemoryLifecycleStage {
  id: 'retain' | 'recall' | 'reflect'
  title: string
  description: string
  example: string
}

export interface MemoryFilters {
  crisisType: CrisisType | ''
  supplier: string
  outcome: MemoryOutcome | ''
  dateFrom: string
  dateTo: string
}

export interface MemoryCentreData {
  stats: MemoryOverviewStats
  memories: HistoricalIncidentMemory[]
  insights: LearnedInsight[]
  lifecycle: MemoryLifecycleStage[]
  crisisTypes: CrisisType[]
  suppliers: string[]
}

export type MemoryCentreResponse = ApiResponse<MemoryCentreData>
export type MemorySearchResponse = ApiResponse<HistoricalIncidentMemory[]>
export type MemoryDetailResponse = ApiResponse<HistoricalIncidentMemory>
