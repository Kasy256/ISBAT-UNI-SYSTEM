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
import { RoomForm } from "@/components/rooms/RoomForm";
import { toast } from "sonner";
import { Button as UIButton } from "@/components/ui/button";
import { roomsAPI } from "@/lib/api";

export default function Rooms() {
  const queryClient = useQueryClient();
  const [searchQuery, setSearchQuery] = useState("");
  const [typeFilter, setTypeFilter] = useState("all");
  const [formOpen, setFormOpen] = useState(false);
  const [editingRoom, setEditingRoom] = useState(undefined);
  const [sortBy, setSortBy] = useState(null);
  const [sortOrder, setSortOrder] = useState("asc");

  // Fetch rooms from API
  const { data, isLoading, error } = useQuery({
    queryKey: ['rooms'],
    queryFn: async () => {
      const response = await roomsAPI.getAll();
      return response.rooms || [];
    },
  });

  const rooms = data || [];

  // Create mutation
  const createMutation = useMutation({
    mutationFn: roomsAPI.create,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['rooms'] });
      toast.success("Room created successfully");
      setFormOpen(false);
    },
    onError: (error) => {
      toast.error(error.message || "Failed to create room");
    },
  });

  // Update mutation
  const updateMutation = useMutation({
    mutationFn: ({ id, data }) => roomsAPI.update(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['rooms'] });
      toast.success("Room updated successfully");
      setFormOpen(false);
      setEditingRoom(undefined);
    },
    onError: (error) => {
      toast.error(error.message || "Failed to update room");
    },
  });

  // Delete mutation
  const deleteMutation = useMutation({
    mutationFn: roomsAPI.delete,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['rooms'] });
      toast.success("Room deleted successfully");
    },
    onError: (error) => {
      toast.error(error.message || "Failed to delete room");
    },
  });

  const getTypeBadgeVariant = (type) => {
    switch (type) {
      case "Lab":
        return "default";
      case "Theory":
        return "secondary";
      default:
        return "outline";
    }
  };

  const handleSort = () => {
    if (sortBy === "room_number") {
      setSortOrder(sortOrder === "asc" ? "desc" : "asc");
    } else {
      setSortBy("room_number");
      setSortOrder("asc");
    }
  };

  const filteredAndSortedRooms = useMemo(() => {
    let filtered = rooms.filter((room) => {
      const matchesSearch =
        room.room_number?.toLowerCase().includes(searchQuery.toLowerCase()) ||
        room.id?.toLowerCase().includes(searchQuery.toLowerCase());
      const matchesType = typeFilter === "all" || room.room_type === typeFilter;
      return matchesSearch && matchesType;
    });

    if (sortBy === "room_number") {
      filtered.sort((a, b) => {
        const comparison = (a.room_number || '').localeCompare(b.room_number || '');
        return sortOrder === "asc" ? comparison : -comparison;
      });
    }

    return filtered;
  }, [rooms, searchQuery, typeFilter, sortBy, sortOrder]);

  const handleAddRoom = (roomData) => {
    createMutation.mutate(roomData);
  };

  const handleEditRoom = (roomData) => {
    if (editingRoom) {
      updateMutation.mutate({ id: editingRoom.id, data: roomData });
    }
  };

  const handleDeleteRoom = (id) => {
    if (confirm("Are you sure you want to delete this room?")) {
      deleteMutation.mutate(id);
    }
  };

  const openEditForm = (room) => {
    setEditingRoom(room);
    setFormOpen(true);
  };

  const closeForm = () => {
    setFormOpen(false);
    setEditingRoom(undefined);
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Rooms</h1>
          <p className="text-muted-foreground mt-1">
            Manage available rooms and facilities
          </p>
        </div>
        <div className="flex items-center gap-2">
          <UIButton variant="outline">Download Template</UIButton>
          <UIButton variant="outline">Import</UIButton>
          <Button className="gap-2" onClick={() => setFormOpen(true)}>
            <Plus className="h-4 w-4" />
            Add Room
          </Button>
        </div>
      </div>

      {/* Filters */}
      <Card className="glass-card p-4">
        <div className="flex flex-col sm:flex-row gap-4">
          <div className="flex-1 relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
            <Input
              placeholder="Search rooms..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="pl-10"
            />
          </div>
          <Select value={typeFilter} onValueChange={setTypeFilter}>
            <SelectTrigger className="w-full sm:w-48">
              <SelectValue placeholder="Filter by Type" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All Types</SelectItem>
              <SelectItem value="Theory">Theory</SelectItem>
              <SelectItem value="Lab">Lab</SelectItem>
            </SelectContent>
          </Select>
        </div>
      </Card>

      {/* Table */}
      <Card className="glass-card">
        {isLoading ? (
          <div className="flex items-center justify-center p-8">
            <Loader2 className="h-6 w-6 animate-spin" />
            <span className="ml-2">Loading rooms...</span>
          </div>
        ) : error ? (
          <div className="p-8 text-center text-destructive">
            Error loading rooms: {error.message}
          </div>
        ) : filteredAndSortedRooms.length === 0 ? (
          <div className="p-8 text-center text-muted-foreground">
            No rooms found
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
                    Room Number
                    <ArrowUpDown className="ml-2 h-4 w-4" />
                  </Button>
                </TableHead>
                <TableHead>Type</TableHead>
                <TableHead>Capacity</TableHead>
                <TableHead>Status</TableHead>
                <TableHead className="text-right">Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {filteredAndSortedRooms.map((room) => (
                <TableRow key={room.id}>
                  <TableCell className="font-medium">{room.room_number}</TableCell>
                  <TableCell>
                    <Badge variant={getTypeBadgeVariant(room.room_type)}>
                      {room.room_type}
                    </Badge>
                  </TableCell>
                  <TableCell>
                    <span className="font-semibold">{room.capacity}</span> people
                  </TableCell>
                  <TableCell>
                    <Badge
                      variant={room.is_available ? "default" : "secondary"}
                    >
                      {room.is_available ? "Available" : "Unavailable"}
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
                        <DropdownMenuItem onClick={() => openEditForm(room)}>
                          <Edit className="h-4 w-4 mr-2" />
                          Edit
                        </DropdownMenuItem>
                        <DropdownMenuItem
                          className="text-destructive"
                          onClick={() => handleDeleteRoom(room.id)}
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

      <RoomForm
        open={formOpen}
        onOpenChange={closeForm}
        onSubmit={editingRoom ? handleEditRoom : handleAddRoom}
        room={editingRoom}
      />
    </div>
  );
}
