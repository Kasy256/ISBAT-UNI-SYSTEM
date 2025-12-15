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
import { X, Plus } from "lucide-react";
import { Checkbox } from "@/components/ui/checkbox";

// Availability Selector Component
function AvailabilitySelector({ availability, onChange }) {
  const days = ["MON", "TUE", "WED", "THU", "FRI"];
  const timeSlots = [
    "09:00-11:00",
    "11:00-13:00",
    "14:00-16:00",
    "16:00-18:00",
    "18:00-20:00",
  ];

  const toggleDayTimeSlot = (day, timeSlot) => {
    const newAvailability = { ...availability };
    if (!newAvailability[day]) {
      newAvailability[day] = [];
    }
    
    const index = newAvailability[day].indexOf(timeSlot);
    if (index > -1) {
      // Remove time slot
      newAvailability[day] = newAvailability[day].filter(ts => ts !== timeSlot);
      if (newAvailability[day].length === 0) {
        delete newAvailability[day];
      }
    } else {
      // Add time slot
      newAvailability[day] = [...newAvailability[day], timeSlot].sort();
    }
    
    onChange(newAvailability);
  };

  const isTimeSlotSelected = (day, timeSlot) => {
    return availability[day]?.includes(timeSlot) || false;
  };

  return (
    <div className="space-y-3 p-3 border rounded-md">
      {days.map((day) => (
        <div key={day} className="space-y-2">
          <div className="flex items-center gap-2">
            <Checkbox
              id={`day-${day}`}
              checked={availability[day] && availability[day].length > 0}
              onCheckedChange={(checked) => {
                if (checked) {
                  // Select all time slots for the day
                  onChange({
                    ...availability,
                    [day]: [...timeSlots],
                  });
                } else {
                  // Remove all time slots for the day
                  const newAvailability = { ...availability };
                  delete newAvailability[day];
                  onChange(newAvailability);
                }
              }}
            />
            <Label htmlFor={`day-${day}`} className="font-medium min-w-[60px]">
              {day}
            </Label>
          </div>
          {availability[day] && availability[day].length > 0 && (
            <div className="flex flex-wrap gap-2 ml-7">
              {timeSlots.map((timeSlot) => (
                <Button
                  key={timeSlot}
                  type="button"
                  variant={isTimeSlotSelected(day, timeSlot) ? "default" : "outline"}
                  size="sm"
                  className="h-8 text-xs"
                  onClick={() => toggleDayTimeSlot(day, timeSlot)}
                >
                  {timeSlot}
                </Button>
              ))}
            </div>
          )}
        </div>
      ))}
    </div>
  );
}

