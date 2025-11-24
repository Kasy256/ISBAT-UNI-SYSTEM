import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { useState } from "react";

type Cohort = {
  id: string;
  program: string;
  code: string; // e.g., BIT-S1
  semester: string;
  term: string;
  studentCount: number;
};

export default function Cohorts() {
  const [cohorts, setCohorts] = useState<Cohort[]>([
    { id: "1", program: "Bachelor of Information Technology", code: "BIT-S1", semester: "Semester 1", term: "Term 1", studentCount: 95 },
    { id: "2", program: "Bachelor of Business Administration", code: "BBA-S1", semester: "Semester 1", term: "Term 1", studentCount: 120 },
  ]);
  const [form, setForm] = useState<Omit<Cohort, "id">>({
    program: "",
    code: "",
    semester: "",
    term: "",
    studentCount: 0,
  });

  const add = () => {
    if (!form.program || !form.code || !form.semester) return;
    setCohorts([...cohorts, { id: Date.now().toString(), ...form }]);
    setForm({ program: "", code: "", semester: "", term: "", studentCount: 0 });
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Cohorts & Units</h1>
          <p className="text-muted-foreground mt-1">Define teaching groups and capture unit load per cohort</p>
        </div>
      </div>
      <Card className="p-4 glass-card">
        <div className="grid gap-3 sm:grid-cols-5">
          <Input placeholder="Program" value={form.program} onChange={(e) => setForm({ ...form, program: e.target.value })} />
          <Input placeholder="Code (e.g., BIT-S1)" value={form.code} onChange={(e) => setForm({ ...form, code: e.target.value })} />
          <Input placeholder="Semester" value={form.semester} onChange={(e) => setForm({ ...form, semester: e.target.value })} />
          <Input placeholder="Term" value={form.term} onChange={(e) => setForm({ ...form, term: e.target.value })} />
          <Input type="number" placeholder="Students" value={form.studentCount} onChange={(e) => setForm({ ...form, studentCount: parseInt(e.target.value) || 0 })} />
        </div>
        <div className="mt-3">
          <Button onClick={add}>Add Cohort</Button>
        </div>
      </Card>
      <Card className="p-4 glass-card">
        <div className="grid gap-2">
          {cohorts.map((c) => (
            <div key={c.id} className="flex items-center justify-between p-3 rounded-lg bg-muted/40">
              <div>
                <div className="font-medium">{c.code} — {c.program}</div>
                <div className="text-xs text-muted-foreground">{c.semester} · {c.term} · {c.studentCount} students</div>
              </div>
            </div>
          ))}
        </div>
      </Card>
    </div>
  );
}


