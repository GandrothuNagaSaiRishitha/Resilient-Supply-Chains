import type { ReactNode } from 'react'

type FormFieldProps = {
  label: string
  htmlFor: string
  required?: boolean
  hint?: string
  children: ReactNode
}

export default function FormField({
  label,
  htmlFor,
  required = false,
  hint,
  children,
}: FormFieldProps) {
  const hintId = hint ? `${htmlFor}-hint` : undefined

  return (
    <div className="min-w-0">
      <label
        htmlFor={htmlFor}
        className="mb-1.5 block text-xs font-semibold text-slate-700"
      >
        {label}
        {required && <span className="ml-1 text-rose-500" aria-hidden="true">*</span>}
      </label>
      {children}
      {hint && (
        <p id={hintId} className="mt-1.5 text-[11px] leading-5 text-slate-400">
          {hint}
        </p>
      )}
    </div>
  )
}
