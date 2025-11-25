import { useSemester } from "@/context/SemesterContext";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Calendar } from "lucide-react";

export default function SemesterSwitcher() {
  const { current, setSemester, available } = useSemester();
  return (
    <div className="flex items-center gap-2">
      <div className="flex items-center gap-2">
        <div className="inline-flex h-8 w-8 items-center justify-center rounded-md bg-primary/10">
          <Calendar className="h-4 w-4 text-primary" />
        </div>
        <span className="text-sm text-muted-foreground hidden sm:inline">Semester</span>
      </div>
      <Select
        value={current.id}
        onValueChange={(id) => {
          const sel = available.find((s) => s.id === id);
          if (sel) setSemester(sel);
        }}
      >
        <SelectTrigger className="w-[200px]">
          <SelectValue placeholder="Select semester" />
        </SelectTrigger>
        <SelectContent>
          {available.map((s) => (
            <SelectItem key={s.id} value={s.id}>
              {s.label}
            </SelectItem>
          ))}
        </SelectContent>
      </Select>
    </div>
  );
}

