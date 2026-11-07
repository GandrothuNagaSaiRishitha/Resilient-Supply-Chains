import type {
  RecoveryStrategy,
  SimulationIncident,
  SimulationScenario,
} from '../types/simulation'

export const simulationIncidents: SimulationIncident[] = [
  {
    id: 'INC-DEMO-2481',
    crisisType: 'Shipment Disruption',
    title: 'Port congestion delaying inbound components',
    reportedAt: 'Nov 07, 2026',
  },
  {
    id: 'INC-DEMO-2479',
    crisisType: 'Supplier Failure',
    title: 'Supplier production line interruption',
    reportedAt: 'Nov 06, 2026',
  },
  {
    id: 'INC-DEMO-2476',
    crisisType: 'Inventory Shortage',
    title: 'Control module inventory below threshold',
    reportedAt: 'Nov 05, 2026',
  },
]

const shipmentStrategies: RecoveryStrategy[] = [
  {
    key: 'wait',
    name: 'Wait for shipment',
    summary: 'Keep the current route and wait for port operations to normalize.',
    additionalCost: 0,
    deliveryDelayDays: 9,
    projectedShortageUnits: 840,
    riskLevel: 'High',
    feasibility: 'Feasible',
    feasibilityNote: 'Current shipment remains active.',
    tradeOff: 'Lowest added cost; accepts the longest delay and shortage exposure.',
  },
  {
    key: 'reroute',
    name: 'Reroute shipment',
    summary: 'Divert inbound freight through an alternate port and carrier.',
    additionalCost: 28600,
    deliveryDelayDays: 4,
    projectedShortageUnits: 360,
    riskLevel: 'Medium',
    feasibility: 'Conditional',
    feasibilityNote: 'Alternate port capacity must be confirmed.',
    tradeOff: 'Balances cost and speed; depends on available alternate capacity.',
  },
  {
    key: 'emergency-sourcing',
    name: 'Emergency sourcing',
    summary: 'Purchase a short-term quantity from an approved alternate supplier.',
    additionalCost: 74200,
    deliveryDelayDays: 2,
    projectedShortageUnits: 120,
    riskLevel: 'Low',
    feasibility: 'Conditional',
    feasibilityNote: 'Expedited allocation and quality checks required.',
    tradeOff: 'Fastest recovery and smallest shortage; highest additional cost.',
  },
  {
    key: 'redistribute',
    name: 'Redistribute inventory',
    summary: 'Transfer available stock between warehouses to protect priority orders.',
    additionalCost: 12400,
    deliveryDelayDays: 5,
    projectedShortageUnits: 290,
    riskLevel: 'Medium',
    feasibility: 'Feasible',
    feasibilityNote: 'Demo network stock is available for transfer.',
    tradeOff: 'Moderate cost and shortage reduction; may reduce buffer elsewhere.',
  },
]

const supplierFailureStrategies: RecoveryStrategy[] = [
  {
    key: 'wait',
    name: 'Wait for shipment',
    summary: 'Hold the current recovery plan while the supplier restores output.',
    additionalCost: 0,
    deliveryDelayDays: 14,
    projectedShortageUnits: 1260,
    riskLevel: 'Critical',
    feasibility: 'Feasible',
    feasibilityNote: 'No additional sourcing commitments.',
    tradeOff: 'Avoids added spend but carries the greatest delay and shortage exposure.',
  },
  {
    key: 'reroute',
    name: 'Reroute shipment',
    summary: 'Use an alternate transport lane for supplier stock already in transit.',
    additionalCost: 34100,
    deliveryDelayDays: 8,
    projectedShortageUnits: 720,
    riskLevel: 'High',
    feasibility: 'Conditional',
    feasibilityNote: 'Limited in-transit stock is available to divert.',
    tradeOff: 'Reduces delay for existing stock; does not fully offset the production gap.',
  },
  {
    key: 'emergency-sourcing',
    name: 'Emergency sourcing',
    summary: 'Qualify an alternate supplier for an expedited component allocation.',
    additionalCost: 96500,
    deliveryDelayDays: 5,
    projectedShortageUnits: 300,
    riskLevel: 'Medium',
    feasibility: 'Conditional',
    feasibilityNote: 'Alternate supplier qualification is required.',
    tradeOff: 'Strong shortage reduction and recovery speed at a significant premium.',
  },
  {
    key: 'redistribute',
    name: 'Redistribute inventory',
    summary: 'Pool stock across facilities and prioritize constrained customer demand.',
    additionalCost: 18700,
    deliveryDelayDays: 7,
    projectedShortageUnits: 540,
    riskLevel: 'Medium',
    feasibility: 'Feasible',
    feasibilityNote: 'Inventory pooling is available in this illustrative scenario.',
    tradeOff: 'Lower cost than new sourcing; shifts rather than eliminates local exposure.',
  },
]

