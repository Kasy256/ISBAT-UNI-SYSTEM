import { useState, useEffect, useMemo, useRef } from "react";
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
  Popover,
  PopoverContent,
  PopoverTrigger,
} from "@/components/ui/popover";
import { Textarea } from "@/components/ui/textarea";
import { X, Search, ChevronDown, Check } from "lucide-react";
import { cn } from "@/lib/utils";

export function CanonicalGroupForm({
  open,
  onOpenChange,
  onSubmit,
  group,
  availableCourses = [],
}) {
  const [formData, setFormData] = useState({
    canonical_id: "",
    name: "",
    course_codes: [],
    description: "",
  });
  const [searchQuery, setSearchQuery] = useState("");
  const [dropdownOpen, setDropdownOpen] = useState(false);
  const searchInputRef = useRef(null);

  useEffect(() => {
    if (group) {
      setFormData({
        canonical_id: group.canonical_id || "",
        name: group.name || "",
        course_codes: group.course_codes || [],
        description: group.description || "",
      });
    } else {
      // Reset form for new group
      setFormData({
        canonical_id: "",
        name: "",
        course_codes: [],
        description: "",
      });
    }
    // Reset search when form opens/closes
    setSearchQuery("");
  }, [group, open]);

  // Focus search input when dropdown opens
  useEffect(() => {
    if (dropdownOpen && searchInputRef.current) {
      setTimeout(() => {
        searchInputRef.current?.focus();
      }, 100);
    }
  }, [dropdownOpen]);

  const handleSubmit = (e) => {
    e.preventDefault();
    onSubmit(formData);
  };

  const toggleCourse = (courseCode) => {
    setFormData((prev) => ({
      ...prev,
      course_codes: prev.course_codes.includes(courseCode)
        ? prev.course_codes.filter((code) => code !== courseCode)
        : [...prev.course_codes, courseCode],
    }));
  };

  const getCourseDisplay = (courseCode) => {
    const course = availableCourses.find((c) => c.code === courseCode);
    return course ? `${course.code} - ${course.name}` : courseCode;
  };

  // Get unique course codes
  const uniqueCourseCodes = useMemo(() => {
    const codes = new Set();
    availableCourses.forEach((course) => {
      if (course.code) codes.add(course.code);
    });
    return Array.from(codes).sort();
  }, [availableCourses]);

  // Filter courses based on search query
  const filteredCourses = useMemo(() => {
    if (!searchQuery.trim()) {
      return uniqueCourseCodes.filter((code) => !formData.course_codes.includes(code));
    }

    const query = searchQuery.toLowerCase();
    return uniqueCourseCodes
      .filter((code) => {
        if (formData.course_codes.includes(code)) return false;
        const course = availableCourses.find((c) => c.code === code);
        if (!course) return code.toLowerCase().includes(query);
        return (
          code.toLowerCase().includes(query) ||
          course.name?.toLowerCase().includes(query)
        );
      })
      .sort();
  }, [searchQuery, uniqueCourseCodes, formData.course_codes, availableCourses]);

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-[600px] max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>
            {group ? "Edit Course Group" : "Add Course Group"}
          </DialogTitle>
          <DialogDescription>
            {group
              ? "Update course group information"
              : "Create a group of equivalent courses across different programs"}
          </DialogDescription>
        </DialogHeader>
        <form onSubmit={handleSubmit}>
          <div className="space-y-4 py-4">
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="canonical_id">Group ID *</Label>
                <Input
                  id="canonical_id"
                  value={formData.canonical_id}
                  onChange={(e) =>
                    setFormData({ ...formData, canonical_id: e.target.value })
                  }
                  placeholder="PROG_C"
                  required
                  disabled={!!group} // Disable ID editing for existing groups
                />
                <p className="text-xs text-muted-foreground">
                  Unique identifier (e.g., PROG_C, DATA_STRUCT)
                </p>
              </div>
              <div className="space-y-2">
                <Label htmlFor="name">Name *</Label>
                <Input
                  id="name"
                  value={formData.name}
                  onChange={(e) =>
                    setFormData({ ...formData, name: e.target.value })
                  }
                  placeholder="Programming in C"
                  required
                />
              </div>
            </div>

            <div className="space-y-2">
              <Label htmlFor="description">Description</Label>
              <Textarea
                id="description"
                value={formData.description}
                onChange={(e) =>
                  setFormData({ ...formData, description: e.target.value })
                }
                placeholder="This group represents the Programming in C course taught across different programs..."
                rows={3}
              />
            </div>

            <div className="space-y-2">
              <Label>Course Codes *</Label>
              <p className="text-xs text-muted-foreground mb-2">
                Select course codes that represent the same course across different programs
              </p>
              <div className="space-y-2">
                <Popover 
                  open={dropdownOpen} 
                  onOpenChange={(open) => {
                    setDropdownOpen(open);
                    if (!open) {
                      setSearchQuery("");
                    }
                  }}
                >
                  <PopoverTrigger asChild>
                    <Button
                      type="button"
                      variant="outline"
                      role="combobox"
                      aria-expanded={dropdownOpen}
                      className="w-full justify-between"
                    >
                      <span className="text-muted-foreground">
                        {formData.course_codes.length > 0
                          ? `${formData.course_codes.length} course${formData.course_codes.length > 1 ? "s" : ""} selected`
                          : "Add course code"}
                      </span>
                      <ChevronDown className="ml-2 h-4 w-4 shrink-0 opacity-50" />
                    </Button>
                  </PopoverTrigger>
                  <PopoverContent className="w-[var(--radix-popover-trigger-width)] p-0" align="start">
                    <div className="flex flex-col">
                      {/* Search Input */}
                      <div className="flex items-center border-b px-3">
                        <Search className="mr-2 h-4 w-4 shrink-0 opacity-50" />
                        <Input
                          ref={searchInputRef}
                          placeholder="Search by code or name..."
                          value={searchQuery}
                          onChange={(e) => setSearchQuery(e.target.value)}
                          className="border-0 focus-visible:ring-0 focus-visible:ring-offset-0"
                        />
                      </div>
                      {/* Scrollable Course List */}
                      <div className="max-h-[300px] overflow-y-auto overflow-x-hidden custom-scrollbar">
                        {filteredCourses.length > 0 ? (
                          <div className="p-1">
                            {filteredCourses.map((code) => {
                              const course = availableCourses.find((c) => c.code === code);
                              const isSelected = formData.course_codes.includes(code);
                              return (
                                <div
                                  key={code}
                                  className={cn(
                                    "relative flex cursor-pointer select-none items-center rounded-sm px-2 py-1.5 text-sm outline-none hover:bg-accent hover:text-accent-foreground",
                                    isSelected && "bg-accent"
                                  )}
                                  onClick={() => {
                                    toggleCourse(code);
                                    setSearchQuery("");
                                  }}
                                >
                                  <div className="flex flex-1 flex-col">
                                    <div className="flex items-center gap-2">
                                      <span className="font-medium">{code}</span>
                                      {isSelected && (
                                        <Check className="h-4 w-4 text-primary" />
                                      )}
                                    </div>
                                    {course && (
                                      <span className="text-xs text-muted-foreground">
                                        {course.name}
                                      </span>
                                    )}
                                  </div>
                                </div>
                              );
                            })}
                          </div>
                        ) : (
                          <div className="px-2 py-6 text-center text-sm text-muted-foreground">
                            {searchQuery
                              ? "No courses found matching your search"
                              : "All available courses have been added"}
                          </div>
                        )}
                      </div>
                    </div>
                  </PopoverContent>
                </Popover>
                {formData.course_codes.length > 0 && (
                  <div className="flex flex-wrap gap-2 p-2 border rounded-md">
                    {formData.course_codes.map((code) => (
                      <span
                        key={code}
                        className="inline-flex items-center gap-1 px-2 py-1 rounded-md bg-primary/10 text-primary text-xs"
                      >
                        {getCourseDisplay(code)}
                        <Button
                          type="button"
                          variant="ghost"
                          size="sm"
                          className="h-5 w-5 p-0"
                          onClick={() => toggleCourse(code)}
                          aria-label={`Remove ${getCourseDisplay(code)}`}
                        >
                          <X className="h-3 w-3" />
                        </Button>
                      </span>
                    ))}
                  </div>
                )}
                {formData.course_codes.length === 0 && (
                  <p className="text-xs text-muted-foreground">
                    No course codes selected. Add at least one course code.
                  </p>
                )}
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
            <Button
              type="submit"
              disabled={formData.course_codes.length === 0}
            >
              {group ? "Update" : "Add"} Course Group
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}

