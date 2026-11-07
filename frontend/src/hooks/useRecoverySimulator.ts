import { useEffect, useState } from 'react'
import {
  confirmRecoveryStrategy,
  getSimulationIncidents,
  getSimulationScenario,
} from '../services/simulationService'
import type {
  RecoveryStrategyKey,
  SimulationIncident,
  SimulationScenario,
} from '../types/simulation'

export function useRecoverySimulator() {
  const [incidents, setIncidents] = useState<SimulationIncident[]>([])
  const [selectedIncidentId, setSelectedIncidentId] = useState('')
  const [scenario, setScenario] = useState<SimulationScenario | null>(null)
  const [selectedStrategyKey, setSelectedStrategyKey] = useState<RecoveryStrategyKey | null>(null)
  const [loadingIncidents, setLoadingIncidents] = useState(true)
  const [loadingScenario, setLoadingScenario] = useState(false)
  const [error, setError] = useState(false)
  const [retryKey, setRetryKey] = useState(0)
  const [confirming, setConfirming] = useState(false)
  const [confirmation, setConfirmation] = useState<string | null>(null)
  const [confirmationError, setConfirmationError] = useState(false)

  useEffect(() => {
    let active = true
    getSimulationIncidents()
      .then(({ data }) => {
        if (active) {
          setIncidents(data)
          setSelectedIncidentId((current) => current || data[0]?.id || '')
          if (data.length > 0) setLoadingScenario(true)
        }
      })
      .catch(() => {
        if (active) setError(true)
      })
      .finally(() => {
        if (active) setLoadingIncidents(false)
      })
    return () => { active = false }
  }, [retryKey])

  useEffect(() => {
    if (!selectedIncidentId) return
    let active = true
    getSimulationScenario(selectedIncidentId)
      .then(({ data }) => {
        if (active) {
          setScenario(data)
          setSelectedStrategyKey(data.recommendedStrategyKey)
          setConfirmation(null)
        }
      })
      .catch(() => {
        if (active) {
          setScenario(null)
          setError(true)
        }
      })
      .finally(() => {
        if (active) setLoadingScenario(false)
      })
    return () => { active = false }
  }, [selectedIncidentId, retryKey])

  const selectIncident = (incidentId: string) => {
    setSelectedIncidentId(incidentId)
    setScenario(null)
    setSelectedStrategyKey(null)
    setLoadingScenario(true)
    setError(false)
    setConfirmation(null)
    setConfirmationError(false)
  }

  const selectStrategy = (key: RecoveryStrategyKey) => {
    setSelectedStrategyKey(key)
    setConfirmation(null)
    setConfirmationError(false)
  }

  const retry = () => {
    setError(false)
    setLoadingIncidents(true)
    setLoadingScenario(incidents.length > 0)
    setScenario(null)
    setRetryKey((key) => key + 1)
  }

  const confirmChoice = async () => {
    if (!selectedIncidentId || !selectedStrategyKey) return
    setConfirming(true)
    setConfirmation(null)
    setConfirmationError(false)
    try {
      const { data } = await confirmRecoveryStrategy({
        incidentId: selectedIncidentId,
        strategyKey: selectedStrategyKey,
      })
      setConfirmation(data.confirmationId)
    } catch {
      setConfirmationError(true)
    } finally {
      setConfirming(false)
    }
  }

  return {
    incidents,
    selectedIncidentId,
    selectedIncident: incidents.find(({ id }) => id === selectedIncidentId),
    scenario,
    selectedStrategyKey,
    loading: loadingIncidents || loadingScenario,
    loadingIncidents,
    error,
    empty: !loadingIncidents && incidents.length === 0,
    confirming,
    confirmation,
    confirmationError,
    selectIncident,
    selectStrategy,
    retry,
    confirmChoice,
  }
}
