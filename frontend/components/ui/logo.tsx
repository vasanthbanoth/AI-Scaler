import Link from "next/link";
import { cn } from "@/lib/utils";

export function Logo({ className, dark }: { className?: string; dark?: boolean }) {
  return (
    <Link href="/" className={cn("flex items-center gap-2.5", className)}>
      <span
        className={cn(
          "flex h-8 w-8 items-center justify-center rounded-md text-xs font-bold tracking-tight",
          dark ? "bg-white text-slate-900" : "bg-slate-900 text-white"
        )}
      >
        VB
      </span>
      <span className={cn("font-semibold tracking-tight", dark ? "text-white" : "text-slate-900")}>
        Vasanth Banoth
      </span>
    </Link>
  );
}
