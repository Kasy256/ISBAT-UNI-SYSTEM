import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { Card as UICard } from "@/components/ui/card";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Input } from "@/components/ui/input";
import { useSemester } from "@/context/SemesterContext";

type Draft = {
  id: string;
  name: string;
  createdAt: string;
  conflicts: number;
  utilization: number; // %
  status: "draft" | "published";
  semester?: string;
  term?: string;
  faculty?: string;
};

export default function Timetables() {
  const navigate = useNavigate();
  const { current } = useSemester();
  const [drafts, setDrafts] = useState<Draft[]>([
    { id: "d1", name: "Draft A", createdAt: "2025-01-05 10:24", conflicts: 0, utilization: 82, status: "draft" },
    { id: "d2", name: "Draft B", createdAt: "2025-01-04 16:10", conflicts: 3, utilization: 79, status: "draft" },
  ]);
  const [showPrecheck, setShowPrecheck] = useState(false);
  const [form, setForm] = useState<{ semester: string; term: string; faculty: string }>({
    semester: "Semester 1",
    term: "Term 1",
    faculty: "All Faculties",
  });
  const checklist = [
    { id: "lecturers", label: "Lecturers set up (roles, limits, availability)", done: true },
    { id: "rooms", label: "Rooms set up (capacity, type, specialization)", done: true },
    { id: "courses", label: "Courses with units and hours/week", done: true },
  ];

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Timetables</h1>
          <p className="text-muted-foreground mt-1">Manage generated drafts and publish versions</p>
        </div>
        <Button onClick={() => setShowPrecheck(true)}>Generate New Timetable</Button>
      </div>
      {showPrecheck && (
        <UICard className="p-6 glass-card">
          <h2 className="text-lg font-semibold">Pre-run Checklist</h2>
          <div className="mt-4 grid gap-4 sm:grid-cols-3">
            <div className="space-y-2">
              <label className="text-sm font-medium">Semester</label>
              <Select
                value={form.semester}
                onValueChange={(v) => setForm({ ...form, semester: v })}
              >
                <SelectTrigger>
                  <SelectValue placeholder="Select semester" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="Semester 1">Semester 1</SelectItem>
                  <SelectItem value="Semester 2">Semester 2</SelectItem>
                  <SelectItem value="Semester 3">Semester 3</SelectItem>
                  <SelectItem value="Semester 4">Semester 4</SelectItem>
                  <SelectItem value="Semester 5">Semester 5</SelectItem>
                  <SelectItem value="Semester 6">Semester 6</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div className="space-y-2">
              <label className="text-sm font-medium">Term</label>
              <Select
                value={form.term}
                onValueChange={(v) => setForm({ ...form, term: v })}
              >
                <SelectTrigger>
                  <SelectValue placeholder="Select term" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="Term 1">Term 1</SelectItem>
                  <SelectItem value="Term 2">Term 2</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div className="space-y-2">
              <label className="text-sm font-medium">Faculty</label>
              <Select
                value={form.faculty}
                onValueChange={(v) => setForm({ ...form, faculty: v })}
              >
                <SelectTrigger>
                  <SelectValue placeholder="Select faculty" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="All Faculties">All Faculties</SelectItem>
                  <SelectItem value="Computer Science">Computer Science</SelectItem>
                  <SelectItem value="Business">Business</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>
          <div className="mt-3 grid gap-2">
            {checklist.map((c) => (
              <div key={c.id} className="flex items-center gap-2">
                <Badge variant={c.done ? "default" : "destructive"}>{c.done ? "OK" : "Missing"}</Badge>
                <span className="text-sm">{c.label}</span>
              </div>
            ))}
          </div>
          <div className="mt-4 flex gap-2">
            <Button
              disabled={!checklist.every((c) => c.done) || !form.semester || !form.term}
              onClick={() => {
                const id = `d${Date.now()}`;
                setDrafts([
                  ...drafts,
                  {
                    id,
                    name: `${form.faculty === "All Faculties" ? "Master" : form.faculty} · ${form.semester} · ${form.term}`,
                    createdAt: new Date().toISOString().slice(0, 16).replace("T", " "),
                    conflicts: 0,
                    utilization: 0,
                    status: "draft",
                    semester: form.semester,
                    term: form.term,
                    faculty: form.faculty,
                  },
                ]);
                setShowPrecheck(false);
              }}
            >
              Create Draft
            </Button>
            <Button variant="outline" onClick={() => setShowPrecheck(false)}>Cancel</Button>
          </div>
        </UICard>
      )}
      <Card className="p-4 glass-card">
        <div className="grid gap-2">
          {drafts.map((d) => (
            <div key={d.id} className="flex items-center justify-between p-3 rounded-lg bg-muted/40">
              <div className="flex items-center gap-3">
                <div className="font-medium">{d.name}</div>
                <Badge variant={d.conflicts ? "destructive" : "default"}>
                  {d.conflicts ? `${d.conflicts} conflicts` : "No conflicts"}
                </Badge>
                <Badge variant="secondary">{d.utilization}% utilization</Badge>
              </div>
              <div className="flex items-center gap-2">
                <span className="text-xs text-muted-foreground">{d.createdAt}</span>
                <Button variant="outline" size="sm" onClick={() => navigate("/timetable")}>
                  Open
                </Button>
                <Button size="sm">Publish</Button>
              </div>
            </div>
          ))}
        </div>
      </Card>
    </div>
  );
}


