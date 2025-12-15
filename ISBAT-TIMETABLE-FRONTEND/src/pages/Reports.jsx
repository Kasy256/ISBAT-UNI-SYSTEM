import React, { useState, useMemo, useEffect } from "react";
import { useQuery } from "@tanstack/react-query";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Label } from "@/components/ui/label";
import { Button } from "@/components/ui/button";
import { Loader2, FileText, Users, Home, Download, Play } from "lucide-react";
import { timetableAPI } from "@/lib/api";
import { toast } from "sonner";

const DAYS = ["MON", "TUE", "WED", "THU", "FRI"];
const DAY_NAMES = {
  MON: "Monday",
  TUE: "Tuesday",
  WED: "Wednesday",
  THU: "Thursday",
  FRI: "Friday",
};

export default function Reports() {
  const [selectedTimetableId, setSelectedTimetableId] = useState("");
  const [reportType, setReportType] = useState("both"); // "both", "lecturers", "rooms"
  const [showReports, setShowReports] = useState(false);
  
  // Filters for displayed reports
  const [filterLecturer, setFilterLecturer] = useState("all");
  const [filterRoom, setFilterRoom] = useState("all");

  // Fetch timetables list
  const { data: timetablesData, isLoading: timetablesLoading } = useQuery({
    queryKey: ["timetables"],
    queryFn: async () => {
      const response = await timetableAPI.list();
      return response.timetables || [];
    },
  });

  // Fetch selected timetable data
  const { data: timetableData, isLoading: timetableLoading } = useQuery({
    queryKey: ["timetable", selectedTimetableId],
    queryFn: async () => {
      if (!selectedTimetableId) return null;
      return await timetableAPI.getById(selectedTimetableId);
    },
    enabled: !!selectedTimetableId,
  });

  // Reset filters and hide reports when timetable changes
  useEffect(() => {
    setReportType("both");
    setShowReports(false);
    setFilterLecturer("all");
    setFilterRoom("all");
  }, [selectedTimetableId]);

  // Hide reports when report type changes
  useEffect(() => {
    setShowReports(false);
  }, [reportType]);

  // Handle Generate button
  const handleGenerate = () => {
    if (!selectedTimetableId) {
      toast.error("Please select a timetable first");
      return;
    }
    setShowReports(true);
    toast.success("Reports generated successfully!");
  };

  const timetables = timetablesData || [];
  const timetable = timetableData || {};
  const timetableSessions = timetable.timetable || {};

  // Process lecturer workload from timetable data
  const lecturerWorkload = useMemo(() => {
    if (!timetableSessions || Object.keys(timetableSessions).length === 0) {
      return {};
    }

    const workload = {};

    // Extract all sessions
    Object.values(timetableSessions).forEach((groupSessions) => {
      if (Array.isArray(groupSessions)) {
        groupSessions.forEach((session) => {
          const lecturerId = session.lecturer?.id || session.lecturer?.name || "Unknown";
          const lecturerName = session.lecturer?.name || lecturerId;
          const day = session.time_slot?.day;

          if (!day) return;

          if (!workload[lecturerId]) {
            workload[lecturerId] = {
              id: lecturerId,
              name: lecturerName,
              days: {
                MON: 0,
                TUE: 0,
                WED: 0,
                THU: 0,
                FRI: 0,
              },
              total: 0,
            };
          }

          if (workload[lecturerId].days[day] !== undefined) {
            workload[lecturerId].days[day]++;
            workload[lecturerId].total++;
          }
        });
      }
    });

    return workload;
  }, [timetableSessions]);

  // Process room utilization from timetable data
  const roomUtilization = useMemo(() => {
    if (!timetableSessions || Object.keys(timetableSessions).length === 0) {
      return {};
    }

    const utilization = {};

    // Extract all sessions
    Object.values(timetableSessions).forEach((groupSessions) => {
      if (Array.isArray(groupSessions)) {
        groupSessions.forEach((session) => {
          const roomId = session.room?.number || session.room?.id || "Unknown";
          const roomName = session.room?.number || roomId;
          const day = session.time_slot?.day;

          if (!day) return;

          if (!utilization[roomId]) {
            utilization[roomId] = {
              id: roomId,
              name: roomName,
              type: session.room?.type || "N/A",
              capacity: session.room?.capacity || 0,
              days: {
                MON: 0,
                TUE: 0,
                WED: 0,
                THU: 0,
                FRI: 0,
              },
              total: 0,
            };
          }

          if (utilization[roomId].days[day] !== undefined) {
            utilization[roomId].days[day]++;
            utilization[roomId].total++;
          }
        });
      }
    });

    return utilization;
  }, [timetableSessions]);

  // Extract unique lecturers and rooms for filters
  const uniqueLecturers = useMemo(() => {
    const lecturers = Object.values(lecturerWorkload).map((lec) => ({
      id: lec.id,
      name: lec.name,
    }));
    return lecturers.sort((a, b) => a.name.localeCompare(b.name));
  }, [lecturerWorkload]);

  const uniqueRooms = useMemo(() => {
    const rooms = Object.values(roomUtilization).map((room) => ({
      id: room.id,
      name: room.name,
    }));
    return rooms.sort((a, b) => a.name.localeCompare(b.name));
  }, [roomUtilization]);

  // Filter lecturer workload
  const filteredLecturerWorkload = useMemo(() => {
    if (filterLecturer === "all") {
      return Object.values(lecturerWorkload).sort((a, b) => b.total - a.total);
    }
    const filtered = lecturerWorkload[filterLecturer];
    return filtered ? [filtered] : [];
  }, [lecturerWorkload, filterLecturer]);

  // Filter room utilization
  const filteredRoomUtilization = useMemo(() => {
    if (filterRoom === "all") {
      return Object.values(roomUtilization).sort((a, b) => b.total - a.total);
    }
    const filtered = roomUtilization[filterRoom];
    return filtered ? [filtered] : [];
  }, [roomUtilization, filterRoom]);

  // Helper function to escape CSV values
  const escapeCsvValue = (value) => {
    const str = String(value);
    // If value contains comma, newline, or quote, wrap in quotes and escape quotes
    if (str.includes(",") || str.includes("\n") || str.includes('"')) {
      return `"${str.replace(/"/g, '""')}"`;
    }
    return str;
  };

  // Export to Excel function - exports only what's currently displayed
  const handleExportToExcel = () => {
    if (!showReports) {
      toast.error("Please generate reports first");
      return;
    }

    try {
      const term = timetable.term || "Term_N/A";
      const timestamp = new Date().toISOString().split("T")[0];
      const filename = `REPORTS_${term}_${timestamp}.csv`;

      // Create CSV content based on report type
      const csvRows = [];

      // Add Lecturer Workload Report (if applicable)
      if (reportType === "both" || reportType === "lecturers") {
        csvRows.push("LECTURER WORKLOAD REPORT");
        csvRows.push(`Timetable: ${term}`);
        csvRows.push(`Generated: ${new Date().toLocaleString()}`);
        if (filterLecturer !== "all") {
          csvRows.push(`Filter: ${filteredLecturerWorkload[0]?.name || filterLecturer}`);
        }
        csvRows.push("");
        
        const lecturerHeaders = ["Lecturer", ...DAYS.map((d) => DAY_NAMES[d]), "Total"];
        csvRows.push(lecturerHeaders.map(escapeCsvValue).join(","));

        filteredLecturerWorkload.forEach((lecturer) => {
          const row = [
            lecturer.name,
            ...DAYS.map((day) => lecturer.days[day] || 0),
            lecturer.total,
          ];
          csvRows.push(row.map(escapeCsvValue).join(","));
        });

        // Add totals row for lecturers
        const lecturerTotals = [
          "Total",
          ...DAYS.map((day) =>
            filteredLecturerWorkload.reduce(
              (sum, lec) => sum + (lec.days[day] || 0),
              0
            )
          ),
          filteredLecturerWorkload.reduce((sum, lec) => sum + lec.total, 0),
        ];
        csvRows.push(lecturerTotals.map(escapeCsvValue).join(","));
      }

      // Add separator if both reports
      if (reportType === "both") {
        csvRows.push("");
        csvRows.push("");
      }

      // Add Room Utilization Report (if applicable)
      if (reportType === "both" || reportType === "rooms") {
        csvRows.push("ROOM UTILIZATION REPORT");
        csvRows.push(`Timetable: ${term}`);
        csvRows.push(`Generated: ${new Date().toLocaleString()}`);
        if (filterRoom !== "all") {
          csvRows.push(`Filter: ${filteredRoomUtilization[0]?.name || filterRoom}`);
        }
        csvRows.push("");

        const roomHeaders = [
          "Room",
          "Type",
          "Capacity",
          ...DAYS.map((d) => DAY_NAMES[d]),
          "Total",
        ];
        csvRows.push(roomHeaders.map(escapeCsvValue).join(","));

        filteredRoomUtilization.forEach((room) => {
          const row = [
            room.name,
            room.type || "N/A",
            room.capacity || 0,
            ...DAYS.map((day) => room.days[day] || 0),
            room.total,
          ];
          csvRows.push(row.map(escapeCsvValue).join(","));
        });

        // Add totals row for rooms
        const roomTotals = [
          "Total",
          "",
          "",
          ...DAYS.map((day) =>
            filteredRoomUtilization.reduce(
              (sum, room) => sum + (room.days[day] || 0),
              0
            )
          ),
          filteredRoomUtilization.reduce((sum, room) => sum + room.total, 0),
        ];
        csvRows.push(roomTotals.map(escapeCsvValue).join(","));
      }

      // Create blob and download
      const csvContent = csvRows.join("\n");
      const blob = new Blob([csvContent], {
        type: "text/csv;charset=utf-8;",
      });
      const link = document.createElement("a");
      const url = URL.createObjectURL(blob);
      link.setAttribute("href", url);
      link.setAttribute("download", filename);
      link.style.visibility = "hidden";
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);

      toast.success("Reports exported to Excel successfully!");
    } catch (error) {
      toast.error(`Failed to export: ${error.message}`);
    }
  };

  const isLoading = timetablesLoading || timetableLoading;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Reports</h1>
          <p className="text-muted-foreground mt-1">
            View lecturer workload and room utilization reports
          </p>
        </div>
      </div>

      {/* Filters and Timetable Selection */}
      <Card className="glass-card p-6">
        <div className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {/* Timetable Selection */}
            <div className="space-y-2">
              <Label htmlFor="timetable">Select Timetable *</Label>
              <Select
                value={selectedTimetableId}
                onValueChange={setSelectedTimetableId}
              >
                <SelectTrigger>
                  <SelectValue placeholder="Select timetable" />
                </SelectTrigger>
                <SelectContent>
                  {timetables.map((tt) => (
                    <SelectItem key={tt._id} value={tt._id}>
                      {tt.term || "Term N/A"} - {tt.statistics?.total_sessions || 0} sessions
                      {tt.created_at && ` (${new Date(tt.created_at).toLocaleDateString()})`}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            {/* Report Type */}
            <div className="space-y-2">
              <Label htmlFor="report-type">Report Type</Label>
              <Select
                value={reportType}
                onValueChange={setReportType}
                disabled={!selectedTimetableId || isLoading}
              >
                <SelectTrigger>
                  <SelectValue placeholder="Select report type" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="both">Both Reports</SelectItem>
                  <SelectItem value="lecturers">Lecturers Only</SelectItem>
                  <SelectItem value="rooms">Rooms Only</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>

          {/* Generate Button */}
          <div className="flex items-center justify-between pt-2">
            <p className="text-xs text-muted-foreground">
              Select a timetable and report type, then click Generate to view reports
            </p>
            <Button
              onClick={handleGenerate}
              disabled={!selectedTimetableId || isLoading}
              className="gap-2"
            >
              <Play className="h-4 w-4" />
              Generate Reports
            </Button>
          </div>
        </div>
      </Card>

      {isLoading && selectedTimetableId ? (
        <Card className="glass-card p-8">
          <div className="flex items-center justify-center">
            <Loader2 className="h-6 w-6 animate-spin" />
            <span className="ml-2">Loading timetable data...</span>
          </div>
        </Card>
      ) : !selectedTimetableId ? (
        <Card className="glass-card p-8 text-center">
          <FileText className="h-12 w-12 mx-auto mb-4 text-muted-foreground" />
          <p className="text-muted-foreground">
            Please select a timetable to generate reports
          </p>
        </Card>
      ) : !showReports ? (
        <Card className="glass-card p-8 text-center">
          <FileText className="h-12 w-12 mx-auto mb-4 text-muted-foreground" />
          <p className="text-muted-foreground mb-4">
            Configure your filters and click "Generate Reports" to view the reports
          </p>
        </Card>
      ) : (
        <>
          {/* Export Button */}
          <div className="flex justify-end">
            <Button onClick={handleExportToExcel} className="gap-2">
              <Download className="h-4 w-4" />
              Export to Excel
            </Button>
          </div>

          {/* Lecturer Workload Report */}
          {(reportType === "both" || reportType === "lecturers") && (
            <Card className="glass-card p-6">
              <div className="flex items-center justify-between mb-6">
                <div className="flex items-center gap-2">
                  <Users className="h-5 w-5" />
                  <h2 className="text-2xl font-semibold">Lecturer Workload by Day</h2>
                </div>
                <div className="flex items-center gap-2">
                  <Label htmlFor="lecturer-filter" className="text-sm">Filter:</Label>
                  <Select
                    value={filterLecturer}
                    onValueChange={setFilterLecturer}
                  >
                    <SelectTrigger className="w-[200px]">
                      <SelectValue placeholder="All Lecturers" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="all">All Lecturers</SelectItem>
                      {uniqueLecturers.map((lecturer) => (
                        <SelectItem key={lecturer.id} value={lecturer.id}>
                          {lecturer.name}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
              </div>

            {filteredLecturerWorkload.length === 0 ? (
              <p className="text-muted-foreground text-center py-8">
                {filterLecturer !== "all"
                  ? "No data found for selected lecturer"
                  : "No lecturer data available for this timetable"}
              </p>
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full border-collapse">
                  <thead>
                    <tr className="border-b border-border">
                      <th className="text-left p-3 font-semibold">Lecturer</th>
                      {DAYS.map((day) => (
                        <th
                          key={day}
                          className="text-center p-3 font-semibold min-w-[100px]"
                        >
                          {DAY_NAMES[day]}
                        </th>
                      ))}
                      <th className="text-center p-3 font-semibold">Total</th>
                    </tr>
                  </thead>
                  <tbody>
                    {filteredLecturerWorkload.map((lecturer) => (
                      <tr
                        key={lecturer.id}
                        className="border-b border-border/50 hover:bg-muted/30"
                      >
                        <td className="p-3 font-medium">{lecturer.name}</td>
                        {DAYS.map((day) => (
                          <td key={day} className="text-center p-3">
                            {lecturer.days[day] > 0 ? (
                              <Badge variant="default" className="min-w-[40px]">
                                {lecturer.days[day]}
                              </Badge>
                            ) : (
                              <span className="text-muted-foreground">0</span>
                            )}
                          </td>
                        ))}
                        <td className="text-center p-3">
                          <Badge variant="secondary" className="min-w-[50px]">
                            {lecturer.total}
                          </Badge>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                  <tfoot>
                    <tr className="border-t-2 border-border font-semibold bg-muted/20">
                      <td className="p-3">Total</td>
                      {DAYS.map((day) => {
                        const dayTotal = filteredLecturerWorkload.reduce(
                          (sum, lecturer) => sum + (lecturer.days[day] || 0),
                          0
                        );
                        return (
                          <td key={day} className="text-center p-3">
                            {dayTotal}
                          </td>
                        );
                      })}
                      <td className="text-center p-3">
                        {filteredLecturerWorkload.reduce(
                          (sum, lecturer) => sum + lecturer.total,
                          0
                        )}
                      </td>
                    </tr>
                  </tfoot>
                </table>
              </div>
            )}
            </Card>
          )}

          {/* Room Utilization Report */}
          {(reportType === "both" || reportType === "rooms") && (
            <Card className="glass-card p-6">
              <div className="flex items-center justify-between mb-6">
                <div className="flex items-center gap-2">
                  <Home className="h-5 w-5" />
                  <h2 className="text-2xl font-semibold">Room Utilization by Day</h2>
                </div>
                <div className="flex items-center gap-2">
                  <Label htmlFor="room-filter" className="text-sm">Filter:</Label>
                  <Select
                    value={filterRoom}
                    onValueChange={setFilterRoom}
                  >
                    <SelectTrigger className="w-[200px]">
                      <SelectValue placeholder="All Rooms" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="all">All Rooms</SelectItem>
                      {uniqueRooms.map((room) => (
                        <SelectItem key={room.id} value={room.id}>
                          {room.name}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
              </div>

            {filteredRoomUtilization.length === 0 ? (
              <p className="text-muted-foreground text-center py-8">
                {filterRoom !== "all"
                  ? "No data found for selected room"
                  : "No room data available for this timetable"}
              </p>
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full border-collapse">
                  <thead>
                    <tr className="border-b border-border">
                      <th className="text-left p-3 font-semibold">Room</th>
                      <th className="text-left p-3 font-semibold">Type</th>
                      <th className="text-left p-3 font-semibold">Capacity</th>
                      {DAYS.map((day) => (
                        <th
                          key={day}
                          className="text-center p-3 font-semibold min-w-[100px]"
                        >
                          {DAY_NAMES[day]}
                        </th>
                      ))}
                      <th className="text-center p-3 font-semibold">Total</th>
                    </tr>
                  </thead>
                  <tbody>
                    {filteredRoomUtilization.map((room) => (
                      <tr
                        key={room.id}
                        className="border-b border-border/50 hover:bg-muted/30"
                      >
                        <td className="p-3 font-medium">{room.name}</td>
                        <td className="p-3">
                          <Badge variant="outline">{room.type}</Badge>
                        </td>
                        <td className="p-3">{room.capacity || "N/A"}</td>
                        {DAYS.map((day) => (
                          <td key={day} className="text-center p-3">
                            {room.days[day] > 0 ? (
                              <Badge variant="default" className="min-w-[40px]">
                                {room.days[day]}
                              </Badge>
                            ) : (
                              <span className="text-muted-foreground">0</span>
                            )}
                          </td>
                        ))}
                        <td className="text-center p-3">
                          <Badge variant="secondary" className="min-w-[50px]">
                            {room.total}
                          </Badge>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                  <tfoot>
                    <tr className="border-t-2 border-border font-semibold bg-muted/20">
                      <td className="p-3" colSpan="3">
                        Total
                      </td>
                      {DAYS.map((day) => {
                        const dayTotal = filteredRoomUtilization.reduce(
                          (sum, room) => sum + (room.days[day] || 0),
                          0
                        );
                        return (
                          <td key={day} className="text-center p-3">
                            {dayTotal}
                          </td>
                        );
                      })}
                      <td className="text-center p-3">
                        {filteredRoomUtilization.reduce(
                          (sum, room) => sum + room.total,
                          0
                        )}
                      </td>
                    </tr>
                  </tfoot>
                </table>
              </div>
            )}
            </Card>
          )}
        </>
      )}
    </div>
  );
}

