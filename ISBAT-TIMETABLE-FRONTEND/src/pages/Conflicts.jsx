import { useMemo } from "react";
import { useQuery } from "@tanstack/react-query";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { AlertTriangle, CheckCircle, Loader2 } from "lucide-react";
import StatCard from "@/components/StatCard";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { timetableAPI } from "@/lib/api";
import { toast } from "sonner";

export default function Conflicts() {
  // Fetch all timetables to analyze for conflicts
  const { data, isLoading, error } = useQuery({
    queryKey: ["timetables"],
    queryFn: async () => {
      const response = await timetableAPI.list();
      return response.timetables || [];
    },
  });

  const timetables = data || [];

  // Get conflicts from verification results
  const conflicts = useMemo(() => {
    const detectedConflicts = [];
    let conflictId = 1;

    timetables.forEach((timetable) => {
      // Use verification results if available (from verify_timetable_constraints.py)
      if (timetable.verification && timetable.verification.violations) {
        timetable.verification.violations.forEach((violation) => {
          // Handle both dict and object formats
          const getValue = (key, defaultValue) => {
            if (typeof violation === 'object' && violation !== null) {
              return violation[key] || violation.get?.(key) || defaultValue;
            }
            return defaultValue;
          };
          
          detectedConflicts.push({
            id: conflictId++,
            type: getValue('constraint_type', getValue('type', 'Unknown Constraint')),
            description: getValue('message', getValue('description', 'No description')),
            affected: getValue('affected_resource', getValue('affected', 'Unknown')),
            suggestedFix: getValue('suggested_fix', getValue('suggestedFix', 'Review and adjust manually')),
            severity: (getValue('severity', 'medium') || 'medium').toLowerCase(),
            autoFix: false,
            timetable_id: timetable._id,
            term: timetable.term || 'N/A',
            details: violation,
          });
        });
      } else {
        // Fallback: Analyze from timetable data if no verification results
        const timetableData = timetable.timetable || {};
        const sessions = [];

        // Collect all sessions
        Object.entries(timetableData).forEach(([groupId, groupSessions]) => {
          groupSessions.forEach((session) => {
            sessions.push({
              ...session,
              student_group_id: groupId,
              timetable_id: timetable._id,
            });
          });
        });

        // Check for lecturer double-booking
        const lecturerSlots = {};
        sessions.forEach((session) => {
          if (session.lecturer?.id && session.time_slot) {
            const key = `${session.lecturer.id}_${session.time_slot.day}_${session.time_slot.period}`;
            if (!lecturerSlots[key]) {
              lecturerSlots[key] = [];
            }
            lecturerSlots[key].push(session);
          }
        });

        Object.entries(lecturerSlots).forEach(([key, slotSessions]) => {
          if (slotSessions.length > 1) {
            detectedConflicts.push({
              id: conflictId++,
              type: "Lecturer Double-Booked",
              description: `${slotSessions[0].lecturer?.name || "Unknown"} scheduled for ${slotSessions.length} classes at the same time`,
              affected: slotSessions[0].lecturer?.name || "Unknown Lecturer",
              suggestedFix: `Reschedule one of the classes to a different time slot`,
              severity: "high",
              autoFix: false,
              timetable_id: slotSessions[0].timetable_id,
              term: timetable.term || 'N/A',
            });
          }
        });

        // Check for room double-booking
        const roomSlots = {};
        sessions.forEach((session) => {
          if (session.room?.id && session.time_slot) {
            const key = `${session.room.id}_${session.time_slot.day}_${session.time_slot.period}`;
            if (!roomSlots[key]) {
              roomSlots[key] = [];
            }
            roomSlots[key].push(session);
          }
        });

        Object.entries(roomSlots).forEach(([key, slotSessions]) => {
          if (slotSessions.length > 1) {
            detectedConflicts.push({
              id: conflictId++,
              type: "Room Double-Booked",
              description: `Room ${slotSessions[0].room?.number || "Unknown"} assigned to ${slotSessions.length} classes at the same time`,
              affected: `Room: ${slotSessions[0].room?.number || "Unknown"}`,
              suggestedFix: `Move one of the classes to a different room`,
              severity: "high",
              autoFix: false,
              timetable_id: slotSessions[0].timetable_id,
              term: timetable.term || 'N/A',
            });
          }
        });
      }
    });

    return detectedConflicts;
  }, [timetables]);

  const conflictStats = [
    {
      title: "Total Conflicts",
      value: conflicts.length,
      icon: AlertTriangle,
      description: "Require attention",
    },
    {
      title: "Critical",
      value: conflicts.filter((c) => c.severity === "high").length,
      icon: AlertTriangle,
      description: "High priority",
    },
    {
      title: "Resolved",
      value: 0,
      icon: CheckCircle,
      description: "This week",
    },
    {
      title: "Timetables Analyzed",
      value: timetables.length,
      icon: CheckCircle,
      description: "Total timetables",
    },
  ];

  const getSeverityColor = (severity) => {
    switch (severity) {
      case "high":
        return "destructive";
      case "medium":
        return "default";
      default:
        return "secondary";
    }
  };

  const handleAutoFix = (conflict) => {
    toast.info("Auto-fix feature coming soon");
  };

  const handleAdjust = (conflict) => {
    toast.info("Manual adjustment feature coming soon");
  };

  if (isLoading) {
    return (
      <div className="space-y-6">
        <div className="flex items-center justify-center p-8">
          <Loader2 className="h-6 w-6 animate-spin" />
          <span className="ml-2">Analyzing conflicts...</span>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="space-y-6">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Conflict Center</h1>
          <p className="text-muted-foreground mt-1">
            Detect and resolve scheduling conflicts
          </p>
        </div>
        <Card className="glass-card p-8 text-center">
          <p className="text-destructive">Error loading timetables: {error.message}</p>
        </Card>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Conflict Center</h1>
        <p className="text-muted-foreground mt-1">
          Detect and resolve scheduling conflicts
        </p>
      </div>

      {/* Stats */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        {conflictStats.map((stat) => (
          <StatCard key={stat.title} {...stat} />
        ))}
      </div>

      {/* Conflicts Table */}
      <Card className="glass-card">
        <div className="p-6 border-b border-border">
          <h2 className="text-lg font-semibold">Active Conflicts</h2>
          <p className="text-sm text-muted-foreground mt-1">
            {conflicts.length === 0
              ? "No conflicts detected in current timetables"
              : "Review and resolve conflicts before publishing timetable"}
          </p>
        </div>
        {conflicts.length === 0 ? (
          <div className="p-8 text-center text-muted-foreground">
            <CheckCircle className="h-12 w-12 mx-auto mb-4 text-green-500" />
            <p>No conflicts detected! All timetables are conflict-free.</p>
          </div>
        ) : (
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Term</TableHead>
                <TableHead>Conflict Type</TableHead>
                <TableHead>Description</TableHead>
                <TableHead>Affected</TableHead>
                <TableHead>Suggested Fix</TableHead>
                <TableHead>Severity</TableHead>
                <TableHead className="text-right">Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {conflicts.map((conflict) => (
                <TableRow key={conflict.id}>
                  <TableCell>
                    <Badge variant="secondary">{conflict.term}</Badge>
                  </TableCell>
                  <TableCell className="font-medium">{conflict.type}</TableCell>
                  <TableCell className="max-w-xs">{conflict.description}</TableCell>
                  <TableCell>
                    <Badge variant="outline">{conflict.affected}</Badge>
                  </TableCell>
                  <TableCell className="max-w-xs text-sm text-muted-foreground">
                    {conflict.suggestedFix}
                  </TableCell>
                  <TableCell>
                    <Badge variant={getSeverityColor(conflict.severity)}>
                      {conflict.severity}
                    </Badge>
                  </TableCell>
                  <TableCell className="text-right">
                    <div className="flex gap-2 justify-end">
                      {conflict.autoFix && (
                        <Button
                          size="sm"
                          variant="default"
                          onClick={() => handleAutoFix(conflict)}
                        >
                          Auto Fix
                        </Button>
                      )}
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() => handleAdjust(conflict)}
                      >
                        Adjust
                      </Button>
                    </div>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        )}
      </Card>
    </div>
  );
}
