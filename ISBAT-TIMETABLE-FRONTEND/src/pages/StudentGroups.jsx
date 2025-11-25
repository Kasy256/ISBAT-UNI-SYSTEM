import { useState, useMemo } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { Plus, Search, MoreVertical, Edit, Trash, ArrowUpDown, Loader2, Users } from "lucide-react";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { StudentGroupForm } from "@/components/student-groups/StudentGroupForm";
import { toast } from "sonner";
import { Button as UIButton } from "@/components/ui/button";
import { studentsAPI, coursesAPI } from "@/lib/api";

export default function StudentGroups() {
  const queryClient = useQueryClient();
  const [searchQuery, setSearchQuery] = useState("");
  const [programFilter, setProgramFilter] = useState("all");
  const [semesterFilter, setSemesterFilter] = useState("all");
  const [formOpen, setFormOpen] = useState(false);
  const [editingGroup, setEditingGroup] = useState(undefined);
  const [sortBy, setSortBy] = useState(null);
  const [sortOrder, setSortOrder] = useState("asc");

  // Fetch student groups from API
  const { data, isLoading, error } = useQuery({
    queryKey: ['student-groups'],
    queryFn: async () => {
      const response = await studentsAPI.getAll();
      return response.student_groups || [];
    },
  });

  // Fetch courses for course assignment
  const { data: coursesData } = useQuery({
    queryKey: ['courses'],
    queryFn: async () => {
      const response = await coursesAPI.getAll();
      return response.courses || [];
    },
  });

  const groups = data || [];
  const courses = coursesData || [];

  // Get unique values for filters
  const programs = useMemo(() => {
    const unique = [...new Set(groups.map(g => g.program).filter(Boolean))];
    return unique.sort();
  }, [groups]);

  const semesters = useMemo(() => {
    const unique = [...new Set(groups.map(g => g.semester).filter(Boolean))];
    return unique.sort();
  }, [groups]);

  // Create mutation
  const createMutation = useMutation({
    mutationFn: studentsAPI.create,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['student-groups'] });
      toast.success("Student group created successfully");
      setFormOpen(false);
    },
    onError: (error) => {
      toast.error(error.message || "Failed to create student group");
    },
  });

  // Update mutation
  const updateMutation = useMutation({
    mutationFn: ({ id, data }) => studentsAPI.update(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['student-groups'] });
      toast.success("Student group updated successfully");
      setFormOpen(false);
      setEditingGroup(undefined);
    },
    onError: (error) => {
      toast.error(error.message || "Failed to update student group");
    },
  });

  // Delete mutation
  const deleteMutation = useMutation({
    mutationFn: studentsAPI.delete,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['student-groups'] });
      toast.success("Student group deleted successfully");
    },
    onError: (error) => {
      toast.error(error.message || "Failed to delete student group");
    },
  });

  const handleSort = () => {
    if (sortBy === "id") {
      setSortOrder(sortOrder === "asc" ? "desc" : "asc");
    } else {
      setSortBy("id");
      setSortOrder("asc");
    }
  };

  const filteredAndSortedGroups = useMemo(() => {
    let filtered = groups.filter((group) => {
      const matchesSearch =
        group.id?.toLowerCase().includes(searchQuery.toLowerCase()) ||
        group.batch?.toLowerCase().includes(searchQuery.toLowerCase()) ||
        group.program?.toLowerCase().includes(searchQuery.toLowerCase());
      const matchesProgram =
        programFilter === "all" || group.program === programFilter;
      const matchesSemester =
        semesterFilter === "all" || group.semester === semesterFilter;
      return matchesSearch && matchesProgram && matchesSemester;
    });

    if (sortBy === "id") {
      filtered.sort((a, b) => {
        const comparison = (a.id || '').localeCompare(b.id || '');
        return sortOrder === "asc" ? comparison : -comparison;
      });
    }

    return filtered;
  }, [groups, searchQuery, programFilter, semesterFilter, sortBy, sortOrder]);

  const handleAddGroup = (groupData) => {
    createMutation.mutate(groupData);
  };

  const handleEditGroup = (groupData) => {
    if (editingGroup) {
      updateMutation.mutate({ id: editingGroup.id, data: groupData });
    }
  };

  const handleDeleteGroup = (id) => {
    if (confirm("Are you sure you want to delete this student group?")) {
      deleteMutation.mutate(id);
    }
  };

  const openEditForm = (group) => {
    setEditingGroup(group);
    setFormOpen(true);
  };

  const closeForm = () => {
    setFormOpen(false);
    setEditingGroup(undefined);
  };

  const getCourseName = (courseIdOrObj) => {
    // Handle both string IDs and object {code, name}
    if (typeof courseIdOrObj === 'object' && courseIdOrObj !== null) {
      return `${courseIdOrObj.code || ''} - ${courseIdOrObj.name || ''}`;
    }
    const course = courses.find(c => c.id === courseIdOrObj || c.code === courseIdOrObj);
    return course ? `${course.code} - ${course.name}` : courseIdOrObj;
  };

  const getCourseKey = (courseIdOrObj) => {
    // Get a unique key for the course
    if (typeof courseIdOrObj === 'object' && courseIdOrObj !== null) {
      return courseIdOrObj.code || courseIdOrObj.id || JSON.stringify(courseIdOrObj);
    }
    return courseIdOrObj;
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Student Groups</h1>
          <p className="text-muted-foreground mt-1">
            Manage student cohorts and assign courses to groups
          </p>
        </div>
        <div className="flex items-center gap-2">
          <UIButton variant="outline">Download Template</UIButton>
          <UIButton variant="outline">Import</UIButton>
          <Button className="gap-2" onClick={() => setFormOpen(true)}>
            <Plus className="h-4 w-4" />
            Add Student Group
          </Button>
        </div>
      </div>

      {/* Filters */}
      <Card className="glass-card p-4">
        <div className="flex flex-col sm:flex-row gap-4">
          <div className="flex-1 relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
            <Input
              placeholder="Search groups..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="pl-10"
            />
          </div>
          <Select value={programFilter} onValueChange={setProgramFilter}>
            <SelectTrigger className="w-full sm:w-48">
              <SelectValue placeholder="Filter by Program" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All Programs</SelectItem>
              {programs.map((program) => (
                <SelectItem key={program} value={program}>
                  {program}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
          <Select value={semesterFilter} onValueChange={setSemesterFilter}>
            <SelectTrigger className="w-full sm:w-48">
              <SelectValue placeholder="Filter by Semester" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All Semesters</SelectItem>
              {semesters.map((semester) => (
                <SelectItem key={semester} value={semester}>
                  {semester}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>
      </Card>

      {/* Table */}
      <Card className="glass-card">
        {isLoading ? (
          <div className="flex items-center justify-center p-8">
            <Loader2 className="h-6 w-6 animate-spin" />
            <span className="ml-2">Loading student groups...</span>
          </div>
        ) : error ? (
          <div className="p-8 text-center text-destructive">
            Error loading student groups: {error.message}
          </div>
        ) : filteredAndSortedGroups.length === 0 ? (
          <div className="p-8 text-center text-muted-foreground">
            No student groups found
          </div>
        ) : (
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>
                  <Button
                    variant="ghost"
                    className="h-8 px-2 hover:bg-transparent"
                    onClick={handleSort}
                  >
                    Group ID
                    <ArrowUpDown className="ml-2 h-4 w-4" />
                  </Button>
                </TableHead>
                <TableHead>Program</TableHead>
                <TableHead>Batch</TableHead>
                <TableHead>Semester</TableHead>
                <TableHead>Size</TableHead>
                <TableHead>Courses</TableHead>
                <TableHead>Status</TableHead>
                <TableHead className="text-right">Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {filteredAndSortedGroups.map((group) => (
                <TableRow key={group.id}>
                  <TableCell className="font-medium">{group.id}</TableCell>
                  <TableCell>
                    <Badge variant="outline">{group.program}</Badge>
                  </TableCell>
                  <TableCell>{group.batch}</TableCell>
                  <TableCell>
                    <Badge variant="secondary">{group.semester}</Badge>
                  </TableCell>
                  <TableCell>
                    <div className="flex items-center gap-1">
                      <Users className="h-4 w-4 text-muted-foreground" />
                      <span className="font-semibold">{group.size}</span>
                    </div>
                  </TableCell>
                  <TableCell>
                    {group.course_units && group.course_units.length > 0 ? (
                      <div className="flex flex-wrap gap-1">
                        {group.course_units.slice(0, 3).map((courseIdOrObj, index) => (
                          <Badge
                            key={getCourseKey(courseIdOrObj) || index}
                            variant="outline"
                            className="bg-primary/5 text-primary border-primary/20 text-xs"
                          >
                            {getCourseName(courseIdOrObj)}
                          </Badge>
                        ))}
                        {group.course_units.length > 3 && (
                          <Badge variant="outline" className="text-xs">
                            +{group.course_units.length - 3} more
                          </Badge>
                        )}
                      </div>
                    ) : (
                      <span className="text-muted-foreground text-sm">No courses</span>
                    )}
                  </TableCell>
                  <TableCell>
                    <Badge
                      variant={group.is_active ? "default" : "secondary"}
                    >
                      {group.is_active ? "Active" : "Inactive"}
                    </Badge>
                  </TableCell>
                  <TableCell className="text-right">
                    <DropdownMenu>
                      <DropdownMenuTrigger asChild>
                        <Button variant="ghost" size="sm">
                          <MoreVertical className="h-4 w-4" />
                        </Button>
                      </DropdownMenuTrigger>
                      <DropdownMenuContent align="end" className="bg-popover">
                        <DropdownMenuItem onClick={() => openEditForm(group)}>
                          <Edit className="h-4 w-4 mr-2" />
                          Edit
                        </DropdownMenuItem>
                        <DropdownMenuItem
                          className="text-destructive"
                          onClick={() => handleDeleteGroup(group.id)}
                        >
                          <Trash className="h-4 w-4 mr-2" />
                          Delete
                        </DropdownMenuItem>
                      </DropdownMenuContent>
                    </DropdownMenu>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        )}
      </Card>

      <StudentGroupForm
        open={formOpen}
        onOpenChange={closeForm}
        onSubmit={editingGroup ? handleEditGroup : handleAddGroup}
        group={editingGroup}
        availableCourses={courses}
      />
    </div>
  );
}

