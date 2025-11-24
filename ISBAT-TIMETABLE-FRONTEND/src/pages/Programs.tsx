import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { useState } from "react";

type Program = { id: string; name: string; faculty: string };

export default function Programs() {
  const [programs, setPrograms] = useState<Program[]>([
    { id: "1", name: "Bachelor of Information Technology", faculty: "Computer Studies" },
    { id: "2", name: "Bachelor of Business Administration", faculty: "Business" },
  ]);
  const [name, setName] = useState("");
  const [faculty, setFaculty] = useState("");

  const add = () => {
    if (!name || !faculty) return;
    setPrograms([...programs, { id: Date.now().toString(), name, faculty }]);
    setName("");
    setFaculty("");
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Programs</h1>
          <p className="text-muted-foreground mt-1">Manage degree and diploma programs</p>
        </div>
      </div>
      <Card className="p-4 glass-card">
        <div className="grid gap-3 sm:grid-cols-3">
          <Input placeholder="Program name" value={name} onChange={(e) => setName(e.target.value)} />
          <Input placeholder="Faculty" value={faculty} onChange={(e) => setFaculty(e.target.value)} />
          <Button onClick={add}>Add Program</Button>
        </div>
      </Card>
      <Card className="p-4 glass-card">
        <div className="grid gap-2">
          {programs.map((p) => (
            <div key={p.id} className="flex items-center justify-between p-3 rounded-lg bg-muted/40">
              <div>
                <div className="font-medium">{p.name}</div>
                <div className="text-xs text-muted-foreground">{p.faculty}</div>
              </div>
            </div>
          ))}
        </div>
      </Card>
    </div>
  );
}


