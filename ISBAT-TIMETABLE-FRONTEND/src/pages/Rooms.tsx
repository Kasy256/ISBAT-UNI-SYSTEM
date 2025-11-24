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
import { RoomForm } from "@/components/rooms/RoomForm";
import { Room } from "@/types/room";
import { toast } from "sonner";
import { Button as UIButton } from "@/components/ui/button";

export default function Rooms() {
  const [searchQuery, setSearchQuery] = useState("");
  const [typeFilter, setTypeFilter] = useState("all");
  const [formOpen, setFormOpen] = useState(false);
  const [editingRoom, setEditingRoom] = useState<Room | undefined>();
  const [sortBy, setSortBy] = useState<"roomId" | null>(null);
  const [sortOrder, setSortOrder] = useState<"asc" | "desc">("asc");

  const [rooms, setRooms] = useState<Room[]>([
    {
      id: "1",
      roomId: "R301",
      type: "Classroom",
      capacity: 40,
    },
    {
      id: "2",
      roomId: "H-A",
      type: "Lecture Hall",
      capacity: 150,
    },
    {
      id: "3",
      roomId: "L405",
      type: "Lab",
      capacity: 30,
      specialization: "Cloud Computing and Virtualization",
    },
    {
      id: "4",
      roomId: "R205",
      type: "Classroom",
      capacity: 35,
    },
  ]);

  const getTypeBadgeVariant = (type: Room["type"]) => {
    switch (type) {
      case "Lecture Hall":
        return "default";
      case "Lab":
        return "secondary";
      default:
        return "outline";
    }
  };

  const handleSort = () => {
    if (sortBy === "roomId") {
      setSortOrder(sortOrder === "asc" ? "desc" : "asc");
    } else {
      setSortBy("roomId");
      setSortOrder("asc");
    }
  };

  const filteredAndSortedRooms = useMemo(() => {
    let filtered = rooms.filter((room) => {
      const matchesSearch = room.roomId
        .toLowerCase()
        .includes(searchQuery.toLowerCase());
      const matchesType = typeFilter === "all" || room.type === typeFilter;
      return matchesSearch && matchesType;
    });

    if (sortBy === "roomId") {
      filtered.sort((a, b) => {
        const comparison = a.roomId.localeCompare(b.roomId);
        return sortOrder === "asc" ? comparison : -comparison;
      });
    }

    return filtered;
  }, [rooms, searchQuery, typeFilter, sortBy, sortOrder]);

  const handleAddRoom = (room: Omit<Room, "id">) => {
    const newRoom: Room = {
      ...room,
      id: Date.now().toString(),
    };
    setRooms([...rooms, newRoom]);
    toast.success("Room added successfully");
  };

  const handleEditRoom = (room: Omit<Room, "id">) => {
    if (editingRoom) {
      setRooms(
        rooms.map((r) => (r.id === editingRoom.id ? { ...room, id: r.id } : r))
      );
      toast.success("Room updated successfully");
      setEditingRoom(undefined);
    }
  };

  const handleDeleteRoom = (id: string) => {
    setRooms(rooms.filter((r) => r.id !== id));
    toast.success("Room deleted successfully");
  };

  const openEditForm = (room: Room) => {
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
              <SelectItem value="Classroom">Classroom</SelectItem>
              <SelectItem value="Lecture Hall">Lecture Hall</SelectItem>
              <SelectItem value="Lab">Lab</SelectItem>
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
                  Room ID
                  <ArrowUpDown className="ml-2 h-4 w-4" />
                </Button>
              </TableHead>
              <TableHead>Type</TableHead>
              <TableHead>Capacity</TableHead>
              <TableHead>Specialization</TableHead>
              <TableHead className="text-right">Actions</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {filteredAndSortedRooms.map((room) => (
              <TableRow key={room.id}>
                <TableCell className="font-medium">{room.roomId}</TableCell>
                <TableCell>
                  <Badge variant={getTypeBadgeVariant(room.type)}>
                    {room.type}
                  </Badge>
                </TableCell>
                <TableCell>
                  <span className="font-semibold">{room.capacity}</span> people
                </TableCell>
                <TableCell>
                  {room.specialization ? (
                    <Badge variant="outline" className="bg-primary/5">
                      {room.specialization}
                    </Badge>
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
