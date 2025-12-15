import { useState, useMemo } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { Plus, Search, MoreVertical, Edit, Trash, ArrowUpDown, Loader2, BookOpen } from "lucide-react";
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
import { SubjectForm } from "@/components/subjects/SubjectForm";
import ImportDialog from "@/components/ImportDialog";
import { toast } from "sonner";
import { Button as UIButton } from "@/components/ui/button";
import { subjectsAPI, importAPI } from "@/lib/api";
import { useNavigate } from "react-router-dom";

export default function Subjects() {
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const [searchQuery, setSearchQuery] = useState("");
  const [programFilter, setProgramFilter] = useState("all");
  const [semesterFilter, setSemesterFilter] = useState("all");
  const [formOpen, setFormOpen] = useState(false);
  const [importOpen, setImportOpen] = useState(false);
  const [editingCourse, setEditingCourse] = useState(undefined);
  const [sortBy, setSortBy] = useState(null);
  const [sortOrder, setSortOrder] = useState("asc");

  // Fetch subjects from API
  const { data, isLoading, error } = useQuery({
    queryKey: ['subjects'],
    queryFn: async () => {
      const response = await subjectsAPI.getAll();
      return response.subjects || [];
    },
  });

  const subjects = data || [];

  // Create mutation
  const createMutation = useMutation({
    mutationFn: subjectsAPI.create,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['subjects'] });
      toast.success("Subject created successfully");
      setFormOpen(false);
    },
    onError: (error) => {
      toast.error(error.message || "Failed to create subject");
    },
  });

  // Update mutation
  const updateMutation = useMutation({
    mutationFn: ({ id, data }) => subjectsAPI.update(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['subjects'] });
      toast.success("Subject updated successfully");
      setFormOpen(false);
      setEditingCourse(undefined);
    },
    onError: (error) => {
      toast.error(error.message || "Failed to update subject");
    },
  });

  // Delete mutation
  const deleteMutation = useMutation({
    mutationFn: subjectsAPI.delete,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['subjects'] });
      toast.success("Subject deleted successfully");
    },
    onError: (error) => {
      toast.error(error.message || "Failed to delete subject");
    },
  });

  const handleSort = () => {
    if (sortBy === "name") {
      setSortOrder(sortOrder === "asc" ? "desc" : "asc");
    } else {
      setSortBy("name");
      setSortOrder("asc");
    }
  };

  // Get unique programs and semesters for filters
  const programs = useMemo(() => {
    const unique = [...new Set(subjects.map(c => c.program).filter(Boolean))];
    return unique.sort();
  }, [subjects]);

  const semesters = useMemo(() => {
    const unique = [...new Set(subjects.map(c => c.semester).filter(Boolean))];
    return unique.sort();
  }, [subjects]);

  const filteredAndSortedCourses = useMemo(() => {
    let filtered = subjects.filter((subject) => {
      const matchesSearch = 
        subject.name?.toLowerCase().includes(searchQuery.toLowerCase()) ||
        subject.code?.toLowerCase().includes(searchQuery.toLowerCase());
      const matchesProgram =
        programFilter === "all" || subject.program === programFilter;
      const matchesSemester =
        semesterFilter === "all" || subject.semester === semesterFilter;
      return matchesSearch && matchesProgram && matchesSemester;
    });

    if (sortBy === "name") {
      filtered.sort((a, b) => {
        const comparison = (a.name || '').localeCompare(b.name || '');
        return sortOrder === "asc" ? comparison : -comparison;
      });
    } else if (sortBy === "code") {
      filtered.sort((a, b) => {
        const comparison = (a.code || '').localeCompare(b.code || '');
        return sortOrder === "asc" ? comparison : -comparison;
      });
    }

    return filtered;
  }, [subjects, searchQuery, programFilter, semesterFilter, sortBy, sortOrder]);

  const handleAddCourse = (courseData) => {
    // Transform form data to backend format
    // Code is used as the primary key (id)
    const backendData = {
      code: courseData.code,
      name: courseData.name,
      weekly_hours: courseData.weekly_hours,
      credits: courseData.credits || 0,
      preferred_room_type: courseData.preferred_room_type || "Theory",
      preferred_term: courseData.preferred_term || null,
      semester: courseData.semester || null,
      program: courseData.program || null,
      course_group: courseData.course_group || null,
    };
    createMutation.mutate(backendData);
  };

  const handleEditCourse = (courseData) => {
    if (editingCourse) {
      // Use code as the identifier (code = id in database)
      const subjectCode = editingCourse.code || editingCourse.id;
      const backendData = {
        code: courseData.code,
        name: courseData.name,
        weekly_hours: courseData.weekly_hours,
        credits: courseData.credits || 0,
        preferred_room_type: courseData.preferred_room_type || "Theory",
        preferred_term: courseData.preferred_term || null,
        semester: courseData.semester || null,
        program: courseData.program || null,
        course_group: courseData.course_group || null,
      };
      updateMutation.mutate({ id: subjectCode, data: backendData });
    }
  };

  const handleDeleteCourse = (subject) => {
    if (confirm("Are you sure you want to delete this subject?")) {
      // Use code as the identifier (code = id in database)
      const subjectCode = subject.code || subject.id;
      deleteMutation.mutate(subjectCode);
    }
  };

  const openEditForm = (subject) => {
    setEditingCourse(subject);
    setFormOpen(true);
  };

  const closeForm = () => {
    setFormOpen(false);
    setEditingCourse(undefined);
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Subjects</h1>
          <p className="text-muted-foreground mt-1">Manage subjects and their units</p>
        </div>
        <div className="flex items-center gap-2">
          <UIButton 
            variant="outline" 
            onClick={() => navigate("/canonical-groups")}
          >
            Subject Groups
          </UIButton>
          <UIButton variant="outline" onClick={() => setImportOpen(true)}>Import</UIButton>
          <Button className="gap-2" onClick={() => setFormOpen(true)}>
            <Plus className="h-4 w-4" />
            Add Subject
          </Button>
        </div>
      </div>

      {/* Info Card for Subject Groups */}
      <Card className="glass-card p-4 bg-primary/5 border-primary/20">
        <div className="flex items-center justify-between">
          <div className="flex items-start gap-3">
            <BookOpen className="h-5 w-5 text-primary mt-0.5" />
            <div>
              <p className="text-sm font-medium">Subject Groups</p>
              <p className="text-xs text-muted-foreground mt-1">
                Group equivalent subjects across programs (e.g., BIT1103, BCS1103 both teach "Programming in C")
              </p>
            </div>
          </div>
          <Button
            variant="outline"
            size="sm"
            onClick={() => navigate("/canonical-groups")}
          >
            Manage Groups
          </Button>
        </div>
      </Card>

      {/* Filters */}
      <Card className="glass-card p-4">
        <div className="flex flex-col sm:flex-row gap-4">
          <div className="flex-1 relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
            <Input
              placeholder="Search subjects..."
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
            <span className="ml-2">Loading subjects...</span>
          </div>
        ) : error ? (
          <div className="p-8 text-center text-destructive">
            Error loading subjects: {error.message}
          </div>
        ) : filteredAndSortedCourses.length === 0 ? (
          <div className="p-8 text-center text-muted-foreground">
            No subjects found
          </div>
        ) : (
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>
                <Button
                  variant="ghost"
                  className="h-8 px-2 hover:bg-transparent"
                    onClick={() => {
                      if (sortBy === "code") {
                        setSortOrder(sortOrder === "asc" ? "desc" : "asc");
                      } else {
                        setSortBy("code");
                        setSortOrder("asc");
                      }
                    }}
                  >
                    Code
                    <ArrowUpDown className="ml-2 h-4 w-4" />
                  </Button>
                </TableHead>
                <TableHead>
                  <Button
                    variant="ghost"
                    className="h-8 px-2 hover:bg-transparent"
                    onClick={() => {
                      if (sortBy === "name") {
                        setSortOrder(sortOrder === "asc" ? "desc" : "asc");
                      } else {
                        setSortBy("name");
                        setSortOrder("asc");
                      }
                    }}
                >
                  Subject Name
                  <ArrowUpDown className="ml-2 h-4 w-4" />
                </Button>
              </TableHead>
                <TableHead>Program</TableHead>
              <TableHead>Semester</TableHead>
                <TableHead>Hours/Week</TableHead>
                <TableHead>Room Type</TableHead>
                <TableHead>Prefered Term</TableHead>
              <TableHead className="text-right">Actions</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {filteredAndSortedCourses.map((subject) => (
              <TableRow key={subject.code || subject.id}>
                  <TableCell className="font-medium">{subject.code}</TableCell>
                <TableCell className="font-medium">{subject.name}</TableCell>
                <TableCell>
                    {subject.program ? (
                      <Badge variant="outline">{subject.program}</Badge>
                    ) : (
                      <span className="text-muted-foreground">—</span>
                    )}
                </TableCell>
                <TableCell>
                    {subject.semester ? (
                      <Badge variant="secondary">{subject.semester}</Badge>
                    ) : (
                      <span className="text-muted-foreground">—</span>
                    )}
                  </TableCell>
                  <TableCell>{subject.weekly_hours || 0} hrs</TableCell>
                  <TableCell>
                      <Badge
                      variant={subject.preferred_room_type === "Lab" ? "default" : "secondary"}
                      >
                      {subject.preferred_room_type || "Theory"}
                      </Badge>
                </TableCell>
                <TableCell>
                    {subject.preferred_term ? (
                      <Badge variant="outline">{subject.preferred_term}</Badge>
                    ) : (
                      <span className="text-muted-foreground">—</span>
                    )}
                  </TableCell>
                <TableCell className="text-right">
                  <DropdownMenu>
                    <DropdownMenuTrigger asChild>
                      <Button variant="ghost" size="sm">
                        <MoreVertical className="h-4 w-4" />
                      </Button>
                    </DropdownMenuTrigger>
                    <DropdownMenuContent align="end" className="bg-popover">
                      <DropdownMenuItem onClick={() => openEditForm(subject)}>
                        <Edit className="h-4 w-4 mr-2" />
                        Edit
                      </DropdownMenuItem>
                      <DropdownMenuItem
                        className="text-destructive"
                        onClick={() => handleDeleteCourse(subject)}
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

      <SubjectForm
        open={formOpen}
        onOpenChange={closeForm}
        onSubmit={editingCourse ? handleEditCourse : handleAddCourse}
        subject={editingCourse}
      />

      <ImportDialog
        open={importOpen}
        onOpenChange={setImportOpen}
        title="Import Subjects"
        description="Upload an Excel (.xlsx, .xls) or CSV (.csv) file to import subjects. Required columns: Subject Code, Subject Name, Program, Semester, Weekly Hours, Room Type, Prefered Term, Credits. Optional: Course Group (for Theory/Practical pairing)."
        entityType="subjects"
        requiredColumns={['Subject Code', 'Subject Name', 'Program', 'Semester', 'Weekly Hours', 'Room Type', 'Prefered Term', 'Credits']}
        onImport={async (data, onProgress) => {
          try {
            const response = await importAPI.importSubjects(data);
            queryClient.invalidateQueries({ queryKey: ['subjects'] });
            return response;
          } catch (error) {
            throw error;
          }
        }}
      />
    </div>
  );
}

