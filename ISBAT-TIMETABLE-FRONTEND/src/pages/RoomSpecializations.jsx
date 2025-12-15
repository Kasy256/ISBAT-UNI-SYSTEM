import { useState, useMemo } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { Plus, Search, MoreVertical, Edit, Trash, ArrowUpDown, Loader2, Tag } from "lucide-react";
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
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { toast } from "sonner";
import { roomSpecializationsAPI } from "@/lib/api";

export default function RoomSpecializations() {
  const queryClient = useQueryClient();
  const [searchQuery, setSearchQuery] = useState("");
  const [formOpen, setFormOpen] = useState(false);
  const [editingSpec, setEditingSpec] = useState(undefined);
  const [formData, setFormData] = useState({
    id: "",
    name: "",
    description: "",
  });

  // Fetch room specializations from API
  const { data, isLoading, error } = useQuery({
    queryKey: ['room-specializations'],
    queryFn: async () => {
      const response = await roomSpecializationsAPI.getAll();
      return response.room_specializations || [];
    },
  });

  const specializations = data || [];

  // Create mutation
  const createMutation = useMutation({
    mutationFn: roomSpecializationsAPI.create,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['room-specializations'] });
      toast.success("Room specialization created successfully");
      setFormOpen(false);
      resetForm();
    },
    onError: (error) => {
      toast.error(error.message || "Failed to create room specialization");
    },
  });

  // Update mutation
  const updateMutation = useMutation({
    mutationFn: ({ id, data }) => roomSpecializationsAPI.update(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['room-specializations'] });
      toast.success("Room specialization updated successfully");
      setFormOpen(false);
      setEditingSpec(undefined);
      resetForm();
    },
    onError: (error) => {
      toast.error(error.message || "Failed to update room specialization");
    },
  });

  // Delete mutation
  const deleteMutation = useMutation({
    mutationFn: roomSpecializationsAPI.delete,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['room-specializations'] });
      toast.success("Room specialization deleted successfully");
    },
    onError: (error) => {
      toast.error(error.message || "Failed to delete room specialization");
    },
  });

  const resetForm = () => {
    setFormData({
      id: "",
      name: "",
      description: "",
    });
  };

  const handleAdd = () => {
    setEditingSpec(undefined);
    resetForm();
    setFormOpen(true);
  };

  const handleEdit = (spec) => {
    setEditingSpec(spec);
    setFormData({
      id: spec.id,
      name: spec.name,
      description: spec.description || "",
    });
    setFormOpen(true);
  };

  const handleDelete = (id) => {
    if (confirm("Are you sure you want to delete this room specialization?")) {
      deleteMutation.mutate(id);
    }
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (editingSpec) {
      updateMutation.mutate({
        id: editingSpec.id,
        data: formData,
      });
    } else {
      createMutation.mutate(formData);
    }
  };

  const filteredSpecializations = useMemo(() => {
    return specializations.filter((spec) =>
      spec.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      spec.id.toLowerCase().includes(searchQuery.toLowerCase()) ||
      (spec.description && spec.description.toLowerCase().includes(searchQuery.toLowerCase()))
    );
  }, [specializations, searchQuery]);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Room Specializations</h1>
          <p className="text-muted-foreground mt-1">
            Manage room specializations for categorizing and matching rooms to subjects
          </p>
        </div>
        <Button className="gap-2" onClick={handleAdd}>
          <Plus className="h-4 w-4" />
          Add Specialization
        </Button>
      </div>

      {/* Search */}
      <Card className="glass-card p-4">
        <div className="relative">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
          <Input
            placeholder="Search specializations..."
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
            <span className="ml-2">Loading specializations...</span>
          </div>
        ) : error ? (
          <div className="p-8 text-center text-destructive">
            Error loading specializations: {error.message}
          </div>
        ) : filteredSpecializations.length === 0 ? (
          <div className="p-8 text-center text-muted-foreground">
            {searchQuery ? "No specializations found" : "No room specializations found"}
          </div>
        ) : (
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>ID</TableHead>
                <TableHead>Name</TableHead>
                <TableHead>Description</TableHead>
                <TableHead className="text-right">Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {filteredSpecializations.map((spec) => (
                <TableRow key={spec.id}>
                  <TableCell className="font-mono">{spec.id}</TableCell>
                  <TableCell className="font-medium">{spec.name}</TableCell>
                  <TableCell className="text-muted-foreground">
                    {spec.description || "—"}
                  </TableCell>
                  <TableCell className="text-right">
                    <DropdownMenu>
                      <DropdownMenuTrigger asChild>
                        <Button variant="ghost" size="sm">
                          <MoreVertical className="h-4 w-4" />
                        </Button>
                      </DropdownMenuTrigger>
                      <DropdownMenuContent align="end">
                        <DropdownMenuItem onClick={() => handleEdit(spec)}>
                          <Edit className="mr-2 h-4 w-4" />
                          Edit
                        </DropdownMenuItem>
                        <DropdownMenuItem
                          onClick={() => handleDelete(spec.id)}
                          className="text-destructive"
                        >
                          <Trash className="mr-2 h-4 w-4" />
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

      {/* Form Dialog */}
      <Dialog open={formOpen} onOpenChange={setFormOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>
              {editingSpec ? "Edit Room Specialization" : "Add Room Specialization"}
            </DialogTitle>
            <DialogDescription>
              {editingSpec
                ? "Update room specialization information"
                : "Add a new room specialization to the system"}
            </DialogDescription>
          </DialogHeader>
          <form onSubmit={handleSubmit}>
            <div className="space-y-4 py-4">
              <div className="space-y-2">
                <Label htmlFor="id">ID *</Label>
                <Input
                  id="id"
                  value={formData.id}
                  onChange={(e) => setFormData({ ...formData, id: e.target.value.toUpperCase() })}
                  placeholder="ICT"
                  required
                  disabled={!!editingSpec}
                />
                <p className="text-xs text-muted-foreground">
                  Unique identifier (e.g., "ICT", "Programming", "Theory")
                </p>
              </div>
              <div className="space-y-2">
                <Label htmlFor="name">Name *</Label>
                <Input
                  id="name"
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                  placeholder="Information and Communication Technology"
                  required
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="description">Description</Label>
                <Textarea
                  id="description"
                  value={formData.description}
                  onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                  placeholder="Optional description for this specialization"
                  rows={3}
                />
              </div>
            </div>
            <DialogFooter>
              <Button
                type="button"
                variant="outline"
                onClick={() => {
                  setFormOpen(false);
                  resetForm();
                  setEditingSpec(undefined);
                }}
              >
                Cancel
              </Button>
              <Button type="submit">
                {editingSpec ? "Update" : "Add"} Specialization
              </Button>
            </DialogFooter>
          </form>
        </DialogContent>
      </Dialog>
    </div>
  );
}

