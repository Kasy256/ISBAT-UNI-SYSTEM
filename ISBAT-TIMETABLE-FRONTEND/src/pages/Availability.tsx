import { Card } from "@/components/ui/card";
import AvailabilityMatrix from "@/components/availability/AvailabilityMatrix";
import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";

export default function Availability() {
  const [availability, setAvailability] = useState<Record<string, string[]>>({});

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Availability & Rules</h1>
          <p className="text-muted-foreground mt-1">Define standard time blocks and lecturer availability</p>
        </div>
      </div>
      <Card className="p-4 glass-card">
        <div className="mb-3 text-sm">
          <Badge variant="secondary">Blocks</Badge>{" "}
          <span className="text-muted-foreground">9–11, 11–1, 2–4, 4–6 (editable later)</span>
        </div>
        <AvailabilityMatrix value={availability} onChange={setAvailability} />
        <div className="mt-4">
          <Button variant="default">Save Availability</Button>
        </div>
      </Card>
    </div>
  );
}


