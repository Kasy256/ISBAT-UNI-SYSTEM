import React, { useState, useMemo, useEffect } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { Plus, Search, MoreVertical, Edit, Trash, ArrowUpDown, Loader2, Clock } from "lucide-react";
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
import { Checkbox } from "@/components/ui/checkbox";
import { toast } from "sonner";
import { timeSlotsAPI } from "@/lib/api";

export default function TimeSlots() {
  const queryClient = useQueryClient();
  const [searchQuery, setSearchQuery] = useState("");
  const [formOpen, setFormOpen] = useState(false);
  const [editingSlot, setEditingSlot] = useState(undefined);
  const [formData, setFormData] = useState({
    period: "",
    start: "",
    end: "",
    is_afternoon: false,
    display_name: "",
    order: 0,
  });

  // Fetch time slots from API
  const { data, isLoading, error } = useQuery({
    queryKey: ['time-slots'],
    queryFn: async () => {
      const response = await timeSlotsAPI.getAll();
      return response.time_slots || [];
    },
  });

  const timeSlots = data || [];

  // Create mutation
  const createMutation = useMutation({
    mutationFn: timeSlotsAPI.create,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['time-slots'] });
      toast.success("Time slot created successfully");
      setFormOpen(false);
      resetForm();
    },
    onError: (error) => {
      toast.error(error.message || "Failed to create time slot");
    },
  });

  // Update mutation
  const updateMutation = useMutation({
    mutationFn: ({ period, data }) => timeSlotsAPI.update(period, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['time-slots'] });
      toast.success("Time slot updated successfully");
      setFormOpen(false);
      setEditingSlot(undefined);
      resetForm();
    },
    onError: (error) => {
      toast.error(error.message || "Failed to update time slot");
    },
  });

  // Delete mutation
  const deleteMutation = useMutation({
    mutationFn: timeSlotsAPI.delete,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['time-slots'] });
      toast.success("Time slot deleted successfully");
    },
    onError: (error) => {
      toast.error(error.message || "Failed to delete time slot");
    },
  });

  const resetForm = () => {
    setFormData({
      period: "",
      start: "",
      end: "",
      is_afternoon: false,
      display_name: "",
      order: 0,
    });
  };

  const handleAdd = () => {
    setEditingSlot(undefined);
    resetForm();
    setFormOpen(true);
  };

  const handleEdit = (slot) => {
    setEditingSlot(slot);
    setFormData({
      period: slot.period,
      start: slot.start,
      end: slot.end,
      is_afternoon: slot.is_afternoon || false,
      display_name: slot.display_name || "",
      order: slot.order || 0,
    });
    setFormOpen(true);
  };

  const handleDelete = (period) => {
    if (confirm("Are you sure you want to delete this time slot?")) {
      deleteMutation.mutate(period);
    }
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    // Ensure display_name is set before submitting
    const submitData = {
      ...formData,
      display_name: formData.display_name || generateDisplayName(formData.start, formData.end)
    };
    
    if (editingSlot) {
      updateMutation.mutate({
        period: editingSlot.period,
        data: submitData,
      });
    } else {
      createMutation.mutate(submitData);
    }
  };

  const filteredTimeSlots = useMemo(() => {
    return timeSlots.filter((slot) =>
      slot.period.toLowerCase().includes(searchQuery.toLowerCase()) ||
      slot.start.includes(searchQuery) ||
      slot.end.includes(searchQuery) ||
      (slot.display_name && slot.display_name.toLowerCase().includes(searchQuery.toLowerCase()))
    );
  }, [timeSlots, searchQuery]);

  const formatTime = (time) => {
    // Convert 24-hour to 12-hour format
    const [hours, minutes] = time.split(':');
    const hour = parseInt(hours);
    const ampm = hour >= 12 ? 'PM' : 'AM';
    const hour12 = hour % 12 || 12;
    return `${hour12}:${minutes} ${ampm}`;
  };

  // Auto-generate display name from start and end times
  const generateDisplayName = (start, end) => {
    if (!start || !end) return "";
    const startFormatted = formatTime(start);
    const endFormatted = formatTime(end);
    return `${startFormatted} - ${endFormatted}`;
  };

  // Update display name when start or end time changes
  useEffect(() => {
    if (formData.start && formData.end) {
      const autoDisplayName = generateDisplayName(formData.start, formData.end);
      setFormData(prev => ({
        ...prev,
        display_name: autoDisplayName
      }));
    }
  }, [formData.start, formData.end]);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Time Slots</h1>
          <p className="text-muted-foreground mt-1">
            Manage timetable time slots for scheduling classes
          </p>
        </div>
        <Button className="gap-2" onClick={handleAdd}>
          <Plus className="h-4 w-4" />
          Add Time Slot
        </Button>
      </div>

      {/* Search */}
      <Card className="glass-card p-4">
        <div className="relative">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
          <Input
            placeholder="Search time slots..."
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
            <span className="ml-2">Loading time slots...</span>
          </div>
        ) : error ? (
          <div className="p-8 text-center text-destructive">
            Error loading time slots: {error.message}
          </div>
        ) : filteredTimeSlots.length === 0 ? (
          <div className="p-8 text-center text-muted-foreground">
            {searchQuery ? "No time slots found" : "No time slots found"}
          </div>
        ) : (
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Period</TableHead>
                <TableHead>Time</TableHead>
                <TableHead>Display Name</TableHead>
                <TableHead>Type</TableHead>
                <TableHead>Order</TableHead>
                <TableHead className="text-right">Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {filteredTimeSlots.map((slot) => (
                <TableRow key={slot.period}>
                  <TableCell className="font-mono font-medium">{slot.period}</TableCell>
                  <TableCell>
                    {formatTime(slot.start)} - {formatTime(slot.end)}
                  </TableCell>
                  <TableCell>
                    {slot.display_name || `${slot.start} - ${slot.end}`}
                  </TableCell>
                  <TableCell>
                    <Badge variant={slot.is_afternoon ? "default" : "secondary"}>
                      {slot.is_afternoon ? "Afternoon" : "Morning"}
                    </Badge>
                  </TableCell>
                  <TableCell>{slot.order || 0}</TableCell>
                  <TableCell className="text-right">
                    <DropdownMenu>
                      <DropdownMenuTrigger asChild>
                        <Button variant="ghost" size="sm">
                          <MoreVertical className="h-4 w-4" />
                        </Button>
                      </DropdownMenuTrigger>
                      <DropdownMenuContent align="end">
                        <DropdownMenuItem onClick={() => handleEdit(slot)}>
                          <Edit className="mr-2 h-4 w-4" />
                          Edit
                        </DropdownMenuItem>
                        <DropdownMenuItem
                          onClick={() => handleDelete(slot.period)}
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
              {editingSlot ? "Edit Time Slot" : "Add Time Slot"}
            </DialogTitle>
            <DialogDescription>
              {editingSlot
                ? "Update time slot information"
                : "Add a new time slot to the system"}
            </DialogDescription>
          </DialogHeader>
          <form onSubmit={handleSubmit}>
            <div className="space-y-4 py-4">
              <div className="space-y-2">
                <Label htmlFor="period">Period *</Label>
                <Input
                  id="period"
                  value={formData.period}
                  onChange={(e) => setFormData({ ...formData, period: e.target.value.toUpperCase() })}
                  placeholder="SLOT_1"
                  required
                  disabled={!!editingSlot}
                />
                <p className="text-xs text-muted-foreground">
                  Unique identifier (e.g., "SLOT_1", "SLOT_2")
                </p>
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="start">Start Time *</Label>
                  <Input
                    id="start"
                    type="time"
                    value={formData.start}
                    onChange={(e) => setFormData({ ...formData, start: e.target.value })}
                    required
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="end">End Time *</Label>
                  <Input
                    id="end"
                    type="time"
                    value={formData.end}
                    onChange={(e) => setFormData({ ...formData, end: e.target.value })}
                    required
                  />
                </div>
              </div>
              <div className="space-y-2">
                <Label htmlFor="display_name">Display Name</Label>
                <Input
                  id="display_name"
                  value={formData.display_name || generateDisplayName(formData.start, formData.end)}
                  readOnly
                  className="bg-muted"
                />
                <p className="text-xs text-muted-foreground">
                  Auto-generated from start and end times
                </p>
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="order">Order</Label>
                  <Input
                    id="order"
                    type="number"
                    min="0"
                    value={formData.order}
                    onChange={(e) => setFormData({ ...formData, order: parseInt(e.target.value) || 0 })}
                  />
                  <p className="text-xs text-muted-foreground">
                    Sort order (lower numbers appear first)
                  </p>
                </div>
                <div className="space-y-2">
                  <div className="flex items-center space-x-2 pt-6">
                    <Checkbox
                      id="is_afternoon"
                      checked={formData.is_afternoon}
                      onCheckedChange={(checked) =>
                        setFormData({ ...formData, is_afternoon: checked })
                      }
                    />
                    <Label htmlFor="is_afternoon" className="cursor-pointer">
                      Afternoon Slot
                    </Label>
                  </div>
                </div>
              </div>
            </div>
            <DialogFooter>
              <Button
                type="button"
                variant="outline"
                onClick={() => {
                  setFormOpen(false);
                  resetForm();
                  setEditingSlot(undefined);
                }}
              >
                Cancel
              </Button>
              <Button type="submit">
                {editingSlot ? "Update" : "Add"} Time Slot
              </Button>
            </DialogFooter>
          </form>
        </DialogContent>
      </Dialog>
    </div>
  );
}

