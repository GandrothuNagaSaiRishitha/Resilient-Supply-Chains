import { useEffect, useState } from 'react'
import { useSearchParams } from 'react-router-dom'
import {
  getDecisionIncidents,
  getDecisionReport,
  submitDecisionAction,
} from '../services/decisionService'
import type {
  DecisionAction,
  DecisionReport,
} from '../types/decision'
import type { RecoveryStrategyKey } from '../types/simulation'

export function useDecisionReport() {
  const [searchParams] = useSearchParams()
  const requestedIncidentId = searchParams.get('incidentId')
  const [incidents, setIncidents] = useState<DecisionReport['scenario']['incident'][]>([])
  const [incidentId, setIncidentId] = useState('')
  const [report, setReport] = useState<DecisionReport | null>(null)
  const [loadingIncidents, setLoadingIncidents] = useState(true)
  const [loadingReport, setLoadingReport] = useState(false)
  const [error, setError] = useState(false)
  const [retryKey, setRetryKey] = useState(0)
  const [action, setAction] = useState<DecisionAction | null>(null)
  const [strategyKey, setStrategyKey] = useState<RecoveryStrategyKey | null>(null)
  const [explanation, setExplanation] = useState('')
  const [confirming, setConfirming] = useState(false)
  const [decisionConfirmation, setDecisionConfirmation] = useState<string | null>(null)
  const [decisionError, setDecisionError] = useState(false)

  useEffect(() => {
    let active = true
    getDecisionIncidents()
      .then(({ data }) => {
        if (active) {
          setIncidents(data)
          setIncidentId((current) => requestedIncidentId && data.some((incident) => incident.id === requestedIncidentId)
            ? requestedIncidentId
            : current && data.some((incident) => incident.id === current)
              ? current
              : data[0]?.id || '')
          setReport(null)
          setAction(null)
          setStrategyKey(null)
          setLoadingReport(data.length > 0)
          setError(false)
        }
      })
      .catch(() => { if (active) setError(true) })
      .finally(() => { if (active) setLoadingIncidents(false) })
    return () => { active = false }
  }, [retryKey, requestedIncidentId])

  useEffect(() => {
    if (!incidentId) return
    let active = true
    getDecisionReport(incidentId)
      .then(({ data }) => {
        if (active) {
          setReport(data)
          setStrategyKey(data.scenario.recommendedStrategyKey)
          setAction(null)
          setExplanation('')
          setDecisionConfirmation(null)
        }
      })
      .catch(() => {
        if (active) {
          setReport(null)
          setError(true)
        }
      })
      .finally(() => { if (active) setLoadingReport(false) })
    return () => { active = false }
  }, [incidentId, retryKey])

  const selectIncident = (nextIncidentId: string) => {
    setIncidentId(nextIncidentId)
    setReport(null)
    setAction(null)
    setStrategyKey(null)
    setLoadingReport(true)
    setError(false)
    setDecisionError(false)
  }

  const retry = () => {
    setReport(null)
    setError(false)
    setLoadingIncidents(true)
    setLoadingReport(incidents.length > 0)
    setRetryKey((key) => key + 1)
  }

  const clearConfirmation = () => {
    setDecisionConfirmation(null)
    setDecisionError(false)
  }

  const selectRecommended = () => {
    setAction('accepted')
    setStrategyKey(
      report?.aiRecommendation?.status === 'generated'
        ? report.aiRecommendation.strategyKey
        : report?.scenario.recommendedStrategyKey ?? null,
    )
    clearConfirmation()
  }

  const rejectRecommendation = () => {
    setAction('rejected')
    setStrategyKey(null)
    clearConfirmation()
  }

  const selectAlternative = (key: RecoveryStrategyKey) => {
    setStrategyKey(key)
    const recommendedKey = report?.aiRecommendation?.status === 'generated'
      ? report.aiRecommendation.strategyKey
      : report?.scenario.recommendedStrategyKey
    setAction(key === recommendedKey ? 'accepted' : 'alternative')
    clearConfirmation()
  }

  const confirmDecision = async () => {
    if (!report || !action) return
    setConfirming(true)
    clearConfirmation()
    try {
      const { data } = await submitDecisionAction({
        incidentId: report.scenario.incident.id,
        requestId: crypto.randomUUID(),
        action,
        strategyKey,
        explanation: explanation.trim(),
      })
      setDecisionConfirmation(data.confirmationId)
    } catch {
      setDecisionError(true)
    } finally {
      setConfirming(false)
    }
  }

  return {
    incidents,
    incidentId,
    report,
    loading: loadingIncidents || loadingReport,
    loadingIncidents,
    error,
    action,
    strategyKey,
    explanation,
    confirming,
    decisionConfirmation,
    decisionError,
    selectIncident,
    retry,
    selectRecommended,
    rejectRecommendation,
    selectAlternative,
    confirmDecision,
    setExplanation,
    clearConfirmation,
  }
}
