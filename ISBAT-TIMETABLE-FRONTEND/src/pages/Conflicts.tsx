import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { AlertTriangle, CheckCircle } from "lucide-react";
import StatCard from "@/components/StatCard";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";

export default function Conflicts() {
  const conflictStats = [
    { title: "Total Conflicts", value: 12, icon: AlertTriangle, description: "Require attention" },
    { title: "Resolved", value: 8, icon: CheckCircle, description: "This week" },
    { title: "Critical", value: 3, icon: AlertTriangle, description: "High priority" },
    { title: "Suggestions", value: 15, icon: CheckCircle, description: "Auto-fix available" },
  ];

  const conflicts = [
    {
      id: "1",
      type: "Room Capacity Exceeded",
      description: "BIT-S3 Networking class has 95 students but room holds 60",
      affected: "Group: BIT-S3",
      suggestedFix: "Split class into two groups",
      severity: "high",
      autoFix: true,
    },
    {
      id: "2",
      type: "Lecturer Double-Booked",
      description: "Dr. Sarah Johnson scheduled for two classes at Monday 10:00 AM",
      affected: "Dr. Sarah Johnson",
      suggestedFix: "Reschedule CS102 to Tuesday 10:00 AM",
      severity: "high",
      autoFix: true,
    },
    {
      id: "3",
      type: "Room Double-Booked",
      description: "Lab 405 assigned to two classes at same time",
      affected: "Room: Lab 405",
      suggestedFix: "Move BBA101 to Room 301",
      severity: "medium",
      autoFix: true,
    },
    {
      id: "4",
      type: "Lecturer Exceeding Hours",
      description: "Mr. David Brown assigned 22 hours but max is 18",
      affected: "Mr. David Brown",
      suggestedFix: "Reassign 2 classes to another lecturer",
      severity: "medium",
      autoFix: false,
    },
  ];

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case "high":
        return "destructive";
      case "medium":
        return "default";
      default:
        return "secondary";
    }
  };

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
            Review and resolve conflicts before publishing timetable
          </p>
        </div>
        <Table>
          <TableHeader>
            <TableRow>
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
                      <Button size="sm" variant="default">
                        Auto Fix
                      </Button>
                    )}
                    <Button size="sm" variant="outline">
                      Adjust
                    </Button>
                  </div>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </Card>
    </div>
  );
}
