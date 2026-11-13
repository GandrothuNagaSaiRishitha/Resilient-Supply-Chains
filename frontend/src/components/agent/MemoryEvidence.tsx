type MemoryEvidenceProps = {
  hits: Array<{ id: string | null; text: string; score: number | null; metadata: Record<string, unknown> }>
}

export function MemoryEvidence({ hits }: MemoryEvidenceProps) {
  return (
    <div className="mt-2 rounded-xl border border-amber-200 bg-amber-50 px-3 py-2">
      <div className="mb-2 flex items-center gap-2">
        <span className="text-[10px] font-bold uppercase tracking-[0.12em] text-amber-700">
          Hindsight evidence
        </span>
        <span className="rounded-full bg-amber-200 px-2 py-0.5 text-[10px] font-medium text-amber-800">
          {hits.length}
        </span>
      </div>
      <ul className="space-y-2">
        {hits.map((hit) => (
          <li key={hit.id ?? hit.text} className="rounded-lg bg-white px-2.5 py-1.5 border border-amber-200">
            <p className="text-[10px] text-slate-500">Score {hit.score?.toFixed(3)}</p>
            <p className="text-[11px] text-slate-700 truncate">{hit.text}</p>
            {hit.metadata.crisis_type && (
              <p className="text-[9px] text-amber-600">{hit.metadata.crisis_type as string}</p>
            )}
          </li>
        ))}
      </ul>
    </div>
  )
}
