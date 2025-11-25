import { useState, useMemo } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { Plus, Search, MoreVertical, Edit, Trash, ArrowUpDown, Loader2 } from "lucide-react";
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
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { LecturerForm } from "@/components/lecturers/LecturerForm";
import { toast } from "sonner";
import { Button as UIButton } from "@/components/ui/button";
import { lecturersAPI, coursesAPI } from "@/lib/api";

export default function Lecturers() {
  const queryClient = useQueryClient();
  const [searchQuery, setSearchQuery] = useState("");
  const [facultyFilter, setFacultyFilter] = useState("all");
  const [roleFilter, setRoleFilter] = useState("all");
  const [formOpen, setFormOpen] = useState(false);
  const [editingLecturer, setEditingLecturer] = useState(undefined);
  const [sortBy, setSortBy] = useState(null);
  const [sortOrder, setSortOrder] = useState("asc");

  // Fetch lecturers from API
  const { data, isLoading, error } = useQuery({
    queryKey: ['lecturers'],
    queryFn: async () => {
      const response = await lecturersAPI.getAll();
      return response.lecturers || [];
    },
  });

  // Fetch courses for specializations dropdown
  const { data: coursesData } = useQuery({
    queryKey: ['courses'],
    queryFn: async () => {
      const response = await coursesAPI.getAll();
      return response.courses || [];
    },
  });

  const lecturers = data || [];
  const courses = coursesData || [];

  // Get unique faculties and roles for filters
  const faculties = useMemo(() => {
    const unique = [...new Set(lecturers.map(l => l.faculty).filter(Boolean))];
    return unique.sort();
  }, [lecturers]);

  const roles = useMemo(() => {
    const unique = [...new Set(lecturers.map(l => l.role).filter(Boolean))];
    return unique.sort();
  }, [lecturers]);

  // Create mutation
  const createMutation = useMutation({
    mutationFn: lecturersAPI.create,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['lecturers'] });
      toast.success("Lecturer created successfully");
      setFormOpen(false);
    },
    onError: (error) => {
      toast.error(error.message || "Failed to create lecturer");
    },
  });

  // Update mutation
  const updateMutation = useMutation({
    mutationFn: ({ id, data }) => lecturersAPI.update(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['lecturers'] });
      toast.success("Lecturer updated successfully");
      setFormOpen(false);
      setEditingLecturer(undefined);
    },
    onError: (error) => {
      toast.error(error.message || "Failed to update lecturer");
    },
  });

  // Delete mutation
  const deleteMutation = useMutation({
    mutationFn: lecturersAPI.delete,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['lecturers'] });
      toast.success("Lecturer deleted successfully");
    },
    onError: (error) => {
      toast.error(error.message || "Failed to delete lecturer");
    },
  });

  const getInitials = (name) => {
    return name
      .split(" ")
      .map((n) => n[0])
      .join("")
      .toUpperCase();
  };

  const getCourseName = (courseId) => {
    const course = courses.find(c => c.id === courseId || c.code === courseId);
    return course ? `${course.code} - ${course.name}` : courseId;
  };

  const handleSort = () => {
    if (sortBy === "name") {
      setSortOrder(sortOrder === "asc" ? "desc" : "asc");
    } else {
      setSortBy("name");
      setSortOrder("asc");
    }
  };

  const filteredAndSortedLecturers = useMemo(() => {
    let filtered = lecturers.filter((lecturer) => {
      const matchesSearch = lecturer.name
        .toLowerCase()
        .includes(searchQuery.toLowerCase());
      const matchesFaculty =
        facultyFilter === "all" || lecturer.faculty === facultyFilter;
      const matchesRole = roleFilter === "all" || lecturer.role === roleFilter;
      return matchesSearch && matchesFaculty && matchesRole;
    });

    if (sortBy === "name") {
      filtered.sort((a, b) => {
        const comparison = a.name.localeCompare(b.name);
        return sortOrder === "asc" ? comparison : -comparison;
      });
    }

    return filtered;
  }, [lecturers, searchQuery, facultyFilter, roleFilter, sortBy, sortOrder]);

  const handleAddLecturer = (lecturerData) => {
    createMutation.mutate(lecturerData);
  };

  const handleEditLecturer = (lecturerData) => {
    if (editingLecturer) {
      updateMutation.mutate({ id: editingLecturer.id, data: lecturerData });
    }
  };

  const handleDeleteLecturer = (id) => {
    if (confirm("Are you sure you want to delete this lecturer?")) {
      deleteMutation.mutate(id);
    }
  };

  const openEditForm = (lecturer) => {
    setEditingLecturer(lecturer);
    setFormOpen(true);
  };

  const closeForm = () => {
    setFormOpen(false);
    setEditingLecturer(undefined);
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Lecturers</h1>
          <p className="text-muted-foreground mt-1">Manage faculty members and their specializations</p>
        </div>
        <div className="flex items-center gap-2">
          <UIButton variant="outline">Download Template</UIButton>
          <UIButton variant="outline">Import</UIButton>
          <Button className="gap-2" onClick={() => setFormOpen(true)}>
            <Plus className="h-4 w-4" />
            Add Lecturer
          </Button>
        </div>
      </div>

      {/* Filters */}
      <Card className="glass-card p-4">
        <div className="flex flex-col sm:flex-row gap-4">
          <div className="flex-1 relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
            <Input
              placeholder="Search lecturers..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="pl-10"
            />
          </div>
          <Select value={facultyFilter} onValueChange={setFacultyFilter}>
            <SelectTrigger className="w-full sm:w-48">
              <SelectValue placeholder="Filter by Faculty" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All Faculties</SelectItem>
              {faculties.map((faculty) => (
                <SelectItem key={faculty} value={faculty}>
                  {faculty}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
          <Select value={roleFilter} onValueChange={setRoleFilter}>
            <SelectTrigger className="w-full sm:w-48">
              <SelectValue placeholder="Filter by Role" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All Roles</SelectItem>
              {roles.map((role) => (
                <SelectItem key={role} value={role}>
                  {role}
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
            <span className="ml-2">Loading lecturers...</span>
          </div>
        ) : error ? (
          <div className="p-8 text-center text-destructive">
            Error loading lecturers: {error.message}
          </div>
        ) : filteredAndSortedLecturers.length === 0 ? (
          <div className="p-8 text-center text-muted-foreground">
            No lecturers found
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
                    Lecturer
                    <ArrowUpDown className="ml-2 h-4 w-4" />
                  </Button>
                </TableHead>
                <TableHead>Faculty</TableHead>
                <TableHead>Role</TableHead>
                <TableHead>Specializations</TableHead>
                <TableHead>Sessions/Day</TableHead>
                <TableHead>Max Hours/Week</TableHead>
                <TableHead className="text-right">Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {filteredAndSortedLecturers.map((lecturer) => (
                <TableRow key={lecturer.id}>
                  <TableCell>
                    <div className="flex items-center gap-3">
                      <Avatar>
                        <AvatarFallback className="bg-primary/10 text-primary font-semibold">
                          {getInitials(lecturer.name)}
                        </AvatarFallback>
                      </Avatar>
                      <span className="font-medium">{lecturer.name}</span>
                    </div>
                  </TableCell>
                  <TableCell>{lecturer.faculty}</TableCell>
                  <TableCell>
                    <Badge variant="secondary">{lecturer.role}</Badge>
                  </TableCell>
                  <TableCell>
                    <div className="flex flex-wrap gap-1">
                      {lecturer.specializations && lecturer.specializations.length > 0 ? (
                        lecturer.specializations.map((specId) => (
                          <Badge
                            key={specId}
                            variant="outline"
                            className="bg-primary/5 text-primary border-primary/20"
                          >
                            {getCourseName(specId)}
                          </Badge>
                        ))
                      ) : (
                        <span className="text-muted-foreground text-sm">—</span>
                      )}
                    </div>
                  </TableCell>
                  <TableCell>{lecturer.sessions_per_day || 2}</TableCell>
                  <TableCell>{lecturer.max_weekly_hours || 22} hrs</TableCell>
                  <TableCell className="text-right">
                    <DropdownMenu>
                      <DropdownMenuTrigger asChild>
                        <Button variant="ghost" size="sm">
                          <MoreVertical className="h-4 w-4" />
                        </Button>
                      </DropdownMenuTrigger>
                      <DropdownMenuContent align="end" className="bg-popover">
                        <DropdownMenuItem onClick={() => openEditForm(lecturer)}>
                          <Edit className="h-4 w-4 mr-2" />
                          Edit
                        </DropdownMenuItem>
                        <DropdownMenuItem
                          className="text-destructive"
                          onClick={() => handleDeleteLecturer(lecturer.id)}
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

      <LecturerForm
        open={formOpen}
        onOpenChange={closeForm}
        onSubmit={editingLecturer ? handleEditLecturer : handleAddLecturer}
        lecturer={editingLecturer}
        availableCourses={courses}
      />
    </div>
  );
}
