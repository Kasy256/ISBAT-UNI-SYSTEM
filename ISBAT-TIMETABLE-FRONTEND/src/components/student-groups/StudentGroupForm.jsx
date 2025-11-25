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
import { Checkbox } from "@/components/ui/checkbox";
import { X } from "lucide-react";

export function StudentGroupForm({
  open,
  onOpenChange,
  onSubmit,
  group,
  availableCourses = [],
}) {
  const [formData, setFormData] = useState({
    id: "",
    batch: "",
    program: "",
    semester: "",
    term: "",
    size: 0,
    course_units: [],
    is_active: true,
  });

  useEffect(() => {
    if (group) {
      // Normalize course_units - convert objects to IDs if needed
      const normalizedCourseUnits = (group.course_units || []).map((cu) => {
        if (typeof cu === 'object' && cu !== null) {
          return cu.code || cu.id || cu;
        }
        return cu;
      });
      
      setFormData({
        id: group.id || "",
        batch: group.batch || "",
        program: group.program || "",
        semester: group.semester || "",
        term: group.term || "Term1", // Default to Term1 if not set
        size: group.size || 0,
        course_units: normalizedCourseUnits,
        is_active: group.is_active !== undefined ? group.is_active : true,
      });
    } else {
      // Reset form for new group
      setFormData({
        id: "",
        batch: "",
        program: "",
        semester: "",
        term: "Term1", // Default to Term1 for new groups
        size: 0,
        course_units: [],
        is_active: true,
      });
    }
  }, [group, open]);

  const handleSubmit = (e) => {
    e.preventDefault();
    onSubmit(formData);
  };

  const toggleCourse = (courseId) => {
    setFormData((prev) => {
      // Normalize course_units for comparison
      const normalizedUnits = prev.course_units.map((cu) => {
        if (typeof cu === 'object' && cu !== null) {
          return cu.code || cu.id || cu;
        }
        return cu;
      });
      
      const isIncluded = normalizedUnits.includes(courseId);
      
      return {
        ...prev,
        course_units: isIncluded
          ? prev.course_units.filter((cu) => {
              const normalized = typeof cu === 'object' && cu !== null
                ? (cu.code || cu.id || cu)
                : cu;
              return normalized !== courseId;
            })
          : [...prev.course_units, courseId],
      };
    });
  };

  const getCourseDisplay = (courseIdOrObj) => {
    // Handle both string IDs and object {code, name}
    if (typeof courseIdOrObj === 'object' && courseIdOrObj !== null) {
      return `${courseIdOrObj.code || ''} - ${courseIdOrObj.name || ''}`;
    }
    const course = availableCourses.find(
      (c) => c.id === courseIdOrObj || c.code === courseIdOrObj
    );
    return course ? `${course.code} - ${course.name}` : courseIdOrObj;
  };

  // Filter courses by program if program is selected
  const filteredCourses = formData.program
    ? availableCourses.filter(
        (c) => !c.program || c.program === formData.program
      )
    : availableCourses;

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-[700px] max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>
            {group ? "Edit Student Group" : "Add Student Group"}
          </DialogTitle>
          <DialogDescription>
            {group
              ? "Update student group information"
              : "Create a new student group and assign courses"}
          </DialogDescription>
        </DialogHeader>
        <form onSubmit={handleSubmit}>
          <div className="space-y-4 py-4">
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="id">Group ID *</Label>
                <Input
                  id="id"
                  value={formData.id}
                  onChange={(e) =>
                    setFormData({ ...formData, id: e.target.value })
                  }
                  placeholder="SG_BSCAIT_S126_S1_T1"
                  required
                  disabled={!!group} // Disable ID editing for existing groups
                />
                <p className="text-xs text-muted-foreground">
                  Format: SG_PROGRAM_BATCH_SEMESTER_TERM
                </p>
              </div>
              <div className="space-y-2">
                <Label htmlFor="batch">Batch *</Label>
                <Input
                  id="batch"
                  value={formData.batch}
                  onChange={(e) =>
                    setFormData({ ...formData, batch: e.target.value })
                  }
                  placeholder="BSCAIT-126"
                  required
                />
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="program">Program *</Label>
                <Input
                  id="program"
                  value={formData.program}
                  onChange={(e) =>
                    setFormData({ ...formData, program: e.target.value })
                  }
                  placeholder="BSCAIT"
                  required
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="semester">Semester *</Label>
                <Select
                  value={formData.semester}
                  onValueChange={(value) =>
                    setFormData({ ...formData, semester: value })
                  }
                >
                  <SelectTrigger>
                    <SelectValue placeholder="Select semester" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="S1">S1</SelectItem>
                    <SelectItem value="S2">S2</SelectItem>
                    <SelectItem value="S3">S3</SelectItem>
                    <SelectItem value="S4">S4</SelectItem>
                    <SelectItem value="S5">S5</SelectItem>
                    <SelectItem value="S6">S6</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>

            <div className="space-y-2">
              <Label htmlFor="size">Group Size *</Label>
                <Input
                  id="size"
                  type="number"
                  min="1"
                  value={formData.size}
                  onChange={(e) =>
                    setFormData({
                      ...formData,
                      size: parseInt(e.target.value) || 0,
                    })
                  }
                  required
                />
            </div>

            <div className="space-y-2">
              <Label>Course Units *</Label>
              <div className="space-y-2">
                <Select
                  onValueChange={(value) => {
                    if (!formData.course_units.includes(value)) {
                      toggleCourse(value);
                    }
                  }}
                >
                  <SelectTrigger>
                    <SelectValue placeholder="Add course unit" />
                  </SelectTrigger>
                  <SelectContent>
                    {filteredCourses
                      .filter((c) => {
                        // Check if course is already in course_units
                        const courseId = c.id || c.code;
                        return !formData.course_units.some((cu) => {
                          if (typeof cu === 'object' && cu !== null) {
                            return (cu.code === courseId || cu.id === courseId);
                          }
                          return cu === courseId;
                        });
                      })
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
                {formData.course_units.length > 0 && (
                  <div className="flex flex-wrap gap-2 p-2 border rounded-md">
                    {formData.course_units.map((courseIdOrObj, index) => {
                      // Get a unique key
                      const key = typeof courseIdOrObj === 'object' && courseIdOrObj !== null
                        ? (courseIdOrObj.code || courseIdOrObj.id || index)
                        : (courseIdOrObj || index);
                      // Get the actual ID for toggling
                      const courseId = typeof courseIdOrObj === 'object' && courseIdOrObj !== null
                        ? (courseIdOrObj.code || courseIdOrObj.id)
                        : courseIdOrObj;
                      
                      return (
                        <span
                          key={key}
                          className="inline-flex items-center gap-1 px-2 py-1 rounded-md bg-primary/10 text-primary text-xs"
                        >
                          {getCourseDisplay(courseIdOrObj)}
                          <Button
                            type="button"
                            variant="ghost"
                            size="sm"
                            className="h-5 w-5 p-0"
                            onClick={() => toggleCourse(courseId)}
                            aria-label={`Remove ${getCourseDisplay(courseIdOrObj)}`}
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
              <div className="flex items-center space-x-2">
                <Checkbox
                  id="is_active"
                  checked={formData.is_active}
                  onCheckedChange={(checked) =>
                    setFormData({ ...formData, is_active: checked })
                  }
                />
                <Label
                  htmlFor="is_active"
                  className="text-sm font-normal cursor-pointer"
                >
                  Active Group
                </Label>
              </div>
              <p className="text-xs text-muted-foreground">
                Inactive groups won't be included in timetable generation
              </p>
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
              {group ? "Update" : "Add"} Student Group
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}

