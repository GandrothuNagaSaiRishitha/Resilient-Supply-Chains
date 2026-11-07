import type { CrisisReportFormOptions } from '../types/crisisReport'

export const crisisReportFormOptions: CrisisReportFormOptions = {
  crisisTypes: [
    'Shipment Disruption',
    'Supplier Failure',
    'Inventory Shortage',
  ],
  suppliers: [
    { id: 'northstar-components', name: 'Northstar Components' },
    { id: 'pacific-freight', name: 'Pacific Freight Group' },
    { id: 'meridian-industrial', name: 'Meridian Industrial Supply' },
    { id: 'atlas-global-logistics', name: 'Atlas Global Logistics' },
  ],
  urgencies: ['Low', 'Medium', 'High', 'Critical'],
}
