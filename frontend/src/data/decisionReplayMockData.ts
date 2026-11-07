import type { RecoveryStrategyKey } from '../types/simulation'
import type { ReplayActualOutcome, ReplayHistoricalEvidence } from '../pages/DecisionReplay/types'

export interface DecisionReplayMockRecord {
  incidentId: string
  originalStrategyKey: RecoveryStrategyKey
  actualOutcome: ReplayActualOutcome
  memoryFreeStrategyKey: RecoveryStrategyKey
  memoryInformedStrategyKey: RecoveryStrategyKey
  historicalEvidence: ReplayHistoricalEvidence[]
  evidenceExplanation: string
  comparisonExplanation: string
}

const demoNotice = 'Illustrative synthetic demo data only. These records are not actual company outcomes, AI-generated recommendations, or memories retrieved from Hindsight.'

export { demoNotice as decisionReplayDemoNotice }

export const decisionReplayMockData: Record<string, DecisionReplayMockRecord> = {
  'INC-DEMO-2481': {
    incidentId: 'INC-DEMO-2481',
    originalStrategyKey: 'reroute',
    actualOutcome: {
      additionalCost: 31200,
      deliveryDelayDays: 5,
      inventoryShortageUnits: 410,
      ordersAffected: 126,
      successful: true,
      summary: 'Synthetic example outcome: rerouting shortened the delay compared with the wait scenario, with added freight cost and some remaining shortage exposure.',
    },
    memoryFreeStrategyKey: 'wait',
    memoryInformedStrategyKey: 'reroute',
    historicalEvidence: [
      {
        id: 'HIST-DEMO-031',
        incidentDate: '2025-03-18',
        crisisType: 'Shipment Disruption',
        decision: 'Reroute shipment through an alternate port.',
        actualOutcome: 'Synthetic example: delivery arrived sooner than the wait option, with additional freight cost.',
        lesson: 'Verify alternate port capacity early and compare the freight premium against the time saved.',
      },
      {
        id: 'HIST-DEMO-044',
        incidentDate: '2024-11-02',
        crisisType: 'Shipment Disruption',
        decision: 'Wait for port operations to normalize.',
        actualOutcome: 'Synthetic example: congestion extended the wait window while inventory buffers remained low.',
        lesson: 'Waiting can preserve budget but may increase shortage exposure when buffers are low.',
      },
    ],
    evidenceExplanation: 'HIST-DEMO-031 is the matching reroute example: it records a shorter delivery delay with added freight cost. HIST-DEMO-044 records extended waiting under low-buffer conditions. Together, these authored examples are used to illustrate why the replay favors rerouting over waiting; they are not retrieved memories.',
    comparisonExplanation: 'The memory-free demo uses the baseline wait strategy. Considering the two synthetic examples changes the illustrative choice to rerouting, trading additional freight cost for reduced delay and shortage exposure.',
  },
  'INC-DEMO-2479': {
    incidentId: 'INC-DEMO-2479',
    originalStrategyKey: 'emergency-sourcing',
    actualOutcome: {
      additionalCost: 101400,
      deliveryDelayDays: 6,
      inventoryShortageUnits: 360,
      ordersAffected: 84,
      successful: true,
      summary: 'Synthetic example outcome: alternate supply reduced the modeled shortage compared with waiting, but qualification and expedite costs were higher.',
    },
    memoryFreeStrategyKey: 'wait',
    memoryInformedStrategyKey: 'emergency-sourcing',
    historicalEvidence: [
      {
        id: 'HIST-DEMO-052',
        incidentDate: '2025-01-21',
        crisisType: 'Supplier Failure',
        decision: 'Qualify an alternate supplier for an expedited allocation.',
        actualOutcome: 'Synthetic example: a limited allocation reduced the production gap after quality review.',
        lesson: 'Start alternate-source qualification early when supplier recovery timing is uncertain.',
      },
      {
        id: 'HIST-DEMO-058',
        incidentDate: '2024-08-14',
        crisisType: 'Supplier Failure',
        decision: 'Wait for the primary supplier to restore production.',
        actualOutcome: 'Synthetic example: recovery took longer than the initial estimate and shortages persisted.',
        lesson: 'Waiting alone may be unsuitable when production recovery has no confirmed date.',
      },
    ],
    evidenceExplanation: 'HIST-DEMO-052 illustrates an alternate-source allocation reducing a supplier production gap; HIST-DEMO-058 illustrates an uncertain primary-supplier recovery extending shortages. The fixed comparison uses those two lessons to illustrate why emergency sourcing is preferred to waiting here.',
    comparisonExplanation: 'The memory-free demo starts with waiting to avoid a new commitment. The synthetic examples illustrate the risk of unconfirmed supplier recovery and the potential value of alternate sourcing, so the memory-informed demo selects emergency sourcing.',
  },
  'INC-DEMO-2476': {
    incidentId: 'INC-DEMO-2476',
    originalStrategyKey: 'redistribute',
    actualOutcome: {
      additionalCost: 10800,
      deliveryDelayDays: 4,
      inventoryShortageUnits: 105,
      ordersAffected: 42,
      successful: true,
      summary: 'Synthetic example outcome: network transfers reduced the local shortage while retaining some exposure at the source facility.',
    },
    memoryFreeStrategyKey: 'emergency-sourcing',
    memoryInformedStrategyKey: 'redistribute',
    historicalEvidence: [
      {
        id: 'HIST-DEMO-063',
        incidentDate: '2025-05-09',
        crisisType: 'Inventory Shortage',
        decision: 'Redistribute stock from a facility with excess coverage.',
        actualOutcome: 'Synthetic example: priority orders were protected, while the origin site had a smaller buffer.',
        lesson: 'Check source-site minimum buffers before transferring inventory.',
      },
      {
        id: 'HIST-DEMO-067',
        incidentDate: '2024-12-03',
        crisisType: 'Inventory Shortage',
        decision: 'Emergency-source a small component quantity.',
        actualOutcome: 'Synthetic example: supply arrived quickly but incurred a higher unit premium.',
        lesson: 'Compare emergency unit premiums with available network stock before committing.',
      },
    ],
    evidenceExplanation: 'HIST-DEMO-063 demonstrates a network transfer protecting priority orders, with a source-buffer trade-off. HIST-DEMO-067 records a higher unit premium for emergency supply. These authored examples illustrate why the replay selects redistribution after checking origin-site minimum stock.',
    comparisonExplanation: 'The memory-free demo selects emergency sourcing to reduce shortage quickly. The synthetic examples emphasize both network stock availability and the emergency premium, shifting the illustrative choice to redistribution subject to a source-buffer check.',
  },
}
