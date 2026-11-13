type ToolCallTraceProps = {
  traces: Array<{
    name: string
    arguments: Record<string, unknown>
    result_summary: string | null
    ok: boolean
    duration_ms: number | null
  }>
}

export function ToolCallTrace({ traces }: ToolCallTraceProps) {
  return (
    <div className="mt-2 rounded-xl border border-slate-200 bg-slate-50 px-3 py-2">
      <div className="mb-2 flex items-center gap-2">
        <span className="text-[10px] font-bold uppercase tracking-[0.12em] text-slate-500">
          Tool calls
        </span>
        <span className="rounded-full bg-slate-200 px-2 py-0.5 text-[10px] font-medium text-slate-700">
          {traces.length}
        </span>
      </div>
      <ul className="space-y-2">
        {traces.map((trace, index) => (
          <li key={index} className="rounded-lg bg-white px-2 py-1.5 border border-slate-200">
            <div className="flex items-center justify-between text-xs">
              <span className="font-mono text-slate-700">{trace.name}</span>
              <span className="text-slate-400">
                {trace.ok ? 'OK' : 'Failed'}
              </span>
            </div>
            {trace.result_summary && (
              <p className="mt-1 text-[10px] text-slate-500 truncate">{trace.result_summary}</p>
            )}
          </li>
        ))}
      </ul>
    </div>
  )
}
