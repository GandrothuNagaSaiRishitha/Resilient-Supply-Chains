import { useEffect, useState } from 'react'
import {
  getDecisionReplay,
  getDecisionReplayIncidents,
  replayIncident as runDecisionReplay,
} from '../../../services/decisionReplayService'
import type { DecisionReplayRecord } from '../types'
import type { SimulationIncident } from '../../../types/simulation'

export function useDecisionReplay() {
  const [incidents, setIncidents] = useState<SimulationIncident[]>([])
  const [incidentId, setIncidentId] = useState('')
  const [record, setRecord] = useState<DecisionReplayRecord | null>(null)
  const [loading, setLoading] = useState(true)
  const [replaying, setReplaying] = useState(false)
  const [error, setError] = useState(false)
  const [replayMessage, setReplayMessage] = useState('')
  const [retryToken, setRetryToken] = useState(0)

  useEffect(() => {
    let active = true
    getDecisionReplayIncidents()
      .then(({ data }) => {
        if (active) {
          setIncidents(data)
          setIncidentId((current) => current || data[0]?.id || '')
          if (data.length === 0) setLoading(false)
        }
      })
      .catch(() => {
        if (active) {
          setError(true)
          setLoading(false)
        }
      })
    return () => { active = false }
  }, [retryToken])

  useEffect(() => {
    if (!incidentId) return
    let active = true
    getDecisionReplay(incidentId)
      .then(({ data }) => {
        if (active) setRecord(data)
      })
      .catch(() => {
        if (active) setError(true)
      })
      .finally(() => {
        if (active) setLoading(false)
      })
    return () => { active = false }
  }, [incidentId, retryToken])

  const selectIncident = (id: string) => {
    setLoading(true)
    setRecord(null)
    setError(false)
    setIncidentId(id)
    setReplayMessage('')
  }

  const replayIncident = async () => {
    if (!incidentId) return
    setReplaying(true)
    setReplayMessage('')
    try {
      const { data } = await runDecisionReplay(incidentId)
      setReplayMessage(data.message)
    } catch {
      setError(true)
    } finally {
      setReplaying(false)
    }
  }

  const retry = () => {
    setLoading(true)
    setError(false)
    setRecord(null)
    setRetryToken((token) => token + 1)
  }

  return {
    incidents,
    incidentId,
    record,
    loading,
    replaying,
    error,
    replayMessage,
    selectIncident,
    replayIncident,
    retry,
  }
}
