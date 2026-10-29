/** Eight-point spark for 点亮八年级. Not the upstream compass. */
const SPARK =
  "M16 6.65 L17.42 12.58 L22.61 9.39 L19.42 14.58 L25.35 16 L19.42 17.42 L22.61 22.61 L17.42 19.42 L16 25.35 L14.58 19.42 L9.39 22.61 L12.58 17.42 L6.65 16 L12.58 14.58 L9.39 9.39 L14.58 12.58 Z";

export function Mark({ size = 28 }: { size?: number }) {
  return (
    <svg width={size} height={size} viewBox="0 0 32 32" aria-hidden="true" className="mark">
      <rect x="1" y="1" width="30" height="30" rx="8" fill="currentColor" />
      <path className="mark-spark" d={SPARK} fill="var(--ochre)" />
      <circle cx="16" cy="16" r="1.7" fill="var(--paper)" />
    </svg>
  );
}

export function Logo({ compact = false }: { compact?: boolean }) {
  return (
    <span className="logo">
      <Mark />
      <span className="logo-text">
        <b>点亮八年级</b>
        {!compact && <small>外研版</small>}
      </span>
    </span>
  );
}
