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
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from "@/components/ui/popover";
import {
  Command,
  CommandEmpty,
  CommandGroup,
  CommandInput,
  CommandItem,
  CommandList,
} from "@/components/ui/command";
import { Badge } from "@/components/ui/badge";
import { Check, X } from "lucide-react";
import { cn } from "@/lib/utils";

import { useQuery } from "@tanstack/react-query";
import { roomSpecializationsAPI } from "@/lib/api";

export function RoomForm({
  open,
  onOpenChange,
  onSubmit,
  room,
}) {
  // Fetch specializations from API
  const { data: specializationsData } = useQuery({
    queryKey: ['room-specializations'],
    queryFn: async () => {
      const response = await roomSpecializationsAPI.getAll();
      return response.room_specializations || [];
    },
  });

  const AVAILABLE_SPECIALIZATIONS = specializationsData?.map(spec => spec.id) || [];

  const [formData, setFormData] = useState({
    room_number: "",
    capacity: 30,
    room_type: "Theory",
    specializations: [],
    is_available: true,
  });
  const [specializationOpen, setSpecializationOpen] = useState(false);

  useEffect(() => {
    if (room) {
      setFormData({
        room_number: room.room_number || "",
        capacity: room.capacity || 30,
        room_type: room.room_type || "Theory",
        specializations: room.specializations || [],
        is_available: room.is_available !== undefined ? room.is_available : true,
      });
    } else {
      // Reset form for new room
      setFormData({
        room_number: "",
        capacity: 30,
        room_type: "Theory",
        specializations: [],
        is_available: true,
      });
    }
  }, [room, open]);

  const toggleSpecialization = (spec) => {
    setFormData((prev) => {
      const current = prev.specializations || [];
      if (current.includes(spec)) {
        return { ...prev, specializations: current.filter((s) => s !== spec) };
      } else {
        return { ...prev, specializations: [...current, spec] };
      }
    });
  };

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
            <div className="space-y-2">
              <Label htmlFor="room_number">Room Number *</Label>
              <Input
                id="room_number"
                value={formData.room_number}
                onChange={(e) =>
                  setFormData({ ...formData, room_number: e.target.value })
                }
                placeholder="104, L201, B-101"
                required
                disabled={!!room} // Disable room_number editing for existing rooms
              />
              <p className="text-xs text-muted-foreground">
                Room number is the unique identifier (e.g., "104", "L201", "B-101")
              </p>
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
              <Label htmlFor="specializations">Specializations</Label>
              <Popover open={specializationOpen} onOpenChange={setSpecializationOpen}>
                <PopoverTrigger asChild>
                  <Button
                    variant="outline"
                    role="combobox"
                    className="w-full justify-between"
                  >
                    {formData.specializations && formData.specializations.length > 0
                      ? `${formData.specializations.length} selected`
                      : "Select specializations..."}
                  </Button>
                </PopoverTrigger>
                <PopoverContent className="w-full p-0" align="start">
                  <Command>
                    <CommandInput placeholder="Search specializations..." />
                    <CommandList>
                      <CommandEmpty>No specialization found.</CommandEmpty>
                      <CommandGroup>
                        {specializationsData?.map((spec) => (
                          <CommandItem
                            key={spec.id}
                            value={spec.id}
                            onSelect={() => toggleSpecialization(spec.id)}
                          >
                            <Check
                              className={cn(
                                "mr-2 h-4 w-4",
                                formData.specializations?.includes(spec.id)
                                  ? "opacity-100"
                                  : "opacity-0"
                              )}
                            />
                            {spec.name} {spec.description && `- ${spec.description}`}
                          </CommandItem>
                        ))}
                      </CommandGroup>
                    </CommandList>
                  </Command>
                </PopoverContent>
              </Popover>
              {formData.specializations && formData.specializations.length > 0 && (
                <div className="flex flex-wrap gap-2 mt-2">
                  {formData.specializations.map((specId) => {
                    const spec = specializationsData?.find(s => s.id === specId);
                    return (
                      <Badge
                        key={specId}
                        variant="secondary"
                        className="flex items-center gap-1"
                      >
                        {spec?.name || specId}
                        <X
                          className="h-3 w-3 cursor-pointer"
                          onClick={() => toggleSpecialization(specId)}
                        />
                      </Badge>
                    );
                  })}
                </div>
              )}
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
