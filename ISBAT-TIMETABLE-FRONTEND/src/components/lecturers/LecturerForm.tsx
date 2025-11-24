import { useState } from "react";
import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Lecturer } from "@/types/lecturer";
import { X } from "lucide-react";

interface LecturerFormProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onSubmit: (lecturer: Omit<Lecturer, "id">) => void;
  lecturer?: Lecturer;
  availableUnits: Array<{ id: string; code: string; title: string; faculty?: string }>;
}

export function LecturerForm({
  open,
  onOpenChange,
  onSubmit,
  lecturer,
  availableUnits,
}: LecturerFormProps) {
  const [formData, setFormData] = useState<Omit<Lecturer, "id">>({
    name: lecturer?.name || "",
    faculty: lecturer?.faculty || "Computer Science",
    role: lecturer?.role || "Lecturer",
    specializations: lecturer?.specializations || [],
    maxHours: lecturer?.maxHours || 20,
  });

  const [selectedUnits, setSelectedUnits] = useState<string[]>(
    lecturer?.specializations || []
  );

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSubmit({ ...formData, specializations: selectedUnits });
    onOpenChange(false);
  };

  const toggleUnit = (unitId: string) => {
    setSelectedUnits((prev) =>
      prev.includes(unitId)
        ? prev.filter((id) => id !== unitId)
        : [...prev, unitId]
    );
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-[500px]">
        <DialogHeader>
          <DialogTitle>
            {lecturer ? "Edit Lecturer" : "Add Lecturer"}
          </DialogTitle>
          <DialogDescription>
            {lecturer
              ? "Update lecturer information"
              : "Add a new lecturer to the system"}
          </DialogDescription>
        </DialogHeader>
        <form onSubmit={handleSubmit}>
          <div className="space-y-4 py-4">
            <div className="space-y-2">
              <Label htmlFor="name">Name</Label>
              <Input
                id="name"
                value={formData.name}
                onChange={(e) =>
                  setFormData({ ...formData, name: e.target.value })
                }
                placeholder="Dr. Sarah Johnson"
                required
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="faculty">Faculty</Label>
              <Select
                value={formData.faculty}
                onValueChange={(value) =>
                  setFormData({ ...formData, faculty: value })
                }
              >
                <SelectTrigger>
                  <SelectValue placeholder="Select faculty" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="Computer Science">Computer Science</SelectItem>
                  <SelectItem value="Business">Business</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-2">
              <Label htmlFor="role">Role</Label>
              <Select
                value={formData.role}
                onValueChange={(value) =>
                  setFormData({ ...formData, role: value as Lecturer["role"] })
                }
              >
                <SelectTrigger>
                  <SelectValue placeholder="Select role" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="Professor">Professor</SelectItem>
                  <SelectItem value="Lecturer">Lecturer</SelectItem>
                  <SelectItem value="Assistant">Assistant</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-2">
              <Label>Specializations</Label>
              <div className="space-y-2">
                <Select
                  onValueChange={(value) => {
                    if (!selectedUnits.includes(value)) {
                      setSelectedUnits([...selectedUnits, value]);
                    }
                  }}
                >
                  <SelectTrigger>
                    <SelectValue placeholder="Add specialization" />
                  </SelectTrigger>
                  <SelectContent>
                    {(availableUnits || [])
                      .filter((u) => !u.faculty || u.faculty === formData.faculty)
                      .map((unit) => (
                        <SelectItem key={unit.id} value={unit.id}>
                          {unit.code} - {unit.title}
                        </SelectItem>
                      ))}
                  </SelectContent>
                </Select>
                {selectedUnits.length > 0 && (
                  <div className="flex flex-wrap gap-2">
                    {selectedUnits.map((id) => {
                      const unit = (availableUnits || []).find((u) => u.id === id);
                      const label = unit ? `${unit.code} - ${unit.title}` : id;
                      return (
                        <span key={id} className="inline-flex items-center gap-1 px-2 py-1 rounded-md bg-primary/10 text-primary text-xs">
                          {label}
                          <Button
                            type="button"
                            variant="ghost"
                            size="sm"
                            className="h-5 w-5 p-0"
                            onClick={() => toggleUnit(id)}
                            aria-label={`Remove ${label}`}
                          >
                            <X className="h-3 w-3" />
                          </Button>
                        </span>
                      );
                    })}
                  </div>
                )}
              </div>
            </div>

            <div className="space-y-2">
              <Label htmlFor="maxHours">Max Hours/Week</Label>
              <Input
                id="maxHours"
                type="number"
                min="1"
                max="40"
                value={formData.maxHours}
                onChange={(e) =>
                  setFormData({
                    ...formData,
                    maxHours: parseInt(e.target.value),
                  })
                }
                required
              />
            </div>
          </div>
          <DialogFooter>
            <Button type="button" variant="outline" onClick={() => onOpenChange(false)}>
              Cancel
            </Button>
            <Button type="submit">
              {lecturer ? "Update" : "Add"} Lecturer
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}
