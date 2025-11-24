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
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { LecturerForm } from "@/components/lecturers/LecturerForm";
import { Lecturer } from "@/types/lecturer";
import { toast } from "sonner";
import { Button as UIButton } from "@/components/ui/button";

// Sample course units for specializations
const COURSE_UNITS = [
  { id: "cs101", code: "CS101", title: "Programming Fundamentals", faculty: "Computer Science" },
  { id: "cs102", code: "CS102", title: "Data Structures", faculty: "Computer Science" },
  { id: "cs103", code: "CS103", title: "Computer Architecture", faculty: "Computer Science" },
  { id: "cs201", code: "CS201", title: "Algorithms", faculty: "Computer Science" },
  { id: "cs202", code: "CS202", title: "Database Systems", faculty: "Computer Science" },
  { id: "bba101", code: "BBA101", title: "Business Principles", faculty: "Business" },
  { id: "bba102", code: "BBA102", title: "Marketing Fundamentals", faculty: "Business" },
];

export default function Lecturers() {
  const [searchQuery, setSearchQuery] = useState("");
  const [facultyFilter, setFacultyFilter] = useState("all");
  const [roleFilter, setRoleFilter] = useState("all");
  const [formOpen, setFormOpen] = useState(false);
  const [editingLecturer, setEditingLecturer] = useState<Lecturer | undefined>();
  const [sortBy, setSortBy] = useState<"name" | null>(null);
  const [sortOrder, setSortOrder] = useState<"asc" | "desc">("asc");

  const [lecturers, setLecturers] = useState<Lecturer[]>([
    {
      id: "1",
      name: "Dr. Sarah Johnson",
      faculty: "Computer Science",
      role: "Professor",
      specializations: ["cs101", "cs102", "cs201"],
      maxHours: 20,
    },
    {
      id: "2",
      name: "Mr. David Brown",
      faculty: "Business",
      role: "Lecturer",
      specializations: ["bba101", "bba102"],
      maxHours: 18,
    },
    {
      id: "3",
      name: "Dr. Emily Chen",
      faculty: "Computer Science",
      role: "Professor",
      specializations: ["cs103", "cs202"],
      maxHours: 16,
    },
  ]);

  const getInitials = (name: string) => {
    return name
      .split(" ")
      .map((n) => n[0])
      .join("")
      .toUpperCase();
  };

  const getUnitTitle = (unitId: string) => {
    return COURSE_UNITS.find((u) => u.id === unitId)?.title || unitId;
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

  const handleAddLecturer = (lecturer: Omit<Lecturer, "id">) => {
    const newLecturer: Lecturer = {
      ...lecturer,
      id: Date.now().toString(),
    };
    setLecturers([...lecturers, newLecturer]);
    toast.success("Lecturer added successfully");
  };

  const handleEditLecturer = (lecturer: Omit<Lecturer, "id">) => {
    if (editingLecturer) {
      setLecturers(
        lecturers.map((l) =>
          l.id === editingLecturer.id ? { ...lecturer, id: l.id } : l
        )
      );
      toast.success("Lecturer updated successfully");
      setEditingLecturer(undefined);
    }
  };

  const handleDeleteLecturer = (id: string) => {
    setLecturers(lecturers.filter((l) => l.id !== id));
    toast.success("Lecturer deleted successfully");
  };

  const openEditForm = (lecturer: Lecturer) => {
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
              <SelectItem value="Computer Science">Computer Science</SelectItem>
              <SelectItem value="Business">Business</SelectItem>
              <SelectItem value="Engineering">Engineering</SelectItem>
            </SelectContent>
          </Select>
          <Select value={roleFilter} onValueChange={setRoleFilter}>
            <SelectTrigger className="w-full sm:w-48">
              <SelectValue placeholder="Filter by Role" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All Roles</SelectItem>
              <SelectItem value="Professor">Professor</SelectItem>
              <SelectItem value="Lecturer">Lecturer</SelectItem>
              <SelectItem value="Assistant">Assistant</SelectItem>
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
                  Lecturer
                  <ArrowUpDown className="ml-2 h-4 w-4" />
                </Button>
              </TableHead>
              <TableHead>Faculty</TableHead>
              <TableHead>Specializations</TableHead>
              <TableHead>Role</TableHead>
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
                  <div className="flex flex-wrap gap-1">
                    {lecturer.specializations.map((specId) => (
                      <Badge
                        key={specId}
                        variant="outline"
                        className="bg-primary/5 text-primary border-primary/20"
                      >
                        {getUnitTitle(specId)}
                      </Badge>
                    ))}
                  </div>
                </TableCell>
                <TableCell>
                  <Badge variant="secondary">{lecturer.role}</Badge>
                </TableCell>
                <TableCell>{lecturer.maxHours} hrs</TableCell>
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
      </Card>

      <LecturerForm
        open={formOpen}
        onOpenChange={closeForm}
        onSubmit={editingLecturer ? handleEditLecturer : handleAddLecturer}
        lecturer={editingLecturer}
        availableUnits={COURSE_UNITS}
      />
    </div>
  );
}
