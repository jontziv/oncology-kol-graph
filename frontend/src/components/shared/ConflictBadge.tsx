import { cn, formatCurrency, paymentBadgeColor } from "@/lib/utils";
import { ShieldCheck, AlertTriangle, AlertCircle } from "lucide-react";

interface ConflictBadgeProps {
  totalUsd: number;
  companyCount: number;
  showLabel?: boolean;
  className?: string;
}

export function ConflictBadge({
  totalUsd,
  companyCount,
  showLabel = true,
  className,
}: ConflictBadgeProps) {
  const Icon =
    totalUsd === 0 ? ShieldCheck : totalUsd <= 10000 ? AlertTriangle : AlertCircle;

  return (
    <div
      className={cn(
        "inline-flex items-center gap-1.5 px-2 py-1 rounded border text-xs font-medium",
        paymentBadgeColor(totalUsd),
        className
      )}
      title="Source: CMS Open Payments (public database)"
    >
      <Icon className="w-3 h-3 flex-shrink-0" />
      {showLabel && (
        <span>
          {totalUsd === 0
            ? "No disclosed payments"
            : `${formatCurrency(totalUsd)} (${companyCount} co.)`}
        </span>
      )}
    </div>
  );
}
