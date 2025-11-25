import React, { useState, useMemo } from "react";
import { useQuery } from "@tanstack/react-query";
import { useSearchParams, useNavigate } from "react-router-dom";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Download, FileText, Calendar, Loader2, ArrowLeft } from "lucide-react";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { timetableAPI } from "@/lib/api";
import { toast } from "sonner";

// Time slots mapping based on backend
const TIME_SLOTS = [
  { period: "SLOT_1", start: "09:00", end: "11:00", display: "09:00 AM - 11:00 AM" },
  { period: "SLOT_2", start: "11:00", end: "13:00", display: "11:00 AM - 01:00 PM" },
  { period: "SLOT_3", start: "14:00", end: "16:00", display: "02:00 PM - 04:00 PM" },
  { period: "SLOT_4", start: "16:00", end: "18:00", display: "04:00 PM - 06:00 PM" },
];

const DAYS = ["MON", "TUE", "WED", "THU", "FRI"];
const DAY_NAMES = {
  MON: "Monday",
  TUE: "Tuesday",
  WED: "Wednesday",
  THU: "Thursday",
  FRI: "Friday",
};

// Color palette for course groups
const COURSE_GROUP_COLORS = [
  { bg: 'bg-blue-100 dark:bg-blue-900/30', border: 'border-blue-300 dark:border-blue-700', text: 'text-blue-800 dark:text-blue-200' },
  { bg: 'bg-green-100 dark:bg-green-900/30', border: 'border-green-300 dark:border-green-700', text: 'text-green-800 dark:text-green-200' },
  { bg: 'bg-purple-100 dark:bg-purple-900/30', border: 'border-purple-300 dark:border-purple-700', text: 'text-purple-800 dark:text-purple-200' },
  { bg: 'bg-orange-100 dark:bg-orange-900/30', border: 'border-orange-300 dark:border-orange-700', text: 'text-orange-800 dark:text-orange-200' },
  { bg: 'bg-pink-100 dark:bg-pink-900/30', border: 'border-pink-300 dark:border-pink-700', text: 'text-pink-800 dark:text-pink-200' },
  { bg: 'bg-cyan-100 dark:bg-cyan-900/30', border: 'border-cyan-300 dark:border-cyan-700', text: 'text-cyan-800 dark:text-cyan-200' },
  { bg: 'bg-yellow-100 dark:bg-yellow-900/30', border: 'border-yellow-300 dark:border-yellow-700', text: 'text-yellow-800 dark:text-yellow-800' },
  { bg: 'bg-indigo-100 dark:bg-indigo-900/30', border: 'border-indigo-300 dark:border-indigo-700', text: 'text-indigo-800 dark:text-indigo-200' },
];

// Get color for a course code (deterministic based on code)
const getCourseColor = (courseCode) => {
  if (!courseCode) return COURSE_GROUP_COLORS[0];
  // Use course code to deterministically assign color
  const hash = courseCode.split('').reduce((acc, char) => acc + char.charCodeAt(0), 0);
  return COURSE_GROUP_COLORS[hash % COURSE_GROUP_COLORS.length];
};

