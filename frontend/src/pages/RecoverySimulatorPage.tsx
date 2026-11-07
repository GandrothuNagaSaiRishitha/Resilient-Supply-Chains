import IncidentSelector from '../components/recovery-simulator/IncidentSelector'
import RecommendationAndConfirmation from '../components/recovery-simulator/RecommendationAndConfirmation'
import ScenarioStrategies from '../components/recovery-simulator/ScenarioStrategies'
import { EmptyState, ErrorState, LoadingState } from '../components/recovery-simulator/SimulationStates'
import StrategyComparison from '../components/recovery-simulator/StrategyComparison'
import { useRecoverySimulator } from '../hooks/useRecoverySimulator'
import { isMockMode } from '../services/apiConfig'

export default function RecoverySimulatorPage() {
  const simulator = useRecoverySimulator()

  return (
    <section className="mx-auto max-w-[1440px]">
      <div className="mb-6 flex flex-col justify-between gap-4 lg:flex-row lg:items-end">
        <div>
          <p className="mb-2 text-sm text-slate-500">Workspace / Recovery Simulator</p>
          <h1 className="text-2xl font-semibold tracking-tight text-slate-900 sm:text-[28px]">Recovery Strategy Simulator</h1>
          <p className="mt-1.5 text-sm text-slate-500">{isMockMode ? 'Compare illustrative response options and understand their trade-offs.' : 'Compare recovery options calculated from the selected incident and organization records.'}</p>
        </div>
        <span className="inline-flex w-fit items-center gap-2 rounded-full border border-blue-200 bg-blue-50 px-3 py-1.5 text-[11px] font-semibold tracking-wide text-blue-700">
          <span className="size-1.5 rounded-full bg-blue-500" />{isMockMode ? 'ILLUSTRATIVE DEMO SIMULATIONS' : 'BACKEND API SIMULATIONS'}
        </span>
      </div>

      <IncidentSelector
        incidents={simulator.incidents}
        selectedIncidentId={simulator.selectedIncidentId}
        selectedIncident={simulator.selectedIncident}
        loading={simulator.loadingIncidents}
        onChange={simulator.selectIncident}
      />

      {simulator.loading ? <LoadingState /> : simulator.error ? <ErrorState onRetry={simulator.retry} /> : simulator.empty ? <EmptyState /> : simulator.scenario && simulator.selectedStrategyKey ? (
        <>
          <ScenarioStrategies scenario={simulator.scenario} selectedStrategyKey={simulator.selectedStrategyKey} onSelect={simulator.selectStrategy} />
          <StrategyComparison scenario={simulator.scenario} selectedStrategyKey={simulator.selectedStrategyKey} onSelect={simulator.selectStrategy} />
          <RecommendationAndConfirmation
            scenario={simulator.scenario}
            selectedStrategyKey={simulator.selectedStrategyKey}
            onConfirm={simulator.confirmChoice}
            confirming={simulator.confirming}
            confirmation={simulator.confirmation}
            confirmationError={simulator.confirmationError}
          />
        </>
      ) : <LoadingState />}
    </section>
  )
}
