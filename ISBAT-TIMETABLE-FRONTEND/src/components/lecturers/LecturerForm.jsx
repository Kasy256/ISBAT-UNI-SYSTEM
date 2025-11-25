import { useState, useEffect } from "react";
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
import { X } from "lucide-react";

export function LecturerForm({
  open,
  onOpenChange,
  onSubmit,
  lecturer,
  availableCourses = [],
}) {
  const [formData, setFormData] = useState({
    id: "",
    name: "",
    role: "Full-Time",
    faculty: "",
    specializations: [],
    availability: null,
    sessions_per_day: 2,
    max_weekly_hours: 22,
  });

  useEffect(() => {
    if (lecturer) {
      setFormData({
        id: lecturer.id || "",
        name: lecturer.name || "",
        role: lecturer.role || "Full-Time",
        faculty: lecturer.faculty || "",
        specializations: lecturer.specializations || [],
        availability: lecturer.availability || null,
        sessions_per_day: lecturer.sessions_per_day || 2,
        max_weekly_hours: lecturer.max_weekly_hours || 22,
      });
    } else {
      // Reset form for new lecturer
      setFormData({
        id: "",
        name: "",
        role: "Full-Time",
        faculty: "",
        specializations: [],
        availability: null,
        sessions_per_day: 2,
        max_weekly_hours: 22,
      });
    }
  }, [lecturer, open]);

  const handleSubmit = (e) => {
    e.preventDefault();
    onSubmit(formData);
  };

  const toggleSpecialization = (courseId) => {
    setFormData((prev) => ({
      ...prev,
      specializations: prev.specializations.includes(courseId)
        ? prev.specializations.filter((id) => id !== courseId)
        : [...prev.specializations, courseId],
    }));
  };

  const getCourseDisplay = (courseId) => {
    const course = availableCourses.find(
      (c) => c.id === courseId || c.code === courseId
    );
    return course ? `${course.code} - ${course.name}` : courseId;
  };

  // Filter courses by faculty if faculty is selected
  const filteredCourses = formData.faculty
    ? availableCourses.filter(
        (c) => !c.faculty || c.faculty === formData.faculty
      )
    : availableCourses;

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-[600px] max-h-[90vh] overflow-y-auto">
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
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="id">Lecturer ID *</Label>
                <Input
                  id="id"
                  value={formData.id}
                  onChange={(e) =>
                    setFormData({ ...formData, id: e.target.value })
                  }
                  placeholder="L001"
                  required
                  disabled={!!lecturer} // Disable ID editing for existing lecturers
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="name">Name *</Label>
                <Input
                  id="name"
                  value={formData.name}
                  onChange={(e) =>
                    setFormData({ ...formData, name: e.target.value })
                  }
                  placeholder="Dr. Jane Doe"
                  required
                />
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="faculty">Faculty *</Label>
                <Input
                  id="faculty"
                  value={formData.faculty}
                  onChange={(e) =>
                    setFormData({ ...formData, faculty: e.target.value })
                  }
                  placeholder="Computing"
                  required
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="role">Role *</Label>
                <Select
                  value={formData.role}
                  onValueChange={(value) =>
                    setFormData({ ...formData, role: value })
                  }
                >
                  <SelectTrigger>
                    <SelectValue placeholder="Select role" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="Faculty Dean">Faculty Dean</SelectItem>
                    <SelectItem value="Full-Time">Full-Time</SelectItem>
                    <SelectItem value="Part-Time">Part-Time</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="sessions_per_day">Sessions per Day</Label>
                <Input
                  id="sessions_per_day"
                  type="number"
                  min="1"
                  max="4"
                  value={formData.sessions_per_day}
                  onChange={(e) =>
                    setFormData({
                      ...formData,
                      sessions_per_day: parseInt(e.target.value) || 2,
                    })
                  }
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="max_weekly_hours">Max Weekly Hours</Label>
                <Input
                  id="max_weekly_hours"
                  type="number"
                  min="1"
                  value={formData.max_weekly_hours}
                  onChange={(e) =>
                    setFormData({
                      ...formData,
                      max_weekly_hours: parseInt(e.target.value) || 22,
                    })
                  }
                />
                <p className="text-xs text-muted-foreground">
                  Auto-set based on role if not specified
                </p>
              </div>
            </div>

            <div className="space-y-2">
              <Label>Specializations *</Label>
              <div className="space-y-2">
                <Select
                  onValueChange={(value) => {
                    if (!formData.specializations.includes(value)) {
                      toggleSpecialization(value);
                    }
                  }}
                >
                  <SelectTrigger>
                    <SelectValue placeholder="Add course specialization" />
                  </SelectTrigger>
                  <SelectContent>
                    {filteredCourses
                      .filter(
                        (c) => !formData.specializations.includes(c.id) && !formData.specializations.includes(c.code)
                      )
                      .map((course) => (
                        <SelectItem
                          key={course.id}
                          value={course.id || course.code}
                        >
                          {course.code} - {course.name}
                        </SelectItem>
                      ))}
                  </SelectContent>
                </Select>
                {formData.specializations.length > 0 && (
                  <div className="flex flex-wrap gap-2 p-2 border rounded-md">
                    {formData.specializations.map((courseId) => (
                      <span
                        key={courseId}
                        className="inline-flex items-center gap-1 px-2 py-1 rounded-md bg-primary/10 text-primary text-xs"
                      >
                        {getCourseDisplay(courseId)}
                        <Button
                          type="button"
                          variant="ghost"
                          size="sm"
                          className="h-5 w-5 p-0"
                          onClick={() => toggleSpecialization(courseId)}
                          aria-label={`Remove ${getCourseDisplay(courseId)}`}
                        >
                          <X className="h-3 w-3" />
                        </Button>
                      </span>
                    ))}
                  </div>
                )}
              </div>
            </div>

            <div className="space-y-2">
              <Label>Availability (Optional)</Label>
              <p className="text-xs text-muted-foreground">
                Format: JSON object with day keys (MON, TUE, etc.) and time slot arrays (e.g., {"{"}"MON": ["09:00-11:00"]{"}"})
              </p>
              <Input
                placeholder='{"MON": ["09:00-11:00"], "TUE": ["14:00-16:00"]}'
                value={
                  formData.availability
                    ? JSON.stringify(formData.availability, null, 2)
                    : ""
                }
                onChange={(e) => {
                  try {
                    const parsed = e.target.value
                      ? JSON.parse(e.target.value)
                      : null;
                    setFormData({ ...formData, availability: parsed });
                  } catch {
                    // Invalid JSON, keep as is
                  }
                }}
              />
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
            <Button type="submit">
              {lecturer ? "Update" : "Add"} Lecturer
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}
