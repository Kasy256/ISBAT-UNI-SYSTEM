import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { useState } from "react";

export default function Generate() {
  const [ready, setReady] = useState(false);
  const checklist = [
    { id: "lecturers", label: "Lecturers set up (roles, limits, availability)", done: true },
    { id: "rooms", label: "Rooms set up (capacity, type, specialization)", done: true },
    { id: "cohorts", label: "Cohorts defined with student counts", done: true },
    { id: "units", label: "Units per cohort with hours/week and type", done: true },
    { id: "rules", label: "Time blocks and rules confirmed", done: true },
  ];

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Generate Timetable</h1>
          <p className="text-muted-foreground mt-1">Run the engine to create a draft timetable (stubbed)</p>
        </div>
      </div>
      <Card className="p-6 glass-card">
        <h2 className="text-lg font-semibold">Pre-run Checklist</h2>
        <div className="mt-3 grid gap-2">
          {checklist.map((c) => (
            <div key={c.id} className="flex items-center gap-2">
              <Badge variant={c.done ? "default" : "destructive"}>{c.done ? "OK" : "Missing"}</Badge>
              <span className="text-sm">{c.label}</span>
            </div>
          ))}
        </div>
        <div className="mt-4 flex gap-2">
          <Button onClick={() => setReady(true)} disabled={!checklist.every((c) => c.done)}>
            Generate Draft
          </Button>
          <Button variant="outline">Adjust Soft Constraint Weights</Button>
        </div>
        {ready && <p className="text-sm text-green-600 mt-3">Draft created (placeholder). Open in Timetables.</p>}
      </Card>
    </div>
  );
}


