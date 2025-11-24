import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Download, FileText, Calendar } from "lucide-react";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";

export default function Timetable() {
  const timeSlots = ["8:00 AM", "10:00 AM", "12:00 PM", "2:00 PM", "4:00 PM"];
  const days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"];

  const sampleClasses = [
    {
      day: "Monday",
      time: "8:00 AM",
      unit: "CS101",
      lecturer: "Dr. Sarah Johnson",
      room: "Lab 405",
      group: "BIT-S1",
    },
    {
      day: "Monday",
      time: "10:00 AM",
      unit: "CS102",
      lecturer: "Dr. Emily Chen",
      room: "Room 301",
      group: "BIT-S1",
    },
    {
      day: "Tuesday",
      time: "8:00 AM",
      unit: "BBA101",
      lecturer: "Mr. David Brown",
      room: "Hall A",
      group: "BBA-S1",
    },
  ];

  const getClassForSlot = (day: string, time: string) => {
    return sampleClasses.find((c) => c.day === day && c.time === time);
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Timetable</h1>
          <p className="text-muted-foreground mt-1">View and manage class schedules</p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" className="gap-2">
            <FileText className="h-4 w-4" />
            Export PDF
          </Button>
          <Button variant="outline" className="gap-2">
            <Download className="h-4 w-4" />
            Export Excel
          </Button>
        </div>
      </div>

      {/* Filters */}
      <Card className="glass-card p-4">
        <div className="flex flex-col sm:flex-row gap-4">
          <Select>
            <SelectTrigger className="w-full sm:w-64">
              <SelectValue placeholder="Select View Type" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="master">Master Timetable</SelectItem>
              <SelectItem value="lecturer">By Lecturer</SelectItem>
              <SelectItem value="group">By Student Group</SelectItem>
            </SelectContent>
          </Select>
          <Select>
            <SelectTrigger className="w-full sm:w-64">
              <SelectValue placeholder="Select Faculty" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All Faculties</SelectItem>
              <SelectItem value="cs">Computer Science</SelectItem>
              <SelectItem value="business">Business</SelectItem>
            </SelectContent>
          </Select>
          <Select>
            <SelectTrigger className="w-full sm:w-64">
              <SelectValue placeholder="Select Semester" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="s1">Semester 1</SelectItem>
              <SelectItem value="s2">Semester 2</SelectItem>
            </SelectContent>
          </Select>
        </div>
      </Card>

      {/* Timetable Grid */}
      <Card className="glass-card p-6 overflow-x-auto">
        <div className="min-w-[800px]">
          <div className="grid grid-cols-6 gap-2">
            {/* Header Row */}
            <div className="font-semibold text-sm text-muted-foreground p-3">Time</div>
            {days.map((day) => (
              <div
                key={day}
                className="font-semibold text-center p-3 bg-primary/5 rounded-lg"
              >
                {day}
              </div>
            ))}

            {/* Time Slots */}
            {timeSlots.map((time) => (
              <>
                <div
                  key={time}
                  className="font-medium text-sm text-muted-foreground p-3 flex items-center"
                >
                  {time}
                </div>
                {days.map((day) => {
                  const classInfo = getClassForSlot(day, time);
                  return (
                    <div
                      key={`${day}-${time}`}
                      className="min-h-[100px] p-2 border border-border rounded-lg hover:bg-accent/30 transition-colors"
                    >
                      {classInfo ? (
                        <div className="h-full p-2 bg-primary/10 border border-primary/20 rounded space-y-1">
                          <Badge className="text-xs font-semibold">
                            {classInfo.unit}
                          </Badge>
                          <p className="text-xs font-medium text-foreground">
                            {classInfo.lecturer}
                          </p>
                          <p className="text-xs text-muted-foreground">
                            {classInfo.room}
                          </p>
                          <p className="text-xs text-muted-foreground">
                            {classInfo.group}
                          </p>
                        </div>
                      ) : null}
                    </div>
                  );
                })}
              </>
            ))}
          </div>
        </div>
      </Card>

      {/* Legend */}
      <Card className="glass-card p-4">
        <div className="flex items-center gap-6">
          <span className="text-sm font-medium">Color Legend:</span>
          <div className="flex items-center gap-2">
            <div className="w-4 h-4 rounded bg-primary/10 border border-primary/20" />
            <span className="text-sm text-muted-foreground">Computer Science</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-4 h-4 rounded bg-accent border border-border" />
            <span className="text-sm text-muted-foreground">Business</span>
          </div>
        </div>
      </Card>
    </div>
  );
}
