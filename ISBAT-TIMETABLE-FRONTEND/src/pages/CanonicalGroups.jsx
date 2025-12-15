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
import { CanonicalGroupForm } from "@/components/canonical-groups/CanonicalGroupForm";
import ImportDialog from "@/components/ImportDialog";
import { toast } from "sonner";
import { Button as UIButton } from "@/components/ui/button";
import { canonicalGroupsAPI, subjectsAPI, importAPI } from "@/lib/api";

export default function CanonicalGroups() {
  const queryClient = useQueryClient();
  const [searchQuery, setSearchQuery] = useState("");
  const [formOpen, setFormOpen] = useState(false);
  const [importOpen, setImportOpen] = useState(false);
  const [editingGroup, setEditingGroup] = useState(undefined);
  const [sortBy, setSortBy] = useState(null);
  const [sortOrder, setSortOrder] = useState("asc");

  // Fetch canonical groups from API
  const { data, isLoading, error } = useQuery({
    queryKey: ['canonical-groups'],
    queryFn: async () => {
      const response = await canonicalGroupsAPI.getAll();
      return response.canonical_groups || [];
    },
  });

  // Fetch subjects for reference
  const { data: coursesData } = useQuery({
    queryKey: ['subjects'],
    queryFn: async () => {
      const response = await subjectsAPI.getAll();
      return response.subjects || [];
    },
  });

  const groups = data || [];
  const subjects = coursesData || [];

  // Create mutation
  const createMutation = useMutation({
    mutationFn: canonicalGroupsAPI.create,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['canonical-groups'] });
      toast.success("Subject group created successfully");
      setFormOpen(false);
    },
    onError: (error) => {
      toast.error(error.message || "Failed to create subject group");
    },
  });

  // Update mutation
  const updateMutation = useMutation({
    mutationFn: ({ id, data }) => canonicalGroupsAPI.update(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['canonical-groups'] });
      toast.success("Subject group updated successfully");
      setFormOpen(false);
      setEditingGroup(undefined);
    },
    onError: (error) => {
      toast.error(error.message || "Failed to update subject group");
    },
  });

  // Delete mutation
  const deleteMutation = useMutation({
    mutationFn: canonicalGroupsAPI.delete,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['canonical-groups'] });
      toast.success("Subject group deleted successfully");
    },
    onError: (error) => {
      toast.error(error.message || "Failed to delete subject group");
    },
  });

  const handleSort = () => {
    if (sortBy === "canonical_id") {
      setSortOrder(sortOrder === "asc" ? "desc" : "asc");
    } else {
      setSortBy("canonical_id");
      setSortOrder("asc");
    }
  };

  const filteredAndSortedGroups = useMemo(() => {
    let filtered = groups.filter((group) => {
      const matchesSearch =
        group.canonical_id?.toLowerCase().includes(searchQuery.toLowerCase()) ||
        group.name?.toLowerCase().includes(searchQuery.toLowerCase()) ||
        group.course_codes?.some(code =>
          code.toLowerCase().includes(searchQuery.toLowerCase())
        );
      return matchesSearch;
    });

    if (sortBy === "canonical_id") {
      filtered.sort((a, b) => {
        const comparison = (a.canonical_id || '').localeCompare(b.canonical_id || '');
        return sortOrder === "asc" ? comparison : -comparison;
      });
    } else if (sortBy === "name") {
      filtered.sort((a, b) => {
        const comparison = (a.name || '').localeCompare(b.name || '');
        return sortOrder === "asc" ? comparison : -comparison;
      });
    }

    return filtered;
  }, [groups, searchQuery, sortBy, sortOrder]);

  const handleAddGroup = (groupData) => {
    createMutation.mutate(groupData);
  };

  const handleEditGroup = (groupData) => {
    if (editingGroup) {
      updateMutation.mutate({ id: editingGroup.canonical_id, data: groupData });
    }
  };

  const handleDeleteGroup = (canonicalId) => {
    if (confirm("Are you sure you want to delete this subject group?")) {
      deleteMutation.mutate(canonicalId);
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

  const getCourseName = (courseCode) => {
    const subject = subjects.find(c => c.code === courseCode);
    return subject ? `${subject.code} - ${subject.name}` : courseCode;
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Subject Groups</h1>
          <p className="text-muted-foreground mt-1">
            Group equivalent subjects across different programs
          </p>
        </div>
        <div className="flex items-center gap-2">
          <UIButton variant="outline" onClick={() => setImportOpen(true)}>Import</UIButton>
          <Button className="gap-2" onClick={() => setFormOpen(true)}>
            <Plus className="h-4 w-4" />
            Add Subject Group
          </Button>
        </div>
      </div>

      {/* Info Card */}
      <Card className="glass-card p-4 bg-primary/5 border-primary/20">
        <div className="flex items-start gap-3">
          <BookOpen className="h-5 w-5 text-primary mt-0.5" />
          <div>
            <p className="text-sm font-medium">What are Subject Groups?</p>
            <p className="text-xs text-muted-foreground mt-1">
              Subject groups link equivalent subjects across programs. For example, "Programming in C" 
              might be taught as BIT1103, BCS1103, and BBA1103 in different programs, but they're the same subject.
              This helps with lecturer assignment and resource sharing.
            </p>
          </div>
        </div>
      </Card>

      {/* Search */}
      <Card className="glass-card p-4">
        <div className="flex-1 relative">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
          <Input
            placeholder="Search by group ID, name, or subject codes..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="pl-10"
          />
        </div>
      </Card>

      {/* Table */}
      <Card className="glass-card">
        {isLoading ? (
          <div className="flex items-center justify-center p-8">
            <Loader2 className="h-6 w-6 animate-spin" />
            <span className="ml-2">Loading subject groups...</span>
          </div>
        ) : error ? (
          <div className="p-8 text-center text-destructive">
            Error loading subject groups: {error.message}
          </div>
        ) : filteredAndSortedGroups.length === 0 ? (
          <div className="p-8 text-center text-muted-foreground">
            No subject groups found
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
                <TableHead>Name</TableHead>
                <TableHead>Subject Codes</TableHead>
                <TableHead>Description</TableHead>
                <TableHead className="text-right">Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {filteredAndSortedGroups.map((group) => (
                <TableRow key={group.canonical_id}>
                  <TableCell className="font-medium">
                    <Badge variant="outline">{group.canonical_id}</Badge>
                  </TableCell>
                  <TableCell className="font-medium">{group.name}</TableCell>
                  <TableCell>
                    {group.course_codes && group.course_codes.length > 0 ? (
                      <div className="flex flex-wrap gap-1">
                        {group.course_codes.map((code) => (
                          <Badge
                            key={code}
                            variant="secondary"
                            className="bg-primary/5 text-primary border-primary/20"
                          >
                            {getCourseName(code)}
                          </Badge>
                        ))}
                      </div>
                    ) : (
                      <span className="text-muted-foreground text-sm">No subjects</span>
                    )}
                  </TableCell>
                  <TableCell>
                    {group.description ? (
                      <p className="text-sm text-muted-foreground max-w-xs truncate">
                        {group.description}
                      </p>
                    ) : (
                      <span className="text-muted-foreground text-sm">—</span>
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
                        <DropdownMenuItem onClick={() => openEditForm(group)}>
                          <Edit className="h-4 w-4 mr-2" />
                          Edit
                        </DropdownMenuItem>
                        <DropdownMenuItem
                          className="text-destructive"
                          onClick={() => handleDeleteGroup(group.canonical_id)}
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

      <CanonicalGroupForm
        open={formOpen}
        onOpenChange={closeForm}
        onSubmit={editingGroup ? handleEditGroup : handleAddGroup}
        group={editingGroup}
        availableCourses={subjects}
      />

      <ImportDialog
        open={importOpen}
        onOpenChange={setImportOpen}
        title="Import Subject Groups"
        description="Upload an Excel (.xlsx, .xls) or CSV (.csv) file to import subject groups. Required columns: Group Id, Subject Name, Subject Codes (comma-separated subject codes, e.g., 'BIT1101, BIT1102, BIT1103'), Description."
        entityType="canonical-groups"
        requiredColumns={['Group Id', 'Subject Name', 'Subject Codes', 'Description']}
        onImport={async (data, onProgress) => {
          try {
            const response = await importAPI.importCanonicalGroups(data);
            queryClient.invalidateQueries({ queryKey: ['canonical-groups'] });
            return response;
          } catch (error) {
            throw error;
          }
        }}
      />
    </div>
  );
}

