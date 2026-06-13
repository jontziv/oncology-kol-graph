import { cn } from "@/lib/utils";

interface LoadingSpinnerProps {
  className?: string;
  size?: "sm" | "md" | "lg";
}

export function LoadingSpinner({ className, size = "md" }: LoadingSpinnerProps) {
  const sizes = { sm: "w-4 h-4", md: "w-6 h-6", lg: "w-10 h-10" };
  return (
    <div
      className={cn(
        "animate-spin rounded-full border-2 border-slate-600 border-t-sky-400",
        sizes[size],
        className
      )}
    />
  );
}

export function LoadingOverlay({ label = "Loading..." }: { label?: string }) {
  return (
    <div className="flex flex-col items-center justify-center gap-3 py-16 text-slate-400">
      <LoadingSpinner size="lg" />
      <span className="text-sm">{label}</span>
    </div>
  );
}
