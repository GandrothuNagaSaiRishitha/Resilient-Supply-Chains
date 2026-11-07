import type { ImpactAnalysis, ImpactIncidentOption } from '../types/impact'

export const impactIncidents: ImpactIncidentOption[] = [
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

export const impactAnalysisByIncident: Record<string, ImpactAnalysis> = {
  'INC-DEMO-2481': {
    incident: impactIncidents[0],
    kpis: [
      { id: 'orders', label: 'Affected Orders', value: 126, formattedValue: '126', severity: 'High' },
      { id: 'shortage', label: 'Inventory Shortage', value: 840, unit: 'units', formattedValue: '840 units', severity: 'Critical' },
      { id: 'suppliers', label: 'Affected Suppliers', value: 3, formattedValue: '3', severity: 'Medium' },
      { id: 'exposure', label: 'Estimated Financial Exposure', value: 284500, formattedValue: '$284,500', severity: 'High' },
    ],
    affectedProducts: [
      { id: 'P-104', product: 'Industrial sensor assembly', component: 'Sensor module SM-4', supplier: 'Northstar Components', shortage: 420, severity: 'Critical' },
      { id: 'P-218', product: 'Precision control unit', component: 'Control board CB-12', supplier: 'Meridian Industrial', shortage: 260, severity: 'High' },
      { id: 'P-319', product: 'Automated valve system', component: 'Valve actuator VA-2', supplier: 'Apex Motion Supply', shortage: 160, severity: 'Medium' },
    ],
    warehouseImpacts: [
      { id: 'wh-east', warehouse: 'East Coast Distribution', location: 'Newark, NJ', availableInventory: 1850, inventoryAtRisk: 460, coverageDays: 6, severity: 'High' },
      { id: 'wh-central', warehouse: 'Central Fulfillment Hub', location: 'Columbus, OH', availableInventory: 2240, inventoryAtRisk: 250, coverageDays: 12, severity: 'Medium' },
      { id: 'wh-west', warehouse: 'West Coast Operations', location: 'Long Beach, CA', availableInventory: 980, inventoryAtRisk: 130, coverageDays: 18, severity: 'Low' },
    ],
    customerOrders: [
      { id: 'ORD-71084', customer: 'Northwind Manufacturing', orderValue: 48200, priority: 'Critical', expectedDelayDays: 9 },
      { id: 'ORD-71091', customer: 'Vertex Industrial Group', orderValue: 36750, priority: 'High', expectedDelayDays: 7 },
      { id: 'ORD-71103', customer: 'Clearwater Systems', orderValue: 21800, priority: 'High', expectedDelayDays: 5 },
      { id: 'ORD-71122', customer: 'Summit Process Controls', orderValue: 14900, priority: 'Medium', expectedDelayDays: 3 },
    ],
    distribution: [
      { category: 'Inventory', value: 38 },
      { category: 'Orders', value: 28 },
      { category: 'Transportation', value: 22 },
      { category: 'Supplier', value: 12 },
    ],
    severityIndicators: [
      { severity: 'Low', count: 8, description: 'Limited operational impact' },
      { severity: 'Medium', count: 14, description: 'Monitor and coordinate' },
      { severity: 'High', count: 9, description: 'Response action recommended' },
      { severity: 'Critical', count: 3, description: 'Immediate review required' },
    ],
    assumptions: {
      items: [
        'All amounts and counts are illustrative demo estimates, not live operational data.',
        'Financial exposure is estimated from at-risk order values and projected delay impact.',
        'Inventory shortage reflects demo demand during the expected shipment delay window.',
        'Severity is a sample classification based on estimated duration, shortage, and order priority.',
      ],
    },
  },
  'INC-DEMO-2479': {
    incident: impactIncidents[1],
    kpis: [
      { id: 'orders', label: 'Affected Orders', value: 84, formattedValue: '84', severity: 'Medium' },
      { id: 'shortage', label: 'Inventory Shortage', value: 1260, unit: 'units', formattedValue: '1,260 units', severity: 'Critical' },
      { id: 'suppliers', label: 'Affected Suppliers', value: 5, formattedValue: '5', severity: 'High' },
      { id: 'exposure', label: 'Estimated Financial Exposure', value: 412800, formattedValue: '$412,800', severity: 'Critical' },
    ],
    affectedProducts: [
      { id: 'P-402', product: 'Power conversion module', component: 'Converter core PC-8', supplier: 'Meridian Industrial', shortage: 740, severity: 'Critical' },
      { id: 'P-415', product: 'Smart relay controller', component: 'Relay pack RP-3', supplier: 'Northstar Components', shortage: 360, severity: 'High' },
      { id: 'P-429', product: 'Thermal management unit', component: 'Cooling plate CP-6', supplier: 'Apex Motion Supply', shortage: 160, severity: 'Medium' },
    ],
    warehouseImpacts: [
      { id: 'wh-east', warehouse: 'East Coast Distribution', location: 'Newark, NJ', availableInventory: 1360, inventoryAtRisk: 610, coverageDays: 4, severity: 'Critical' },
      { id: 'wh-central', warehouse: 'Central Fulfillment Hub', location: 'Columbus, OH', availableInventory: 1980, inventoryAtRisk: 420, coverageDays: 8, severity: 'High' },
      { id: 'wh-west', warehouse: 'West Coast Operations', location: 'Long Beach, CA', availableInventory: 1120, inventoryAtRisk: 230, coverageDays: 14, severity: 'Medium' },
    ],
    customerOrders: [
      { id: 'ORD-70817', customer: 'Apex Energy Solutions', orderValue: 72500, priority: 'Critical', expectedDelayDays: 14 },
      { id: 'ORD-70866', customer: 'Northwind Manufacturing', orderValue: 42800, priority: 'High', expectedDelayDays: 11 },
      { id: 'ORD-70902', customer: 'Brightline Automation', orderValue: 29600, priority: 'High', expectedDelayDays: 8 },
      { id: 'ORD-70938', customer: 'Clearwater Systems', orderValue: 18500, priority: 'Medium', expectedDelayDays: 5 },
    ],
    distribution: [
      { category: 'Inventory', value: 42 },
      { category: 'Orders', value: 24 },
      { category: 'Transportation', value: 10 },
      { category: 'Supplier', value: 24 },
    ],
    severityIndicators: [
      { severity: 'Low', count: 4, description: 'Limited operational impact' },
      { severity: 'Medium', count: 10, description: 'Monitor and coordinate' },
      { severity: 'High', count: 12, description: 'Response action recommended' },
      { severity: 'Critical', count: 7, description: 'Immediate review required' },
    ],
    assumptions: {
      items: [
        'All amounts and counts are illustrative demo estimates, not live operational data.',
        'Supplier exposure assumes production remains constrained during the modeled recovery window.',
        'Inventory shortage reflects demo demand across dependent products and facilities.',
        'Financial exposure uses sample order values and projected fulfillment delays.',
      ],
    },
  },
  'INC-DEMO-2476': {
    incident: impactIncidents[2],
    kpis: [
      { id: 'orders', label: 'Affected Orders', value: 42, formattedValue: '42', severity: 'Medium' },
      { id: 'shortage', label: 'Inventory Shortage', value: 350, unit: 'units', formattedValue: '350 units', severity: 'High' },
      { id: 'suppliers', label: 'Affected Suppliers', value: 2, formattedValue: '2', severity: 'Low' },
      { id: 'exposure', label: 'Estimated Financial Exposure', value: 96800, formattedValue: '$96,800', severity: 'Medium' },
    ],
    affectedProducts: [
      { id: 'P-502', product: 'Control module assembly', component: 'Control module CM-204', supplier: 'Northstar Components', shortage: 210, severity: 'High' },
      { id: 'P-519', product: 'Industrial sensor assembly', component: 'Sensor module SM-4', supplier: 'Meridian Industrial', shortage: 140, severity: 'Medium' },
    ],
    warehouseImpacts: [
      { id: 'wh-east', warehouse: 'East Coast Distribution', location: 'Newark, NJ', availableInventory: 1680, inventoryAtRisk: 190, coverageDays: 8, severity: 'Medium' },
      { id: 'wh-central', warehouse: 'Central Fulfillment Hub', location: 'Columbus, OH', availableInventory: 1820, inventoryAtRisk: 110, coverageDays: 15, severity: 'Low' },
      { id: 'wh-west', warehouse: 'West Coast Operations', location: 'Long Beach, CA', availableInventory: 860, inventoryAtRisk: 50, coverageDays: 21, severity: 'Low' },
    ],
    customerOrders: [
      { id: 'ORD-70312', customer: 'Vertex Industrial Group', orderValue: 26800, priority: 'High', expectedDelayDays: 6 },
      { id: 'ORD-70378', customer: 'Summit Process Controls', orderValue: 19400, priority: 'Medium', expectedDelayDays: 4 },
      { id: 'ORD-70409', customer: 'Brightline Automation', orderValue: 12300, priority: 'Medium', expectedDelayDays: 3 },
      { id: 'ORD-70455', customer: 'Northwind Manufacturing', orderValue: 8700, priority: 'Low', expectedDelayDays: 2 },
    ],
    distribution: [
      { category: 'Inventory', value: 48 },
      { category: 'Orders', value: 30 },
      { category: 'Transportation', value: 8 },
      { category: 'Supplier', value: 14 },
    ],
    severityIndicators: [
      { severity: 'Low', count: 13, description: 'Limited operational impact' },
      { severity: 'Medium', count: 11, description: 'Monitor and coordinate' },
      { severity: 'High', count: 5, description: 'Response action recommended' },
      { severity: 'Critical', count: 1, description: 'Immediate review required' },
    ],
    assumptions: {
      items: [
        'All amounts and counts are illustrative demo estimates, not live operational data.',
        'Inventory shortage is modeled against expected demand until replenishment.',
        'Warehouse coverage days are sample estimates based on assumed average consumption.',
        'Financial exposure represents sample order value at risk and is not a forecast.',
      ],
    },
  },
}
