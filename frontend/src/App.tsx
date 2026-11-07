import { Navigate, Route, Routes } from 'react-router-dom'
import Layout from './components/Layout'
import DashboardPage from './pages/DashboardPage'
import DecisionReportPage from './pages/DecisionReportPage'
import DecisionReplay from './pages/DecisionReplay/DecisionReplay'
import ImpactAnalysisPage from './pages/ImpactAnalysisPage'
import MemoryCentrePage from './pages/MemoryCentrePage'
import RecoverySimulatorPage from './pages/RecoverySimulatorPage'
import ReportCrisisPage from './pages/ReportCrisisPage'

function App() {
  return (
    <Routes>
      <Route element={<Layout />}>
        <Route index element={<Navigate to="/dashboard" replace />} />
        <Route path="/dashboard" element={<DashboardPage />} />
        <Route path="/report-crisis" element={<ReportCrisisPage />} />
        <Route path="/impact-analysis" element={<ImpactAnalysisPage />} />
        <Route path="/recovery-simulator" element={<RecoverySimulatorPage />} />
        <Route path="/memory-centre" element={<MemoryCentrePage />} />
        <Route path="/decision-report" element={<DecisionReportPage />} />
        <Route path="/decision-replay" element={<DecisionReplay />} />
        <Route path="*" element={<Navigate to="/dashboard" replace />} />
      </Route>
    </Routes>
  )
}

export default App
