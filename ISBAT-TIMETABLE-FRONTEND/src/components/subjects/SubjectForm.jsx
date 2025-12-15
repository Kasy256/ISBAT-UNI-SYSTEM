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

export function SubjectForm({
  open,
  onOpenChange,
  onSubmit,
  subject,
}) {
  const [formData, setFormData] = useState({
    code: "",
    name: "",
    weekly_hours: 0,
    credits: 0,
    preferred_room_type: "Theory",
    preferred_term: "",
    semester: "",
    program: "",
    course_group: "",
  });

  useEffect(() => {
    if (subject) {
      // Ensure values are properly set, handling null/undefined
      // Normalize preferred_term to match SelectItem values
      let preferredTerm = subject.preferred_term || "";
      if (preferredTerm) {
        // Normalize various formats to match SelectItem values
        const normalized = preferredTerm.trim();
        if (normalized.toLowerCase() === "term 1" || normalized.toLowerCase() === "term1" || normalized === "1") {
          preferredTerm = "Term 1";
        } else if (normalized.toLowerCase() === "term 2" || normalized.toLowerCase() === "term2" || normalized === "2") {
          preferredTerm = "Term 2";
        } else if (normalized.toLowerCase() === "either" || normalized === "") {
          preferredTerm = "";
        }
        // If it's already "Term 1" or "Term 2", keep it as is
      }
      
      // Normalize semester to match SelectItem values
      let semester = subject.semester || "";
      if (semester) {
        // Normalize various formats to match SelectItem values (S1, S2, S3, S4, S5, S6)
        const normalized = semester.trim().toUpperCase();
        if (normalized.match(/^S[1-6]$/)) {
          // Already in correct format (S1-S6)
          semester = normalized;
        } else if (normalized.match(/^[1-6]$/)) {
          // Just the number, add S prefix
          semester = `S${normalized}`;
        } else {
          // If it doesn't match, keep original or set to empty
          semester = semester.trim();
        }
      }
      
      setFormData({
        code: subject.code || subject.id || "", // Use code, fallback to id for backward compatibility
        name: subject.name || "",
        weekly_hours: subject.weekly_hours || 0,
        credits: subject.credits || 0,
        preferred_room_type: subject.preferred_room_type || "Theory",
        preferred_term: preferredTerm,
        semester: semester,
        program: subject.program || "",
        course_group: subject.course_group || "",
      });
    } else {
      // Reset form for new subject
      setFormData({
        code: "",
        name: "",
        weekly_hours: 0,
        credits: 0,
        preferred_room_type: "Theory",
        preferred_term: "",
        semester: "",
        program: "",
        course_group: "",
      });
    }
  }, [subject, open]);

  const handleSubmit = (e) => {
    e.preventDefault();
    // Normalize form data before submission
    // Use code as the id (primary key)
    const submitData = {
      ...formData,
      id: formData.code, // Set id to code
      credits: formData.credits || 0,
      semester: formData.semester === "none" ? "" : formData.semester,
      preferred_term: formData.preferred_term === "either" ? "" : formData.preferred_term,
      course_group: formData.course_group || null,
    };
    onSubmit(submitData);
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-[600px] max-h-[90vh] overflow-y-auto" key={subject?.code || subject?.id || 'new'}>
        <DialogHeader>
          <DialogTitle>{subject ? "Edit Subject" : "Add Subject"}</DialogTitle>
          <DialogDescription>
            {subject
              ? "Update subject information"
              : "Add a new subject to the system"}
          </DialogDescription>
        </DialogHeader>
        <form onSubmit={handleSubmit}>
          <div className="space-y-4 py-4">
              <div className="space-y-2">
                <Label htmlFor="code">Subject Code *</Label>
                <Input
                  id="code"
                  value={formData.code}
                  onChange={(e) =>
                    setFormData({ ...formData, code: e.target.value })
                  }
                  placeholder="CS101"
                  required
                disabled={!!subject} // Disable code editing for existing subjects (code is the primary key)
                />
              <p className="text-xs text-muted-foreground">
                Subject Code is used as the unique identifier
              </p>
            </div>

            <div className="space-y-2">
              <Label htmlFor="name">Subject Name *</Label>
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

            <div className="grid grid-cols-2 gap-4">
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
                <Label htmlFor="credits">Credits</Label>
                <Input
                  id="credits"
                  type="number"
                  min="0"
                  value={formData.credits}
                  onChange={(e) =>
                    setFormData({
                      ...formData,
                      credits: parseInt(e.target.value) || 0,
                    })
                  }
                />
              </div>
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
                  value={formData.semester && formData.semester !== "" ? formData.semester : "none"}
                  onValueChange={(value) =>
                    setFormData({ ...formData, semester: value === "none" ? "" : value })
                  }
                >
                  <SelectTrigger>
                    <SelectValue placeholder="Select semester">
                      {formData.semester && formData.semester !== "" ? formData.semester : "None"}
                    </SelectValue>
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
                <Label htmlFor="preferred_term">Prefered Term</Label>
                <Select
                  value={formData.preferred_term && formData.preferred_term !== "" ? formData.preferred_term : "either"}
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
                <Label htmlFor="course_group">Subject Group</Label>
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
            <Button type="submit">{subject ? "Update" : "Add"} Subject</Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}
