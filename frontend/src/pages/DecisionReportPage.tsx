import { useDecisionReport } from '../hooks/useDecisionReport'
import { submitOutcomeFeedback } from '../services/decisionService'
import AlternativeStrategies from '../components/decision-report/AlternativeStrategies'
import DecisionActions from '../components/decision-report/DecisionActions'
import DecisionExplanation from '../components/decision-report/DecisionExplanation'
import HistoricalEvidence from '../components/decision-report/HistoricalEvidence'
import IncidentSummary, { IncidentSelector } from '../components/decision-report/IncidentSummary'
import MemoryComparison from '../components/decision-report/MemoryComparison'
import OutcomeFeedbackForm from '../components/decision-report/OutcomeFeedbackForm'
import RecommendationPanel from '../components/decision-report/RecommendationPanel'
import { EmptyState, ErrorState, LoadingState } from '../components/decision-report/DecisionUi'
import { strategyForKey } from '../components/decision-report/decisionUtils'
import { isMockMode } from '../services/apiConfig'

export default function DecisionReportPage() {
  const decision = useDecisionReport()
  const {
    incidents,
    incidentId,
    report,
    loading,
    error,
    action,
    strategyKey,
    explanation,
    confirming,
    decisionConfirmation,
    decisionError,
  } = decision
  const recommendedStrategyKey = report?.aiRecommendation?.status === 'generated'
    ? report.aiRecommendation.strategyKey
    : report?.scenario.recommendedStrategyKey

  return (
    <div className="space-y-5">
      <header className="flex flex-col justify-between gap-2 sm:flex-row sm:items-end">
        <div>
          <p className="text-[10px] font-bold uppercase tracking-[0.16em] text-blue-600">Decision intelligence</p>
          <h1 className="mt-1 text-2xl font-semibold tracking-tight text-slate-900">Decision Report</h1>
          <p className="mt-1 text-xs text-slate-500">{isMockMode ? 'Review illustrative recovery options, demo evidence, and decision trade-offs.' : 'Review incident recovery options, Hindsight evidence, and decision trade-offs.'}</p>
        </div>
        <span className="w-fit rounded-full border border-blue-200 bg-blue-50 px-3 py-1.5 text-[10px] font-semibold text-blue-700">{isMockMode ? 'Illustrative demo data' : 'Backend API data'}</span>
      </header>

      <IncidentSelector
        incidents={incidents}
        incidentId={incidentId}
        loading={loading}
        onChange={decision.selectIncident}
      />

      {loading && <LoadingState />}
      {!loading && error && <ErrorState onRetry={decision.retry} />}
      {!loading && !error && !report && <EmptyState />}

      {!loading && !error && report && (
        <>
          <IncidentSummary report={report} />
          <RecommendationPanel report={report} />
          <AlternativeStrategies
            report={report}
            selectedKey={strategyKey}
            onSelect={decision.selectAlternative}
          />
          <HistoricalEvidence records={report.historicalEvidence} memoryStatus={report.memoryStatus} />
          <MemoryComparison report={report} />
          <DecisionActions
            action={action}
            strategy={strategyKey ? strategyForKey(report.scenario.strategies, strategyKey) : null}
            explanation={explanation}
            confirmation={decisionConfirmation}
            confirming={confirming}
            error={decisionError}
            onAccept={decision.selectRecommended}
            onReject={decision.rejectRecommendation}
            onExplanationChange={decision.setExplanation}
            onConfirm={decision.confirmDecision}
          />
          <OutcomeFeedbackForm
            key={report.scenario.incident.id}
            report={report}
            initialStrategyKey={recommendedStrategyKey ?? report.scenario.recommendedStrategyKey}
            onSubmit={async (request) => {
              const { data } = await submitOutcomeFeedback(request)
              return data.outcomeId
            }}
          />
          <DecisionExplanation notice={report.demoDataNotice} />
        </>
      )}
    </div>
  )
}
