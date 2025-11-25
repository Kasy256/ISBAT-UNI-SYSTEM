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

export function CourseForm({
  open,
  onOpenChange,
  onSubmit,
  course,
}) {
  const [formData, setFormData] = useState({
    id: "",
    code: "",
    name: "",
    weekly_hours: 0,
    preferred_room_type: "Theory",
    preferred_term: "",
    semester: "",
    program: "",
    course_group: "",
  });

  useEffect(() => {
    if (course) {
      setFormData({
        id: course.id || "",
        code: course.code || "",
        name: course.name || "",
        weekly_hours: course.weekly_hours || 0,
        preferred_room_type: course.preferred_room_type || "Theory",
        preferred_term: course.preferred_term || "",
        semester: course.semester || "",
        program: course.program || "",
        course_group: course.course_group || "",
      });
    } else {
      // Reset form for new course
      setFormData({
        id: "",
        code: "",
        name: "",
        weekly_hours: 0,
        preferred_room_type: "Theory",
        preferred_term: "",
        semester: "",
        program: "",
        course_group: "",
      });
    }
  }, [course, open]);

  const handleSubmit = (e) => {
    e.preventDefault();
    // Normalize form data before submission
    const submitData = {
      ...formData,
      semester: formData.semester === "none" ? "" : formData.semester,
      preferred_term: formData.preferred_term === "either" ? "" : formData.preferred_term,
      course_group: formData.course_group || null,
    };
    onSubmit(submitData);
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-[600px] max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>{course ? "Edit Course Unit" : "Add Course Unit"}</DialogTitle>
          <DialogDescription>
            {course
              ? "Update course unit information"
              : "Add a new course unit to the system"}
          </DialogDescription>
        </DialogHeader>
        <form onSubmit={handleSubmit}>
          <div className="space-y-4 py-4">
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="id">Course ID *</Label>
                <Input
                  id="id"
                  value={formData.id}
                  onChange={(e) =>
                    setFormData({ ...formData, id: e.target.value })
                  }
                  placeholder="CS101"
                  required
                  disabled={!!course} // Disable ID editing for existing courses
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="code">Course Code *</Label>
                <Input
                  id="code"
                  value={formData.code}
                  onChange={(e) =>
                    setFormData({ ...formData, code: e.target.value })
                  }
                  placeholder="CS101"
                  required
                />
              </div>
            </div>

            <div className="space-y-2">
              <Label htmlFor="name">Course Name *</Label>
              <Input
                id="name"
                value={formData.name}
                onChange={(e) =>
                  setFormData({ ...formData, name: e.target.value })
                }
                placeholder="Programming Fundamentals"
                required
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="weekly_hours">Weekly Hours *</Label>
              <Input
                id="weekly_hours"
                type="number"
                min="1"
                value={formData.weekly_hours}
                onChange={(e) =>
                  setFormData({
                    ...formData,
                    weekly_hours: parseInt(e.target.value) || 0,
                  })
                }
                required
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="preferred_room_type">Room Type *</Label>
              <Select
                value={formData.preferred_room_type}
                onValueChange={(value) =>
                  setFormData({ ...formData, preferred_room_type: value })
                }
              >
                <SelectTrigger>
                  <SelectValue placeholder="Select room type" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="Theory">Theory</SelectItem>
                  <SelectItem value="Lab">Lab</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="program">Program</Label>
                <Input
                  id="program"
                  value={formData.program}
                  onChange={(e) =>
                    setFormData({ ...formData, program: e.target.value })
                  }
                  placeholder="BSCAIT"
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="semester">Semester</Label>
                <Select
                  value={formData.semester || "none"}
                  onValueChange={(value) =>
                    setFormData({ ...formData, semester: value === "none" ? "" : value })
                  }
                >
                  <SelectTrigger>
                    <SelectValue placeholder="Select semester" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="none">None</SelectItem>
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

            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="preferred_term">Preferred Term</Label>
                <Select
                  value={formData.preferred_term || "either"}
                  onValueChange={(value) =>
                    setFormData({ ...formData, preferred_term: value === "either" ? "" : value })
                  }
                >
                  <SelectTrigger>
                    <SelectValue placeholder="Select term" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="either">Either</SelectItem>
                    <SelectItem value="Term 1">Term 1</SelectItem>
                    <SelectItem value="Term 2">Term 2</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <div className="space-y-2">
                <Label htmlFor="course_group">Course Group</Label>
                <Input
                  id="course_group"
                  value={formData.course_group || ""}
                  onChange={(e) =>
                    setFormData({ ...formData, course_group: e.target.value || null })
                  }
                  placeholder="BIT1101_GROUP"
                />
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
            <Button type="submit">{course ? "Update" : "Add"} Course Unit</Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}