const inventoryStrategies: RecoveryStrategy[] = [
  {
    key: 'wait',
    name: 'Wait for shipment',
    summary: 'Maintain current replenishment timing without additional intervention.',
    additionalCost: 0,
    deliveryDelayDays: 8,
    projectedShortageUnits: 350,
    riskLevel: 'High',
    feasibility: 'Feasible',
    feasibilityNote: 'Existing replenishment plan remains in place.',
    tradeOff: 'No added cost, with shortage exposure persisting until replenishment.',
  },
  {
    key: 'reroute',
    name: 'Reroute shipment',
    summary: 'Expedite the replenishment shipment using a faster alternate lane.',
    additionalCost: 16200,
    deliveryDelayDays: 3,
    projectedShortageUnits: 110,
    riskLevel: 'Low',
    feasibility: 'Conditional',
    feasibilityNote: 'Expedited carrier capacity must be secured.',
    tradeOff: 'Shortens the replenishment gap; premium transport adds cost.',
  },
  {
    key: 'emergency-sourcing',
    name: 'Emergency sourcing',
    summary: 'Secure a limited quantity from a secondary approved supplier.',
    additionalCost: 48900,
    deliveryDelayDays: 2,
    projectedShortageUnits: 40,
    riskLevel: 'Low',
    feasibility: 'Conditional',
    feasibilityNote: 'Secondary supplier allocation is subject to confirmation.',
    tradeOff: 'Minimizes projected shortage quickly but has higher unit cost.',
  },
  {
    key: 'redistribute',
    name: 'Redistribute inventory',
    summary: 'Transfer stock from facilities with greater coverage to affected sites.',
    additionalCost: 9200,
    deliveryDelayDays: 4,
    projectedShortageUnits: 90,
    riskLevel: 'Low',
    feasibility: 'Feasible',
    feasibilityNote: 'Inter-warehouse transfer is feasible in this demo scenario.',
    tradeOff: 'Low cost and reduced shortage; may consume buffer stock at origin sites.',
  },
]

export const simulationScenarios: Record<string, SimulationScenario> = {
  'INC-DEMO-2481': {
    incident: simulationIncidents[0],
    summary:
      'Inbound components are delayed by port congestion. The illustrative scenario compares protecting priority orders against transport premium and remaining network stock.',
    constraints: [
      { id: 'arrival', label: 'Current inbound ETA', detail: '9 days (demo estimate)' },
      { id: 'stock', label: 'Network inventory buffer', detail: 'Limited for priority components' },
      { id: 'capacity', label: 'Alternate port capacity', detail: 'Subject to confirmation' },
    ],
    strategies: shipmentStrategies,
    recommendedStrategyKey: 'reroute',
    recommendationExplanation:
      'Rerouting is the modeled middle ground: it reduces the expected delay and projected shortage compared with waiting, while requiring less additional spend than emergency sourcing. Its feasibility depends on confirming alternate port capacity.',
  },
  'INC-DEMO-2479': {
    incident: simulationIncidents[1],
    summary:
      'A supplier production interruption constrains component replenishment. The modeled options weigh alternate qualification time against the cost of expedited supply.',
    constraints: [
      { id: 'recovery', label: 'Supplier recovery window', detail: '14 days (demo estimate)' },
      { id: 'qualification', label: 'Alternate source', detail: 'Requires qualification review' },
      { id: 'buffer', label: 'Available component buffer', detail: 'Below modeled demand' },
    ],
    strategies: supplierFailureStrategies,
    recommendedStrategyKey: 'emergency-sourcing',
    recommendationExplanation:
      'Emergency sourcing has the lowest modeled delivery delay and shortage for this supplier-interruption scenario. It carries the highest additional cost and depends on alternate supplier qualification, so the trade-off should be reviewed before choosing.',
  },
  'INC-DEMO-2476': {
    incident: simulationIncidents[2],
    summary:
      'A component shortage puts near-term orders at risk. The demo scenario evaluates using distributed stock versus paying to accelerate replenishment.',
    constraints: [
      { id: 'coverage', label: 'Current stock coverage', detail: '8 days (demo estimate)' },
      { id: 'transfer', label: 'Transfer stock', detail: 'Available between selected facilities' },
      { id: 'orders', label: 'Priority demand', detail: '42 affected orders (demo estimate)' },
    ],
    strategies: inventoryStrategies,
    recommendedStrategyKey: 'redistribute',
    recommendationExplanation:
      'Redistributing inventory is the modeled lower-cost option that reduces the shortage and delivery delay in this scenario. The main trade-off is reduced buffer at facilities that supply the transfer.',
  },
}

export const strategyChartColors: Record<string, string> = {
  wait: '#64748b',
  reroute: '#2563eb',
  'emergency-sourcing': '#8b5cf6',
  redistribute: '#14b8a6',
}