export function LecturerForm({
  open,
  onOpenChange,
  onSubmit,
  lecturer,
  availableCourses = [],
  canonicalGroups = [],
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
      const role = lecturer.role || "Full-Time";
      // For Part-Time, preserve existing availability or set to empty object
      // For Full-Time and Faculty Dean, set to null (always available)
      let availability = null;
      if (role === "Part-Time") {
        availability = lecturer.availability || {};
      } else {
        availability = null; // Full-Time and Faculty Dean are always available
      }
      
      // Set default max_weekly_hours based on role if not already set
      let defaultHours = 22; // Default for Full-Time
      if (role === "Faculty Dean") {
        defaultHours = 16;
      } else if (role === "Part-Time") {
        defaultHours = 2;
      }
      
      setFormData({
        id: lecturer.id || "",
        name: lecturer.name || "",
        role: role,
        faculty: lecturer.faculty || "",
        specializations: lecturer.specializations || [],
        availability: availability,
        sessions_per_day: lecturer.sessions_per_day || 2,
        max_weekly_hours: lecturer.max_weekly_hours || defaultHours,
      });
    } else {
      // Reset form for new lecturer (defaults to Full-Time with 22 hours)
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

  // Handle role change - update availability and set default max_weekly_hours
  const handleRoleChange = (newRole) => {
    let defaultHours = 22; // Default for Full-Time
    if (newRole === "Faculty Dean") {
      defaultHours = 16;
    } else if (newRole === "Part-Time") {
      defaultHours = 2;
    }
    
    if (newRole === "Full-Time") {
      // Full-Time: Always available (set to null)
      setFormData({
        ...formData,
        role: newRole,
        availability: null,
        max_weekly_hours: defaultHours,
      });
    } else if (newRole === "Part-Time") {
      // Part-Time: Must select availability
      setFormData({
        ...formData,
        role: newRole,
        availability: formData.availability || {},
        max_weekly_hours: defaultHours,
      });
    } else if (newRole === "Faculty Dean") {
      // Faculty Dean: Always available
      setFormData({
        ...formData,
        role: newRole,
        availability: null,
        max_weekly_hours: defaultHours,
      });
    }
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    // Ensure Full-Time and Faculty Dean have availability set to null
    const submitData = { ...formData };
    if (submitData.role === "Full-Time" || submitData.role === "Faculty Dean") {
      submitData.availability = null;
    }
    // Ensure Part-Time has availability set (even if empty object)
    if (submitData.role === "Part-Time" && !submitData.availability) {
      submitData.availability = {};
    }
    onSubmit(submitData);
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
    // Return the specialization ID exactly as stored - no normalization or conversion
    return courseId;
  };

  // Filter canonical groups - specializations should use subject groups, not individual subjects
  const filteredCanonicalGroups = canonicalGroups || [];

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
                  onValueChange={handleRoleChange}
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
                {formData.role === "Full-Time" && (
                  <p className="text-xs text-muted-foreground">
                    Full-Time lecturers are always available
                  </p>
                )}
                {formData.role === "Faculty Dean" && (
                  <p className="text-xs text-muted-foreground">
                    Faculty Deans are always available (14-16 hours/week)
                  </p>
                )}
                {formData.role === "Part-Time" && (
                  <p className="text-xs text-muted-foreground">
                    Part-Time lecturers must specify availability below
                  </p>
                )}
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
                <Label htmlFor="max_weekly_hours">Max Weekly Hours *</Label>
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
                  required
                />
                <p className="text-xs text-muted-foreground">
                  Maximum number of teaching hours per week
                </p>
              </div>
            </div>

            <div className="space-y-2">
              <Label>Specializations(Subject Groups) *</Label>
              <p className="text-xs text-muted-foreground">
                Select subject groups (not individual subjects). A subject group represents equivalent subjects across programs.
              </p>
              <div className="space-y-2">
                <Select
                  onValueChange={(value) => {
                    if (!formData.specializations.includes(value)) {
                      toggleSpecialization(value);
                    }
                  }}
                >
                  <SelectTrigger>
                    <SelectValue placeholder="Add subject group specialization" />
                  </SelectTrigger>
                  <SelectContent>
                    {filteredCanonicalGroups
                      .filter(
                        (g) => !formData.specializations.includes(g.canonical_id)
                      )
                      .map((group) => (
                        <SelectItem
                          key={group.canonical_id}
                          value={group.canonical_id}
                        >
                          {group.name} ({group.canonical_id})
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

            {/* Availability Section */}
            {formData.role === "Part-Time" ? (
              <div className="space-y-2">
                <Label>Availability * (Required for Part-Time)</Label>
                <p className="text-xs text-muted-foreground">
                  Select days and time slots when this lecturer is available
                </p>
                <AvailabilitySelector
                  availability={formData.availability || {}}
                  onChange={(newAvailability) =>
                    setFormData({ ...formData, availability: newAvailability })
                  }
                />
              </div>
            ) : (
              <div className="space-y-2">
                <Label>Availability</Label>
                <div className="p-3 bg-muted/50 rounded-md">
                  <p className="text-sm text-muted-foreground">
                    {formData.role === "Full-Time" && "✓ Always available (Full-Time lecturers)"}
                    {formData.role === "Faculty Dean" && "✓ Always available (Faculty Dean)"}
                  </p>
                </div>
              </div>
            )}
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
