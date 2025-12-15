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
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from "@/components/ui/popover";
import {
  Command,
  CommandEmpty,
  CommandGroup,
  CommandInput,
  CommandItem,
  CommandList,
} from "@/components/ui/command";
import { Checkbox } from "@/components/ui/checkbox";
import { X, Check, ChevronsUpDown } from "lucide-react";
import { cn } from "@/lib/utils";

export function ProgramForm({
  open,
  onOpenChange,
  onSubmit,
  program,
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
  const [subjectSearchOpen, setSubjectSearchOpen] = useState(false);
  const [subjectSearchQuery, setSubjectSearchQuery] = useState("");

  useEffect(() => {
    if (program) {
      // Normalize course_units - convert objects to IDs if needed
      const normalizedCourseUnits = (program.course_units || []).map((cu) => {
        if (typeof cu === 'object' && cu !== null) {
          return cu.code || cu.id || cu;
        }
        return cu;
      });
      
      setFormData({
        id: program.id || "",
        batch: program.batch || "",
        program: program.program || "",
        semester: program.semester || "",
        term: program.term || "Term1", // Default to Term1 if not set
        size: program.size || 0,
        course_units: normalizedCourseUnits,
        is_active: program.is_active !== undefined ? program.is_active : true,
      });
    } else {
      // Reset form for new program
      setFormData({
        id: "",
        batch: "",
        program: "",
        semester: "",
        term: "Term1", // Default to Term1 for new programs
        size: 0,
        course_units: [],
        is_active: true,
      });
    }
  }, [program, open]);

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
    const subject = availableCourses.find(
      (c) => c.id === courseIdOrObj || c.code === courseIdOrObj
    );
    return subject ? `${subject.code} - ${subject.name}` : courseIdOrObj;
  };

  // Show all subjects (don't filter by program - subjects can be assigned to any program)
  // Get available subjects (not already selected)
  const availableSubjects = availableCourses.filter((c) => {
    const courseId = c.id || c.code;
    return !formData.course_units.some((cu) => {
      if (typeof cu === 'object' && cu !== null) {
        return (cu.code === courseId || cu.id === courseId);
      }
      return cu === courseId;
    });
  });
  
  // Filter subjects by search query
  const searchFilteredSubjects = subjectSearchQuery
    ? availableSubjects.filter((subject) => {
        const searchLower = subjectSearchQuery.toLowerCase();
        return (
          subject.code?.toLowerCase().includes(searchLower) ||
          subject.name?.toLowerCase().includes(searchLower)
        );
      })
    : availableSubjects;

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-[700px] max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>
            {program ? "Edit Program" : "Add Program"}
          </DialogTitle>
          <DialogDescription>
            {program
              ? "Update program information"
              : "Create a new program and assign subjects"}
          </DialogDescription>
        </DialogHeader>
        <form onSubmit={handleSubmit}>
          <div className="space-y-4 py-4">
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="id">Program ID *</Label>
                <Input
                  id="id"
                  value={formData.id}
                  onChange={(e) =>
                    setFormData({ ...formData, id: e.target.value })
                  }
                  placeholder="SG_BSCAIT_S126_S1_T1"
                  required
                  disabled={!!program} // Disable ID editing for existing programs
                />
                <p className="text-xs text-muted-foreground">
                  Format: SG_PROGRAM_BATCH_SEMESTER_TERM
                </p>
              </div>
              <div className="space-y-2">
                <Label htmlFor="batch">BATCH *</Label>
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
                <Label htmlFor="program">Program Name *</Label>
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
              <Label htmlFor="size">Student Size *</Label>
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
              <Label>Subjects *</Label>
              <div className="space-y-2">
                <Popover open={subjectSearchOpen} onOpenChange={setSubjectSearchOpen}>
                  <PopoverTrigger asChild>
                    <Button
                      variant="outline"
                      role="combobox"
                      aria-expanded={subjectSearchOpen}
                      className="w-full justify-between"
                    >
                      <span className="text-muted-foreground">
                        {availableSubjects.length > 0 
                          ? "Search and select subjects..." 
                          : "No subjects available"}
                      </span>
                      <ChevronsUpDown className="ml-2 h-4 w-4 shrink-0 opacity-50" />
                    </Button>
                  </PopoverTrigger>
                  <PopoverContent className="w-[600px] p-0" align="start">
                    <Command shouldFilter={false}>
                      <CommandInput 
                        placeholder="Search subjects by code or name..." 
                        value={subjectSearchQuery}
                        onValueChange={setSubjectSearchQuery}
                      />
                      <CommandList className="max-h-[300px] overflow-y-auto">
                        <CommandEmpty>No subjects found.</CommandEmpty>
                        <CommandGroup>
                          {searchFilteredSubjects.map((subject) => {
                            const courseId = subject.id || subject.code;
                            const isSelected = formData.course_units.some((cu) => {
                              if (typeof cu === 'object' && cu !== null) {
                                return (cu.code === courseId || cu.id === courseId);
                              }
                              return cu === courseId;
                            });
                            
                            return (
                              <CommandItem
                                key={subject.id || subject.code}
                                value={`${subject.code} ${subject.name}`}
                                onSelect={() => {
                                  toggleCourse(courseId);
                                  // Don't close popover - allow multiple selections
                                }}
                              >
                                <Check
                                  className={cn(
                                    "mr-2 h-4 w-4",
                                    isSelected ? "opacity-100" : "opacity-0"
                                  )}
                                />
                                <span className="flex-1">
                                  {subject.code} - {subject.name}
                                </span>
                              </CommandItem>
                            );
                          })}
                        </CommandGroup>
                      </CommandList>
                    </Command>
                  </PopoverContent>
                </Popover>
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
                  Active Program
                </Label>
              </div>
              <p className="text-xs text-muted-foreground">
                Inactive programs won't be included in timetable generation
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
              {program ? "Update" : "Add"} Program
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}

