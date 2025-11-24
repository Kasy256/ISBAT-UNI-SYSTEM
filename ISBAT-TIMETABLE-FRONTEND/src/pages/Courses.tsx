import { useState, useMemo } from "react";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { Plus, Search, MoreVertical, Edit, Trash, ArrowUpDown } from "lucide-react";
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
import { CourseForm } from "@/components/courses/CourseForm";
import { Course } from "@/types/course";
import { toast } from "sonner";
import { Button as UIButton } from "@/components/ui/button";

export default function Courses() {
  const [searchQuery, setSearchQuery] = useState("");
  const [facultyFilter, setFacultyFilter] = useState("all");
  const [semesterFilter, setSemesterFilter] = useState("all");
  const [formOpen, setFormOpen] = useState(false);
  const [editingCourse, setEditingCourse] = useState<Course | undefined>();
  const [sortBy, setSortBy] = useState<"name" | null>(null);
  const [sortOrder, setSortOrder] = useState<"asc" | "desc">("asc");

  const [courses, setCourses] = useState<Course[]>([
    {
      id: "1",
      name: "Bachelor of Information Technology",
      faculty: "Computer Science",
      semester: "Semester 1",
      term: "Term 1",
      students: 95,
      units: [
        { code: "CS101", title: "Programming Fundamentals", hoursPerWeek: 4 },
        { code: "CS102", title: "Data Structures", hoursPerWeek: 4 },
        { code: "CS103", title: "Computer Architecture", hoursPerWeek: 3 },
      ],
    },
    {
      id: "2",
      name: "Bachelor of Business Administration",
      faculty: "Business",
      semester: "Semester 1",
      term: "Term 1",
      students: 120,
      units: [
        { code: "BBA101", title: "Business Principles", hoursPerWeek: 3 },
        { code: "BBA102", title: "Marketing Fundamentals", hoursPerWeek: 3 },
      ],
    },
  ]);

  const handleSort = () => {
    if (sortBy === "name") {
      setSortOrder(sortOrder === "asc" ? "desc" : "asc");
    } else {
      setSortBy("name");
      setSortOrder("asc");
    }
  };

  const filteredAndSortedCourses = useMemo(() => {
    let filtered = courses.filter((course) => {
      const matchesSearch = course.name
        .toLowerCase()
        .includes(searchQuery.toLowerCase());
      const matchesFaculty =
        facultyFilter === "all" || course.faculty === facultyFilter;
      const matchesSemester =
        semesterFilter === "all" || course.semester === semesterFilter;
      return matchesSearch && matchesFaculty && matchesSemester;
    });

    if (sortBy === "name") {
      filtered.sort((a, b) => {
        const comparison = a.name.localeCompare(b.name);
        return sortOrder === "asc" ? comparison : -comparison;
      });
    }

    return filtered;
  }, [courses, searchQuery, facultyFilter, semesterFilter, sortBy, sortOrder]);

  const handleAddCourse = (course: Omit<Course, "id">) => {
    const newCourse: Course = {
      ...course,
      id: Date.now().toString(),
    };
    setCourses([...courses, newCourse]);
    toast.success("Course added successfully");
  };

  const handleEditCourse = (course: Omit<Course, "id">) => {
    if (editingCourse) {
      setCourses(
        courses.map((c) =>
          c.id === editingCourse.id ? { ...course, id: c.id } : c
        )
      );
      toast.success("Course updated successfully");
      setEditingCourse(undefined);
    }
  };

  const handleDeleteCourse = (id: string) => {
    setCourses(courses.filter((c) => c.id !== id));
    toast.success("Course deleted successfully");
  };

  const handleStudentCountChange = (id: string, count: number) => {
    setCourses(
      courses.map((c) => (c.id === id ? { ...c, students: count } : c))
    );
  };

  const openEditForm = (course: Course) => {
    setEditingCourse(course);
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
          <h1 className="text-3xl font-bold tracking-tight">Courses</h1>
          <p className="text-muted-foreground mt-1">Manage courses and their units</p>
        </div>
        <div className="flex items-center gap-2">
          <UIButton variant="outline">Download Template</UIButton>
          <UIButton variant="outline">Import</UIButton>
          <Button className="gap-2" onClick={() => setFormOpen(true)}>
            <Plus className="h-4 w-4" />
            Add Course
          </Button>
        </div>
      </div>

      {/* Filters */}
      <Card className="glass-card p-4">
        <div className="flex flex-col sm:flex-row gap-4">
          <div className="flex-1 relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
            <Input
              placeholder="Search courses..."
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
              <SelectItem value="Computer Science">Computer Science</SelectItem>
              <SelectItem value="Business">Business</SelectItem>
            </SelectContent>
          </Select>
          <Select value={semesterFilter} onValueChange={setSemesterFilter}>
            <SelectTrigger className="w-full sm:w-48">
              <SelectValue placeholder="Filter by Semester" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All Semesters</SelectItem>
              <SelectItem value="Semester 1">Semester 1</SelectItem>
              <SelectItem value="Semester 2">Semester 2</SelectItem>
            </SelectContent>
          </Select>
        </div>
      </Card>

      {/* Table */}
      <Card className="glass-card">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>
                <Button
                  variant="ghost"
                  className="h-8 px-2 hover:bg-transparent"
                  onClick={handleSort}
                >
                  Course Name
                  <ArrowUpDown className="ml-2 h-4 w-4" />
                </Button>
              </TableHead>
              <TableHead>Faculty</TableHead>
              <TableHead>Semester</TableHead>
              <TableHead>Course Units</TableHead>
              <TableHead>Students</TableHead>
              <TableHead className="text-right">Actions</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {filteredAndSortedCourses.map((course) => (
              <TableRow key={course.id}>
                <TableCell className="font-medium">{course.name}</TableCell>
                <TableCell>{course.faculty}</TableCell>
                <TableCell>
                  <Badge variant="secondary">{course.semester}</Badge>
                </TableCell>
                <TableCell>
                  <div className="flex flex-wrap gap-1">
                    {course.units.map((unit) => (
                      <Badge
                        key={unit.code}
                        variant="outline"
                        className="bg-accent text-accent-foreground"
                      >
                        {unit.code} - {unit.title} ({unit.hoursPerWeek}h)
                      </Badge>
                    ))}
                  </div>
                </TableCell>
                <TableCell>
                  <Input
                    type="number"
                    min="1"
                    value={course.students}
                    onChange={(e) =>
                      handleStudentCountChange(
                        course.id,
                        parseInt(e.target.value) || 0
                      )
                    }
                    className="w-20"
                  />
                </TableCell>
                <TableCell className="text-right">
                  <DropdownMenu>
                    <DropdownMenuTrigger asChild>
                      <Button variant="ghost" size="sm">
                        <MoreVertical className="h-4 w-4" />
                      </Button>
                    </DropdownMenuTrigger>
                    <DropdownMenuContent align="end" className="bg-popover">
                      <DropdownMenuItem onClick={() => openEditForm(course)}>
                        <Edit className="h-4 w-4 mr-2" />
                        Edit
                      </DropdownMenuItem>
                      <DropdownMenuItem
                        className="text-destructive"
                        onClick={() => handleDeleteCourse(course.id)}
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
      </Card>

      <CourseForm
        open={formOpen}
        onOpenChange={closeForm}
        onSubmit={editingCourse ? handleEditCourse : handleAddCourse}
        course={editingCourse}
      />
    </div>
  );
}
