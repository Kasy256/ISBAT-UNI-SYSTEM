import { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";

export function RoomForm({
  open,
  onOpenChange,
  onSubmit,
  room,
}) {
  const [formData, setFormData] = useState({
    id: "",
    room_number: "",
    capacity: 30,
    room_type: "Theory",
    is_available: true,
  });

  useEffect(() => {
    if (room) {
      setFormData({
        id: room.id || "",
        room_number: room.room_number || "",
        capacity: room.capacity || 30,
        room_type: room.room_type || "Theory",
        is_available: room.is_available !== undefined ? room.is_available : true,
      });
    } else {
      // Reset form for new room
      setFormData({
        id: "",
        room_number: "",
        capacity: 30,
        room_type: "Theory",
        is_available: true,
      });
    }
  }, [room, open]);

  const handleSubmit = (e) => {
    e.preventDefault();
    onSubmit(formData);
  };


  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-[500px] max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>{room ? "Edit Room" : "Add Room"}</DialogTitle>
          <DialogDescription>
            {room
              ? "Update room information"
              : "Add a new room to the system"}
          </DialogDescription>
        </DialogHeader>
        <form onSubmit={handleSubmit}>
          <div className="space-y-4 py-4">
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="id">Room ID *</Label>
                <Input
                  id="id"
                  value={formData.id}
                  onChange={(e) =>
                    setFormData({ ...formData, id: e.target.value })
                  }
                  placeholder="R001"
                  required
                  disabled={!!room} // Disable ID editing for existing rooms
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="room_number">Room Number *</Label>
                <Input
                  id="room_number"
                  value={formData.room_number}
                  onChange={(e) =>
                    setFormData({ ...formData, room_number: e.target.value })
                  }
                  placeholder="L201"
                  required
                />
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="capacity">Capacity *</Label>
                <Input
                  id="capacity"
                  type="number"
                  min="1"
                  value={formData.capacity}
                  onChange={(e) =>
                    setFormData({
                      ...formData,
                      capacity: parseInt(e.target.value) || 0,
                    })
                  }
                  required
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="room_type">Room Type *</Label>
                <Select
                  value={formData.room_type}
                  onValueChange={(value) =>
                    setFormData({ ...formData, room_type: value })
                  }
                >
                  <SelectTrigger>
                    <SelectValue placeholder="Select type" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="Theory">Theory</SelectItem>
                    <SelectItem value="Lab">Lab</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>

            <div className="space-y-2">
              <Label htmlFor="is_available">Status</Label>
              <Select
                value={formData.is_available ? "available" : "unavailable"}
                onValueChange={(value) =>
                  setFormData({
                    ...formData,
                    is_available: value === "available",
                  })
                }
              >
                <SelectTrigger>
                  <SelectValue placeholder="Select status" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="available">Available</SelectItem>
                  <SelectItem value="unavailable">Unavailable</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>
          <DialogFooter>
            <Button
              type="button"
              variant="outline"
              onClick={() => onOpenChange(false)}
            >
              Cancel
            </Button>
            <Button type="submit">{room ? "Update" : "Add"} Room</Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}
