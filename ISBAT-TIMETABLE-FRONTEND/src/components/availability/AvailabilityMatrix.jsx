import { useState } from "react";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";

const defaultBlocks = ["9-11", "11-1", "2-4", "4-6"];
const defaultDays = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"];

export default function AvailabilityMatrix({
  value,
  onChange,
  blocks = defaultBlocks,
  days = defaultDays,
}) {
  const [local, setLocal] = useState(
    value || Object.fromEntries(days.map((d) => [d, []]))
  );

  const toggle = (day, block) => {
    const next = { ...local };
    next[day] = next[day]?.includes(block)
      ? next[day].filter((b) => b !== block)
      : [...(next[day] || []), block];
    setLocal(next);
    onChange?.(next);
  };

  return (
    <Card className="p-4">
      <div className="grid grid-cols-[140px_repeat(4,minmax(0,1fr))] gap-2">
        <div />
        {blocks.map((b) => (
          <div key={b} className="text-xs font-medium text-muted-foreground text-center">
            {b}
          </div>
        ))}
        {days.map((day) => (
          <div key={day} className="contents">
            <div className="text-sm font-medium">{day}</div>
            {blocks.map((b) => {
              const active = local[day]?.includes(b);
              return (
                <button
                  key={b}
                  className={
                    "h-10 rounded border text-xs " +
                    (active
                      ? "bg-primary/10 border-primary/30 text-primary"
                      : "bg-muted/30 border-border hover:bg-accent/30")
                  }
                  onClick={() => toggle(day, b)}
                >
                  {active ? "Available" : "Unavailable"}
                </button>
              );
            })}
          </div>
        ))}
      </div>
      <div className="mt-3 flex items-center gap-3">
        <Badge variant="outline" className="bg-primary/10 text-primary border-primary/20">
          Click cells to toggle availability
        </Badge>
      </div>
    </Card>
  );
}

