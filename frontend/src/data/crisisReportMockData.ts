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
  orders: [
    { id: 'demo-order-101', orderNumber: 'DEMO-101', supplierId: 'northstar-components', product: 'Control boards', status: 'in_transit', destination: 'North warehouse' },
    { id: 'demo-order-102', orderNumber: 'DEMO-102', supplierId: 'pacific-freight', product: 'Industrial components', status: 'delayed', destination: 'West warehouse' },
    { id: 'demo-order-103', orderNumber: 'DEMO-103', supplierId: 'meridian-industrial', product: 'Precision sensors', status: 'confirmed', destination: 'Central warehouse' },
  ],
  urgencies: ['Low', 'Medium', 'High', 'Critical'],
}
