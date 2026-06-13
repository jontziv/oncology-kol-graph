import { cn, scoreBg } from "@/lib/utils";

interface ScoreBadgeProps {
  label: string;
  score: number;
  className?: string;
}

export function ScoreBadge({ label, score, className }: ScoreBadgeProps) {
  return (
    <div className={cn("flex flex-col items-center gap-0.5", className)}>
      <span className="text-xs text-slate-400">{label}</span>
      <span
        className={cn(
          "text-sm font-semibold px-2 py-0.5 rounded border",
          scoreBg(score)
        )}
      >
        {score.toFixed(0)}
      </span>
    </div>
  );
}
