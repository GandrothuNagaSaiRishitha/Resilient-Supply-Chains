import type {
  HistoricalIncidentMemory,
  LearnedInsight,
  MemoryLifecycleStage,
  MemoryOverviewStats,
} from '../types/memory'

export const memoryOverviewStats: MemoryOverviewStats = {
  totalHistoricalIncidents: 128,
  successfulStrategies: 86,
  ineffectiveStrategies: 42,
  lessonsRetained: 214,
  demo: true,
}

export const memoryRecords: HistoricalIncidentMemory[] = [
  {
    id: 'HIST-DEMO-031',
    incidentDate: '2025-03-18',
    crisisType: 'Shipment Disruption',
    supplier: 'Northstar Components',
    title: 'Port congestion delayed sensor modules',
    description:
      'Synthetic example of an inbound component shipment delayed during a period of port congestion.',
    decisionTaken: 'Reroute shipment through an alternate port.',
    expectedResult:
      'Shorten the delivery delay while maintaining component availability for priority orders.',
    actualOutcome:
      'Illustrative outcome: shipment arrived sooner than the wait option, with additional freight cost.',
    outcome: 'Successful',
    lessonLearned:
      'Confirm alternate capacity early and compare the freight premium against the time saved.',
    demoRecord: true,
  },
  {
    id: 'HIST-DEMO-044',
    incidentDate: '2024-11-02',
    crisisType: 'Shipment Disruption',
    supplier: 'Pacific Freight Group',
    title: 'Vessel wait extended at a congested port',
    description:
      'Synthetic example of inbound material held while port congestion continued beyond the initial estimate.',
    decisionTaken: 'Wait for the original shipment to clear.',
    expectedResult:
      'Avoid incremental logistics costs and continue on the planned route.',
    actualOutcome:
      'Illustrative outcome: additional congestion extended the modeled wait and increased downstream shortage exposure.',
    outcome: 'Ineffective',
    lessonLearned:
      'When inventory buffers are low, define a time-bound decision point for alternate routing.',
    demoRecord: true,
  },
  {
    id: 'HIST-DEMO-052',
    incidentDate: '2025-08-21',
    crisisType: 'Supplier Failure',
    supplier: 'Meridian Industrial Supply',
    title: 'Supplier line interruption constrained control boards',
    description:
      'Synthetic example of a temporary production interruption affecting a high-use component.',
    decisionTaken: 'Use an approved alternate supplier for a limited allocation.',
    expectedResult:
      'Bridge the supply gap while the primary supplier restores production.',
    actualOutcome:
      'Illustrative outcome: alternate allocation reduced the modeled gap after quality and specification checks.',
    outcome: 'Successful',
    lessonLearned:
      'Complete supplier qualification and quality review before committing to emergency purchases.',
    demoRecord: true,
  },
  {
    id: 'HIST-DEMO-019',
    incidentDate: '2024-06-11',
    crisisType: 'Supplier Failure',
    supplier: 'Northstar Components',
    title: 'Production interruption affected shared components',
    description:
      'Synthetic example of a supplier outage where available inventory was pooled between facilities.',
    decisionTaken: 'Redistribute inventory from regional facilities.',
    expectedResult:
      'Protect priority orders until supplier production resumed.',
    actualOutcome:
      'Illustrative outcome: selected orders were protected, while origin-site inventory buffers were reduced.',
    outcome: 'Ineffective',
    lessonLearned:
      'Check network-wide coverage and preserve minimum origin-site buffers before approving transfers.',
    demoRecord: true,
  },
  {
    id: 'HIST-DEMO-063',
    incidentDate: '2025-01-09',
    crisisType: 'Inventory Shortage',
    supplier: 'Apex Motion Supply',
    title: 'Regional stock fell below component threshold',
    description:
      'Synthetic example of a regional component shortage with inventory available at other facilities.',
    decisionTaken: 'Redistribute inventory to the affected warehouse.',
    expectedResult:
      'Cover near-term demand without the premium associated with expedited sourcing.',
    actualOutcome:
      'Illustrative outcome: targeted transfers covered modeled near-term demand at lower added cost.',
    outcome: 'Successful',
    lessonLearned:
      'Verify transfer quantities and origin-site minimum stock before moving inventory.',
    demoRecord: true,
  },
  {
    id: 'HIST-DEMO-028',
    incidentDate: '2024-09-14',
    crisisType: 'Inventory Shortage',
    supplier: 'Meridian Industrial Supply',
    title: 'Control module shortage required expedited replenishment',
    description:
      'Synthetic example of a component shortage with limited transferable network stock.',
    decisionTaken: 'Purchase an expedited allocation from a secondary source.',
    expectedResult:
      'Reduce shortage exposure faster than waiting for the routine replenishment cycle.',
    actualOutcome:
      'Illustrative outcome: replenishment arrived sooner in the example, with a higher premium.',
    outcome: 'Successful',
    lessonLearned:
      'Compare transfer availability with expedited supplier lead time and cost before selecting a response.',
    demoRecord: true,
  },
]

export const learnedInsights: LearnedInsight[] = [
  {
    id: 'insight-port',
    category: 'Recurring pattern',
    title: 'Low buffers amplify port delays',
    description:
      'Synthetic examples show a higher modeled exposure when port delays coincide with limited component coverage.',
    evidenceCount: 2,
  },
  {
    id: 'insight-reroute',
    category: 'Successful strategy',
    title: 'Early alternate-lane checks can protect time',
    description:
      'In illustrative examples, validating capacity early helped compare route premiums before wait windows expanded.',
    evidenceCount: 1,
  },
  {
    id: 'insight-wait',
    category: 'Ineffective approach',
    title: 'Unbounded waiting can extend exposure',
    description:
      'A synthetic port-delay example illustrates why teams may set a review point when inventory coverage is low.',
    evidenceCount: 1,
  },
  {
    id: 'insight-pooling',
    category: 'Lesson learned',
    title: 'Protect origin-site minimums during transfers',
    description:
      'Illustrative supplier and inventory examples highlight the need to check network-wide buffers before redistribution.',
    evidenceCount: 2,
  },
]

export const memoryLifecycle: MemoryLifecycleStage[] = [
  {
    id: 'retain',
    title: 'Retain',
    description: 'Store a new incident, the decision taken, and its eventual outcome.',
    example: 'Incident details → decision → observed outcome',
  },
  {
    id: 'recall',
    title: 'Recall',
    description: 'Retrieve relevant historical experiences when a new crisis is assessed.',
    example: 'New crisis → matching prior experiences',
  },
  {
    id: 'reflect',
    title: 'Reflect',
    description: 'Synthesize patterns and lessons from stored incident outcomes.',
    example: 'Outcomes → lessons → improved future context',
  },
]

export const memoryCrisisTypes = [
  'Shipment Disruption',
  'Supplier Failure',
  'Inventory Shortage',
] as const
