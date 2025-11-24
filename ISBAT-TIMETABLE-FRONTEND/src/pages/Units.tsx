import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { useState } from "react";

type Unit = {
  id: string;
  cohortCode: string;
  code: string;
  title: string;
  hoursPerWeek: number;
  type: "Theory" | "Lab";
};

export default function Units() {
  const [units, setUnits] = useState<Unit[]>([
    { id: "1", cohortCode: "BIT-S1", code: "CS101", title: "Programming Fundamentals", hoursPerWeek: 4, type: "Theory" },
    { id: "2", cohortCode: "BIT-S1", code: "CS102", title: "Data Structures", hoursPerWeek: 4, type: "Theory" },
    { id: "3", cohortCode: "BBA-S1", code: "BBA101", title: "Business Principles", hoursPerWeek: 3, type: "Theory" },
  ]);
  const [form, setForm] = useState<Omit<Unit, "id">>({
    cohortCode: "",
    code: "",
    title: "",
    hoursPerWeek: 0,
    type: "Theory",
  });

  const add = () => {
    if (!form.cohortCode || !form.code) return;
    setUnits([...units, { id: Date.now().toString(), ...form }]);
    setForm({ cohortCode: "", code: "", title: "", hoursPerWeek: 0, type: "Theory" });
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Units</h1>
          <p className="text-muted-foreground mt-1">Manage cohort-specific units and weekly hours</p>
        </div>
      </div>
      <Card className="p-4 glass-card">
        <div className="grid gap-3 sm:grid-cols-6">
          <Input placeholder="Cohort Code (e.g., BIT-S1)" value={form.cohortCode} onChange={(e) => setForm({ ...form, cohortCode: e.target.value })} />
          <Input placeholder="Unit Code" value={form.code} onChange={(e) => setForm({ ...form, code: e.target.value })} />
          <Input placeholder="Title" value={form.title} onChange={(e) => setForm({ ...form, title: e.target.value })} />
          <Input type="number" placeholder="Hours/Week" value={form.hoursPerWeek} onChange={(e) => setForm({ ...form, hoursPerWeek: parseInt(e.target.value) || 0 })} />
          <Input placeholder="Type (Theory/Lab)" value={form.type} onChange={(e) => setForm({ ...form, type: (e.target.value as Unit["type"]) })} />
          <Button onClick={add}>Add Unit</Button>
        </div>
      </Card>
      <Card className="p-4 glass-card">
        <div className="grid gap-2">
          {units.map((u) => (
            <div key={u.id} className="flex items-center justify-between p-3 rounded-lg bg-muted/40">
              <div className="flex items-center gap-3">
                <Badge variant="outline" className="bg-accent text-accent-foreground">{u.cohortCode}</Badge>
                <div className="font-medium">{u.code} — {u.title}</div>
              </div>
              <div className="text-sm text-muted-foreground">{u.hoursPerWeek}h · {u.type}</div>
            </div>
          ))}
        </div>
      </Card>
    </div>
  );
}


