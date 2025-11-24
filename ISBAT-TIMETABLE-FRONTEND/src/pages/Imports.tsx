import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";

export default function Imports() {
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Imports</h1>
          <p className="text-muted-foreground mt-1">Import data from CSV/Excel templates</p>
        </div>
      </div>
      <div className="grid gap-4 md:grid-cols-3">
        {[
          { title: "Lecturers", desc: "Name, Role, Specializations, Limits, Availability" },
          { title: "Rooms", desc: "Room, Type, Capacity, Specialization" },
          { title: "Cohorts & Units", desc: "Program, Cohort, Units, Hours/Week, Type" },
        ].map((item) => (
          <Card key={item.title} className="p-6 glass-card">
            <div className="flex items-start justify-between">
              <div>
                <h2 className="text-lg font-semibold">{item.title}</h2>
                <p className="text-sm text-muted-foreground mt-1">{item.desc}</p>
              </div>
              <Badge variant="secondary">CSV/XLSX</Badge>
            </div>
            <div className="mt-4 flex gap-2">
              <Button variant="outline">Download Template</Button>
              <Button>Upload File</Button>
            </div>
          </Card>
        ))}
      </div>
    </div>
  );
}


