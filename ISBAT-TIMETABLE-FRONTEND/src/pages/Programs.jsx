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
import { ProgramForm } from "@/components/programs/ProgramForm";
import ImportDialog from "@/components/ImportDialog";
import { toast } from "sonner";
import { Button as UIButton } from "@/components/ui/button";
import { programsAPI, subjectsAPI, importAPI } from "@/lib/api";

export default function Programs() {
  const queryClient = useQueryClient();
  const [searchQuery, setSearchQuery] = useState("");
  const [programFilter, setProgramFilter] = useState("all");
  const [semesterFilter, setSemesterFilter] = useState("all");
  const [formOpen, setFormOpen] = useState(false);
  const [importOpen, setImportOpen] = useState(false);
  const [editingProgram, setEditingProgram] = useState(undefined);
  const [sortBy, setSortBy] = useState(null);
  const [sortOrder, setSortOrder] = useState("asc");

  // Fetch programs from API
  const { data, isLoading, error } = useQuery({
    queryKey: ['programs'],
    queryFn: async () => {
      const response = await programsAPI.getAll();
      return response.programs || [];
    },
  });

  // Fetch subjects for subject assignment
  const { data: coursesData } = useQuery({
    queryKey: ['subjects'],
    queryFn: async () => {
      const response = await subjectsAPI.getAll();
      return response.subjects || [];
    },
  });

  const programEntries = data || [];
  const subjects = coursesData || [];

  // Get unique values for filters
  const programNames = useMemo(() => {
    const unique = [...new Set(programEntries.map(p => p.program).filter(Boolean))];
    return unique.sort();
  }, [programEntries]);

  const semesters = useMemo(() => {
    const unique = [...new Set(programEntries.map(p => p.semester).filter(Boolean))];
    return unique.sort();
  }, [programEntries]);

  // Create mutation
  const createMutation = useMutation({
    mutationFn: programsAPI.create,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['programs'] });
      toast.success("Program created successfully");
      setFormOpen(false);
    },
    onError: (error) => {
      toast.error(error.message || "Failed to create program");
    },
  });

  // Update mutation
  const updateMutation = useMutation({
    mutationFn: ({ id, data }) => programsAPI.update(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['programs'] });
      toast.success("Program updated successfully");
      setFormOpen(false);
      setEditingProgram(undefined);
    },
    onError: (error) => {
      toast.error(error.message || "Failed to update program");
    },
  });

  // Delete mutation
  const deleteMutation = useMutation({
    mutationFn: programsAPI.delete,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['programs'] });
      toast.success("Program deleted successfully");
    },
    onError: (error) => {
      toast.error(error.message || "Failed to delete program");
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

  const filteredPrograms = useMemo(() => {
    let filtered = programEntries.filter((programEntry) => {
      const matchesSearch =
        programEntry.id?.toLowerCase().includes(searchQuery.toLowerCase()) ||
        programEntry.batch?.toLowerCase().includes(searchQuery.toLowerCase()) ||
        programEntry.program?.toLowerCase().includes(searchQuery.toLowerCase());
      const matchesProgram =
        programFilter === "all" || programEntry.program === programFilter;
      const matchesSemester =
        semesterFilter === "all" || programEntry.semester === semesterFilter;
      return matchesSearch && matchesProgram && matchesSemester;
    });

    if (sortBy === "id") {
      filtered.sort((a, b) => {
        const comparison = (a.id || '').localeCompare(b.id || '');
        return sortOrder === "asc" ? comparison : -comparison;
      });
    }

    return filtered;
  }, [programEntries, searchQuery, programFilter, semesterFilter, sortBy, sortOrder]);

  const handleAddProgram = (programData) => {
    createMutation.mutate(programData);
  };

  const handleEditProgram = (programData) => {
    if (editingProgram) {
      updateMutation.mutate({ id: editingProgram.id, data: programData });
    }
  };

  const handleDeleteProgram = (id) => {
    if (confirm("Are you sure you want to delete this program?")) {
      deleteMutation.mutate(id);
    }
  };

  const openEditForm = (program) => {
    setEditingProgram(program);
    setFormOpen(true);
  };

  const closeForm = () => {
    setFormOpen(false);
    setEditingProgram(undefined);
  };

  const getCourseName = (courseIdOrObj) => {
    // Handle both string IDs and object {code, name}
    if (typeof courseIdOrObj === 'object' && courseIdOrObj !== null) {
      return `${courseIdOrObj.code || ''} - ${courseIdOrObj.name || ''}`;
    }
    const subject = subjects.find(c => c.id === courseIdOrObj || c.code === courseIdOrObj);
    return subject ? `${subject.code} - ${subject.name}` : courseIdOrObj;
  };

  const getCourseKey = (courseIdOrObj) => {
    // Get a unique key for the subject
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
          <h1 className="text-3xl font-bold tracking-tight">Programs</h1>
          <p className="text-muted-foreground mt-1">
            Manage academic programs and assign subjects
          </p>
        </div>
        <div className="flex items-center gap-2">
          <UIButton variant="outline" onClick={() => setImportOpen(true)}>Import</UIButton>
          <Button className="gap-2" onClick={() => setFormOpen(true)}>
            <Plus className="h-4 w-4" />
            Add Program
          </Button>
        </div>
      </div>

      {/* Filters */}
      <Card className="glass-card p-4">
        <div className="flex flex-col sm:flex-row gap-4">
          <div className="flex-1 relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
            <Input
              placeholder="Search programs..."
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
              {programNames.map((programName) => (
                <SelectItem key={programName} value={programName}>
                  {programName}
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
            <span className="ml-2">Loading programs...</span>
          </div>
        ) : error ? (
          <div className="p-8 text-center text-destructive">
            Error loading programs: {error.message}
          </div>
        ) : filteredPrograms.length === 0 ? (
          <div className="p-8 text-center text-muted-foreground">
            No programs found
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
                    Program Code
                    <ArrowUpDown className="ml-2 h-4 w-4" />
                  </Button>
                </TableHead>
                <TableHead>Program Name</TableHead>
                <TableHead>BATCH</TableHead>
                <TableHead>Semester</TableHead>
                <TableHead>Student Size</TableHead>
                <TableHead>Subjects</TableHead>
                <TableHead>Status</TableHead>
                <TableHead className="text-right">Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {filteredPrograms.map((programEntry) => (
                <TableRow key={programEntry.id}>
                  <TableCell className="font-medium">{programEntry.id}</TableCell>
                  <TableCell>{programEntry.program}</TableCell>
                  <TableCell>{programEntry.batch}</TableCell>
                  <TableCell>
                    <Badge variant="secondary">{programEntry.semester}</Badge>
                  </TableCell>
                  <TableCell>
                    <div className="flex items-center gap-1">
                      <Users className="h-4 w-4 text-muted-foreground" />
                      <span className="font-semibold">{programEntry.size}</span>
                    </div>
                  </TableCell>
                  <TableCell>
                    {programEntry.course_units && programEntry.course_units.length > 0 ? (
                      <div className="flex flex-wrap gap-1">
                        {programEntry.course_units.slice(0, 3).map((courseIdOrObj, index) => (
                          <Badge
                            key={getCourseKey(courseIdOrObj) || index}
                            variant="outline"
                            className="bg-primary/5 text-primary border-primary/20 text-xs"
                          >
                            {getCourseName(courseIdOrObj)}
                          </Badge>
                        ))}
                        {programEntry.course_units.length > 3 && (
                          <Badge variant="outline" className="text-xs">
                            +{programEntry.course_units.length - 3} more
                          </Badge>
                        )}
                      </div>
                    ) : (
                      <span className="text-muted-foreground text-sm">No subjects</span>
                    )}
                  </TableCell>
                  <TableCell>
                    <Badge
                      variant={programEntry.is_active ? "default" : "secondary"}
                    >
                      {programEntry.is_active ? "Active" : "Inactive"}
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
                        <DropdownMenuItem onClick={() => openEditForm(programEntry)}>
                          <Edit className="h-4 w-4 mr-2" />
                          Edit
                        </DropdownMenuItem>
                        <DropdownMenuItem
                          className="text-destructive"
                          onClick={() => handleDeleteProgram(programEntry.id)}
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

      <ProgramForm
        open={formOpen}
        onOpenChange={closeForm}
        onSubmit={editingProgram ? handleEditProgram : handleAddProgram}
        program={editingProgram}
        availableCourses={subjects}
      />

      <ImportDialog
        open={importOpen}
        onOpenChange={setImportOpen}
        title="Import Programs"
        description="Upload an Excel (.xlsx, .xls) or CSV (.csv) file to import programs. Required columns: Program Code, Program Name, Faculty, Batch, Semester, Student Size, Subjects (comma-separated subject codes, e.g., 'BIT1101, BIT1102, BIT1103')."
        entityType="programs"
        requiredColumns={['Program Code', 'Program Name', 'Faculty', 'Batch', 'Semester', 'Student Size', 'Subjects']}
        onImport={async (data, onProgress) => {
          try {
            const response = await importAPI.importPrograms(data);
            queryClient.invalidateQueries({ queryKey: ['programs'] });
            return response;
          } catch (error) {
            throw error;
          }
        }}
      />
    </div>
  );
}

