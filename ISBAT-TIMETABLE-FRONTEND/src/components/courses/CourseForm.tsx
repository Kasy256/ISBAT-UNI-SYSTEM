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
import { Course, CourseUnit } from "@/types/course";
import { Plus, Trash } from "lucide-react";

interface CourseFormProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onSubmit: (course: Omit<Course, "id">) => void;
  course?: Course;
}

export function CourseForm({
  open,
  onOpenChange,
  onSubmit,
  course,
}: CourseFormProps) {
  const [formData, setFormData] = useState<Omit<Course, "id">>({
    name: course?.name || "",
    faculty: course?.faculty || "",
    semester: course?.semester || "",
    term: course?.term || "",
    students: course?.students || 0,
    units: course?.units || [],
  });

  const [units, setUnits] = useState<CourseUnit[]>(
    course?.units || [{ code: "", title: "", hoursPerWeek: 0 }]
  );

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSubmit({ ...formData, units });
    onOpenChange(false);
  };

  const addUnit = () => {
    setUnits([...units, { code: "", title: "", hoursPerWeek: 0 }]);
  };

  const removeUnit = (index: number) => {
    setUnits(units.filter((_, i) => i !== index));
  };

  const updateUnit = (index: number, field: keyof CourseUnit, value: string | number) => {
    const newUnits = [...units];
    newUnits[index] = { ...newUnits[index], [field]: value };
    setUnits(newUnits);
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-[600px] max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>{course ? "Edit Course" : "Add Course"}</DialogTitle>
          <DialogDescription>
            {course
              ? "Update course information and units"
              : "Add a new course to the system"}
          </DialogDescription>
        </DialogHeader>
        <form onSubmit={handleSubmit}>
          <div className="space-y-4 py-4">
            <div className="space-y-2">
              <Label htmlFor="name">Course Name</Label>
              <Input
                id="name"
                value={formData.name}
                onChange={(e) =>
                  setFormData({ ...formData, name: e.target.value })
                }
                placeholder="Bachelor of Information Technology"
                required
              />
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="faculty">Faculty</Label>
                <Input
                  id="faculty"
                  value={formData.faculty}
                  onChange={(e) =>
                    setFormData({ ...formData, faculty: e.target.value })
                  }
                  placeholder="Computer Science"
                  required
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="students">Student Count</Label>
                <Input
                  id="students"
                  type="number"
                  min="1"
                  value={formData.students}
                  onChange={(e) =>
                    setFormData({
                      ...formData,
                      students: parseInt(e.target.value),
                    })
                  }
                  required
                />
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="semester">Semester</Label>
                <Input
                  id="semester"
                  value={formData.semester}
                  onChange={(e) =>
                    setFormData({ ...formData, semester: e.target.value })
                  }
                  placeholder="Semester 1"
                  required
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="term">Term</Label>
                <Input
                  id="term"
                  value={formData.term}
                  onChange={(e) =>
                    setFormData({ ...formData, term: e.target.value })
                  }
                  placeholder="Term 1"
                  required
                />
              </div>
            </div>

            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <Label>Course Units</Label>
                <Button
                  type="button"
                  variant="outline"
                  size="sm"
                  onClick={addUnit}
                >
                  <Plus className="h-4 w-4 mr-1" />
                  Add Unit
                </Button>
              </div>

              <div className="space-y-3 max-h-64 overflow-y-auto p-1">
                {units.map((unit, index) => (
                  <div
                    key={index}
                    className="border rounded-lg p-3 space-y-2 bg-muted/30"
                  >
                    <div className="flex justify-between items-center mb-2">
                      <span className="text-sm font-medium">
                        Unit {index + 1}
                      </span>
                      {units.length > 1 && (
                        <Button
                          type="button"
                          variant="ghost"
                          size="sm"
                          onClick={() => removeUnit(index)}
                        >
                          <Trash className="h-4 w-4 text-destructive" />
                        </Button>
                      )}
                    </div>

                    <div className="grid grid-cols-2 gap-2">
                      <Input
                        placeholder="Code (e.g., CS101)"
                        value={unit.code}
                        onChange={(e) =>
                          updateUnit(index, "code", e.target.value)
                        }
                        required
                      />
                      <Input
                        placeholder="Hours/Week"
                        type="number"
                        min="1"
                        value={unit.hoursPerWeek}
                        onChange={(e) =>
                          updateUnit(
                            index,
                            "hoursPerWeek",
                            parseInt(e.target.value)
                          )
                        }
                        required
                      />
                    </div>
                    <Input
                      placeholder="Title (e.g., Programming Fundamentals)"
                      value={unit.title}
                      onChange={(e) => updateUnit(index, "title", e.target.value)}
                      required
                    />
                  </div>
                ))}
              </div>
            </div>
          </div>
          <DialogFooter>
            <Button
              type="button"
              variant="outline"
              onClick={() => onOpenChange(false)}
            >
              Cancel
            </Button>
            <Button type="submit">{course ? "Update" : "Add"} Course</Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}