export default function Timetable() {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const timetableId = searchParams.get("id");
  
  // Filter states
  const [selectedCourse, setSelectedCourse] = useState("all");
  const [selectedProgram, setSelectedProgram] = useState("all");
  const [selectedSemester, setSelectedSemester] = useState("all");

  // Fetch timetable data
  const { data, isLoading, error } = useQuery({
    queryKey: ["timetable", timetableId],
    queryFn: async () => {
      if (!timetableId) {
        throw new Error("No timetable ID provided");
      }
      return await timetableAPI.getById(timetableId);
    },
    enabled: !!timetableId,
  });

  const timetable = data || {};
  const timetableData = timetable.timetable || {};
  
  // Debug: Log timetable data structure
  React.useEffect(() => {
    if (timetableData && Object.keys(timetableData).length > 0) {
      const firstGroup = Object.keys(timetableData)[0];
      const firstSession = timetableData[firstGroup]?.[0];
      console.log('Timetable data loaded:', {
        groups: Object.keys(timetableData).length,
        firstGroup,
        firstSession,
        timeSlot: firstSession?.time_slot,
        program: firstSession?.program,
        semester: firstSession?.semester
      });
    }
  }, [timetableData]);

  // Extract all unique values for filters
  const { courses, programs, semesters } = useMemo(() => {
    const courseMap = new Map(); // Map code to {code, name}
    const programSet = new Set();
    const semesterSet = new Set();

    Object.entries(timetableData).forEach(([groupId, groupSessions]) => {
      if (Array.isArray(groupSessions)) {
        groupSessions.forEach((session) => {
          if (session?.course_unit?.code) {
            courseMap.set(session.course_unit.code, {
              code: session.course_unit.code,
              name: session.course_unit.name || session.course_unit.code
            });
          }
          if (session?.program) {
            programSet.add(session.program);
          }
          if (session?.semester) {
            // Normalize semester format (ensure S1, S2, etc.)
            const sem = session.semester.toUpperCase();
            if (sem.startsWith('S')) {
              semesterSet.add(sem);
            } else {
              semesterSet.add(`S${sem}`);
            }
          }
        });
      }
    });

    // Debug: Log extracted values
    const extractedPrograms = Array.from(programSet);
    const extractedSemesters = Array.from(semesterSet);
    
    console.log('Extracted filters:', {
      courses: Array.from(courseMap.values()).length,
      programs: extractedPrograms,
      semesters: extractedSemesters,
      sampleSession: Object.values(timetableData)[0]?.[0]
    });

    return {
      courses: Array.from(courseMap.values()).sort((a, b) => a.code.localeCompare(b.code)),
      programs: extractedPrograms.length > 0 ? extractedPrograms.sort() : ['BIT', 'BCS'], // Fallback if empty
      semesters: extractedSemesters.length > 0 ? extractedSemesters.sort((a, b) => {
        // Sort S1, S2, S3... numerically
        const numA = parseInt(a.replace(/^S/i, ''));
        const numB = parseInt(b.replace(/^S/i, ''));
        return numA - numB;
      }) : ['S1', 'S2', 'S3', 'S4', 'S5', 'S6'], // Fallback if empty
    };
  }, [timetableData]);

  // Filter sessions based on selected filters
  const sessions = useMemo(() => {
    if (!timetableData) return [];

    const allSessions = [];
    Object.entries(timetableData).forEach(([groupId, groupSessions]) => {
      groupSessions.forEach((session) => {
        // Apply filters
        if (selectedCourse !== "all" && session.course_unit?.code !== selectedCourse) {
          return;
        }
        if (selectedProgram !== "all" && session.program !== selectedProgram) {
          return;
        }
        if (selectedSemester !== "all" && session.semester !== selectedSemester) {
          return;
        }

        allSessions.push({
          ...session,
          student_group_id: groupId,
        });
      });
    });

    return allSessions;
  }, [timetableData, selectedCourse, selectedProgram, selectedSemester]);

  // Organize sessions by day and time slot
  const organizedSessions = useMemo(() => {
    const organized = {};
    DAYS.forEach((day) => {
      organized[day] = {};
      TIME_SLOTS.forEach((slot) => {
        organized[day][slot.period] = [];
      });
    });

    sessions.forEach((session) => {
      const timeSlot = session.time_slot;
      if (timeSlot && timeSlot.day) {
        // Match period by checking start time
        let period = timeSlot.period;
        
        // If period is missing or doesn't match, find by start time
        if (!period || !organized[timeSlot.day] || !organized[timeSlot.day][period]) {
          if (timeSlot.start) {
            const matchingSlot = TIME_SLOTS.find(slot => slot.start === timeSlot.start);
            if (matchingSlot) {
              period = matchingSlot.period;
            }
          }
        }
        
        // Final check: if still no period, try to match by time range
        if (!period && timeSlot.start && timeSlot.end) {
          const timeRange = `${timeSlot.start}-${timeSlot.end}`;
          if (timeRange === '09:00-11:00') period = 'SLOT_1';
          else if (timeRange === '11:00-13:00') period = 'SLOT_2';
          else if (timeRange === '14:00-16:00') period = 'SLOT_3';
          else if (timeRange === '16:00-18:00') period = 'SLOT_4';
        }
        
        if (period && organized[timeSlot.day] && organized[timeSlot.day][period]) {
          organized[timeSlot.day][period].push(session);
        } else {
          // Debug: log unmatched sessions
          console.warn('Session not matched:', {
            day: timeSlot.day,
            period: timeSlot.period,
            start: timeSlot.start,
            end: timeSlot.end,
            course: session.course_unit?.code
          });
        }
      }
    });

    return organized;
  }, [sessions]);

  const getClassForSlot = (day, period) => {
    return organizedSessions[day]?.[period] || [];
  };

  const handleExport = async (format) => {
    if (format === "Excel") {
      try {
        // Create CSV content matching the exact format from generate_term_timetable.py
        const headers = [
          "Session_ID", "Day", "Time_Slot", "Start_Time", "End_Time",
          "Course_Code", "Course_Name", "Course_Type", "Credits",
          "Lecturer_ID", "Lecturer_Name", "Lecturer_Role",
          "Room_Number", "Room_Type", "Room_Capacity", "Room_Campus",
          "Student_Group", "Semester", "Term", "Group_Size"
        ];
        
        const rows = sessions.map(session => [
          session.session_id || '',
          session.time_slot?.day || '',
          session.time_slot?.time_slot || `${session.time_slot?.start || ''}-${session.time_slot?.end || ''}`,
          session.time_slot?.start || '',
          session.time_slot?.end || '',
          session.course_unit?.code || '',
          session.course_unit?.name || '',
          session.course_unit?.preferred_room_type || '',
          session.course_unit?.credits || 0,
          session.lecturer?.id || '',
          session.lecturer?.name || '',
          session.lecturer?.role || '',
          session.room?.number || '',
          session.room?.type || '',
          session.room?.capacity || 0,
          session.room?.campus || 'N/A',
          session.student_group_name || session.student_group_id || '',
          session.semester || '',
          session.term || '',
          session.group_size || 0
        ]);
        
        // Convert to CSV (no quotes around values, matching Python script output)
        const csvContent = [
          headers.join(','),
          ...rows.map(row => row.map(cell => {
            const cellStr = String(cell);
            // Only quote if contains comma, newline, or quote
            if (cellStr.includes(',') || cellStr.includes('\n') || cellStr.includes('"')) {
              return `"${cellStr.replace(/"/g, '""')}"`;
            }
            return cellStr;
          }).join(','))
        ].join('\n');
        
        // Create blob and download
        const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
        const link = document.createElement('a');
        const url = URL.createObjectURL(blob);
        link.setAttribute('href', url);
        const termName = timetable.term || 'export';
        link.setAttribute('download', `TIMETABLE_${termName.toUpperCase().replace(' ', '_')}_COMPLETE.csv`);
        link.style.visibility = 'hidden';
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        
        toast.success("Timetable exported to Excel (CSV) successfully!");
      } catch (error) {
        toast.error(`Failed to export: ${error.message}`);
      }
    } else {
      toast.info(`Export to ${format} feature coming soon`);
    }
  };

  if (!timetableId) {
    return (
      <div className="space-y-6">
        <div className="flex items-center gap-4">
          <Button variant="outline" onClick={() => navigate("/timetables")}>
            <ArrowLeft className="h-4 w-4 mr-2" />
            Back to Timetables
          </Button>
        </div>
        <Card className="glass-card p-8 text-center">
          <p className="text-muted-foreground">No timetable selected. Please select a timetable from the list.</p>
        </Card>
      </div>
    );
  }

  if (isLoading) {
    return (
      <div className="space-y-6">
        <div className="flex items-center justify-center p-8">
          <Loader2 className="h-6 w-6 animate-spin" />
          <span className="ml-2">Loading timetable...</span>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="space-y-6">
        <div className="flex items-center gap-4">
          <Button variant="outline" onClick={() => navigate("/timetables")}>
            <ArrowLeft className="h-4 w-4 mr-2" />
            Back to Timetables
          </Button>
        </div>
        <Card className="glass-card p-8 text-center">
          <p className="text-destructive">Error loading timetable: {error.message}</p>
        </Card>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <Button variant="outline" onClick={() => navigate("/timetables")}>
            <ArrowLeft className="h-4 w-4 mr-2" />
            Back
          </Button>
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Timetable</h1>
            <p className="text-muted-foreground mt-1">
              {timetable.term || 'Term N/A'} • {sessions.length} sessions displayed
            </p>
          </div>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" className="gap-2" onClick={() => handleExport("PDF")}>
            <FileText className="h-4 w-4" />
            Export PDF
          </Button>
          <Button variant="outline" className="gap-2" onClick={() => handleExport("Excel")}>
            <Download className="h-4 w-4" />
            Export Excel
          </Button>
        </div>
      </div>

      {/* Info Card */}
      {timetable.statistics && (
        <Card className="glass-card p-4">
          <div className="flex items-center gap-6 flex-wrap">
            <div>
              <span className="text-sm text-muted-foreground">Total Sessions: </span>
              <span className="font-semibold">{timetable.statistics.total_sessions || 0}</span>
            </div>
            {timetable.optimized && (
              <Badge variant="default">Optimized with GGA</Badge>
            )}
            {timetable.verification && (
              <div>
                <span className="text-sm text-muted-foreground">Conflicts: </span>
                <Badge variant={timetable.verification.total_violations === 0 ? "default" : "destructive"}>
                  {timetable.verification.total_violations || 0}
                </Badge>
              </div>
            )}
            {timetable.created_at && (
              <div>
                <span className="text-sm text-muted-foreground">Generated: </span>
                <span className="font-semibold">
                  {new Date(timetable.created_at).toLocaleString()}
                </span>
              </div>
            )}
          </div>
        </Card>
      )}

      {/* Filters */}
      <Card className="glass-card p-4">
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
          <div className="space-y-2">
            <label className="text-sm font-medium">Course Unit</label>
            <Select value={selectedCourse} onValueChange={setSelectedCourse}>
              <SelectTrigger>
                <SelectValue placeholder="All Courses" />
            </SelectTrigger>
            <SelectContent>
                <SelectItem value="all">All Courses</SelectItem>
                {courses.map((course) => (
                  <SelectItem key={course.code} value={course.code}>
                    {course.code} - {course.name}
                  </SelectItem>
                ))}
            </SelectContent>
          </Select>
          </div>
          <div className="space-y-2">
            <label className="text-sm font-medium">Program</label>
            <Select value={selectedProgram} onValueChange={setSelectedProgram}>
              <SelectTrigger>
                <SelectValue placeholder="All Programs" />
            </SelectTrigger>
            <SelectContent>
                <SelectItem value="all">All Programs</SelectItem>
                {programs.map((program) => (
                  <SelectItem key={program} value={program}>
                    {program}
                  </SelectItem>
                ))}
            </SelectContent>
          </Select>
          </div>
          <div className="space-y-2">
            <label className="text-sm font-medium">Semester</label>
            <Select value={selectedSemester} onValueChange={setSelectedSemester}>
              <SelectTrigger>
                <SelectValue placeholder="All Semesters" />
            </SelectTrigger>
            <SelectContent>
                <SelectItem value="all">All Semesters</SelectItem>
                {semesters.map((semester) => (
                  <SelectItem key={semester} value={semester}>
                    {semester}
                  </SelectItem>
                ))}
            </SelectContent>
          </Select>
          </div>
        </div>
      </Card>


      {/* Timetable Grid */}
      <Card className="glass-card p-6 overflow-x-auto">
        <div className="min-w-[1000px]">
          <div className="grid grid-cols-6 gap-2">
            {/* Header Row */}
            <div className="font-semibold text-sm text-muted-foreground p-3">Time</div>
            {DAYS.map((day) => (
              <div
                key={day}
                className="font-semibold text-center p-3 bg-primary/5 rounded-lg"
              >
                {DAY_NAMES[day]}
              </div>
            ))}

            {/* Time Slots */}
            {TIME_SLOTS.map((slot) => (
              <React.Fragment key={slot.period}>
                <div
                  className="font-medium text-sm text-muted-foreground p-3 flex items-center"
                >
                  {slot.display}
                </div>
                {DAYS.map((day) => {
                  const slotSessions = getClassForSlot(day, slot.period);
                  return (
                    <div
                      key={`${day}-${slot.period}`}
                      className="min-h-[120px] p-2 border border-border rounded-lg hover:bg-accent/30 transition-colors"
                    >
                      {slotSessions.length > 0 ? (
                        <div className="space-y-2">
                          {slotSessions.map((session, idx) => {
                            const courseCode = session.course_unit?.code || "N/A";
                            const colorScheme = getCourseColor(courseCode);
                            const sessionKey = session.session_id || `${session.course_unit?.id || 'unknown'}-${session.student_group_id || 'unknown'}-${day}-${slot.period}-${idx}`;
                  return (
                    <div
                                key={sessionKey}
                                className={`h-full p-2 ${colorScheme.bg} ${colorScheme.border} border-2 rounded space-y-1 transition-all hover:shadow-md`}
                              >
                                <Badge className={`text-xs font-semibold ${colorScheme.text} bg-transparent border ${colorScheme.border}`}>
                                  {courseCode}
                          </Badge>
                                <p className={`text-xs font-medium ${colorScheme.text}`}>
                                  {session.course_unit?.name || "Unknown Course"}
                                </p>
                                <p className={`text-xs ${colorScheme.text} opacity-80`}>
                                  {session.lecturer?.name || "TBA"}
                                </p>
                                <p className={`text-xs ${colorScheme.text} opacity-80`}>
                                  {session.room?.number || "TBA"}
                                </p>
                                <div className="flex gap-1 flex-wrap">
                                  {session.program && (
                                    <Badge variant="outline" className="text-xs">
                                      {session.program}
                                    </Badge>
                                  )}
                                  {session.semester && (
                                    <Badge variant="outline" className="text-xs">
                                      {session.semester}
                                    </Badge>
                                  )}
                                </div>
                              </div>
                            );
                          })}
                        </div>
                      ) : null}
                    </div>
                  );
                })}
              </React.Fragment>
            ))}
          </div>
        </div>
      </Card>

      {/* Legend */}
      <Card className="glass-card p-4">
        <div className="space-y-3">
          <span className="text-sm font-medium">Course Color Legend:</span>
          <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-3">
            {courses.map((course) => {
              const colorScheme = getCourseColor(course.code);
              return (
                <div key={course.code} className="flex items-center gap-2">
                  <div className={`w-4 h-4 rounded border-2 ${colorScheme.border} ${colorScheme.bg}`} />
                  <div className="flex flex-col">
                    <span className="text-xs font-semibold">{course.code}</span>
                    <span className="text-xs text-muted-foreground truncate max-w-[120px]" title={course.name}>
                      {course.name}
                    </span>
                  </div>
                </div>
              );
            })}
          </div>
          {courses.length === 0 && (
            <p className="text-xs text-muted-foreground">
              No courses to display. Generate a timetable to see course color codes.
            </p>
          )}
        </div>
      </Card>
    </div>
  );
}
