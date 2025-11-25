import { useQuery } from "@tanstack/react-query";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import StatCard from "@/components/StatCard";
import { Users, BookOpen, Home, Calendar, Plus, RefreshCw, Loader2, GraduationCap } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { useNavigate } from "react-router-dom";
import { lecturersAPI, coursesAPI, roomsAPI, timetableAPI, studentsAPI } from "@/lib/api";

export default function Dashboard() {
  const navigate = useNavigate();

  // Fetch statistics from backend
  const { data: lecturersData, isLoading: lecturersLoading } = useQuery({
    queryKey: ['lecturers'],
    queryFn: async () => {
      const response = await lecturersAPI.getAll();
      return response.lecturers || [];
    },
  });

  const { data: coursesData, isLoading: coursesLoading } = useQuery({
    queryKey: ['courses'],
    queryFn: async () => {
      const response = await coursesAPI.getAll();
      return response.courses || [];
    },
  });

  const { data: roomsData, isLoading: roomsLoading } = useQuery({
    queryKey: ['rooms'],
    queryFn: async () => {
      const response = await roomsAPI.getAll();
      return response.rooms || [];
    },
  });

  const { data: timetablesData, isLoading: timetablesLoading } = useQuery({
    queryKey: ['timetables'],
    queryFn: async () => {
      const response = await timetableAPI.list();
      return response.timetables || [];
    },
  });

  const { data: studentGroupsData, isLoading: studentGroupsLoading } = useQuery({
    queryKey: ['student-groups'],
    queryFn: async () => {
      const response = await studentsAPI.getAll();
      return response.student_groups || [];
    },
  });

  const lecturers = lecturersData || [];
  const courses = coursesData || [];
  const rooms = roomsData || [];
  const timetables = timetablesData || [];
  const studentGroups = studentGroupsData || [];

  const latestTimetable = timetables.length > 0 ? timetables[0] : null;
  const hasGeneratedTimetable = timetables.length > 0;

  const stats = [
    {
      title: "Total Lecturers",
      value: lecturers.length,
      icon: Users,
      description: "Active faculty members",
      trend: { value: `${lecturers.length} total`, isPositive: true },
    },
    {
      title: "Total Courses",
      value: courses.length,
      icon: BookOpen,
      description: "Course units available",
      trend: { value: `${courses.length} units`, isPositive: true },
    },
    {
      title: "Total Rooms",
      value: rooms.length,
      icon: Home,
      description: "Available for scheduling",
      trend: { value: `${rooms.filter(r => r.is_available).length} available`, isPositive: true },
    },
    {
      title: "Student Groups",
      value: studentGroups.length,
      icon: GraduationCap,
      description: "Student cohorts defined",
      trend: { value: `${studentGroups.filter(sg => sg.is_active).length} active`, isPositive: studentGroups.length > 0 },
    },
    {
      title: "Timetables",
      value: timetables.length,
      icon: Calendar,
      description: hasGeneratedTimetable ? "Generated timetables" : "Ready to generate",
      trend: { value: hasGeneratedTimetable ? "Latest generated" : "Not generated", isPositive: hasGeneratedTimetable },
    },
  ];

  const quickActions = [
    { label: "Add Lecturer", icon: Users, variant: "default", to: "/lecturers" },
    { label: "Add Course", icon: BookOpen, variant: "default", to: "/courses" },
    { label: "Add Room", icon: Home, variant: "default", to: "/rooms" },
    { label: "Student Groups", icon: Users, variant: "default", to: "/student-groups" },
    { label: "Generate Timetable", icon: RefreshCw, variant: "default", to: "/timetables" },
  ];

  const isLoading = lecturersLoading || coursesLoading || roomsLoading || timetablesLoading || studentGroupsLoading;

  return (
    <div className="space-y-8">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold tracking-tight text-foreground">Dashboard</h1>
        <p className="text-muted-foreground mt-1">
          Welcome to ISBAT University Timetable Management System
        </p>
      </div>

      {/* Stats Grid */}
      {isLoading ? (
        <div className="flex items-center justify-center p-8">
          <Loader2 className="h-6 w-6 animate-spin" />
          <span className="ml-2">Loading statistics...</span>
        </div>
      ) : (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-5">
          {stats.map((stat) => (
            <StatCard key={stat.title} {...stat} />
          ))}
        </div>
      )}

      {/* Quick Actions */}
      <Card className="glass-card p-6">
        <h2 className="text-lg font-semibold mb-4">Quick Actions</h2>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
          {quickActions.map((action) => (
            <Button
              key={action.label}
              variant={action.variant}
              className="h-auto flex-col gap-2 py-4"
              onClick={() => navigate(action.to)}
            >
              <action.icon className="h-5 w-5" />
              <span className="text-xs">{action.label}</span>
            </Button>
          ))}
        </div>
      </Card>

      <div className="grid gap-6 md:grid-cols-2">
        {/* Recent Timetables */}
        <Card className="glass-card p-6">
          <h2 className="text-lg font-semibold mb-4">Recent Timetables</h2>
          {isLoading ? (
            <div className="flex items-center justify-center p-4">
              <Loader2 className="h-4 w-4 animate-spin" />
            </div>
          ) : timetables.length === 0 ? (
            <div className="text-sm text-muted-foreground">
              No timetables generated yet. Click "Generate Timetable" to create one.
            </div>
          ) : (
            <div className="space-y-4">
              {timetables.slice(0, 5).map((tt) => (
                <div key={tt._id} className="flex gap-3">
                  <div className="w-2 h-2 rounded-full bg-primary mt-2" />
                  <div className="flex-1 space-y-1">
                    <p className="text-sm font-medium">
                      {tt.program} - {tt.batch}
                    </p>
                    <p className="text-xs text-muted-foreground">
                      Semesters: {tt.semesters?.join(", ") || "—"}
                    </p>
                    <p className="text-xs text-muted-foreground">
                      {new Date(tt.created_at).toLocaleString()}
                    </p>
                  </div>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => navigate(`/timetable?id=${tt._id}`)}
                  >
                    View
                  </Button>
                </div>
              ))}
            </div>
          )}
        </Card>

        {/* System Status */}
        <Card className="glass-card p-6">
          <h2 className="text-lg font-semibold mb-4">System Status</h2>
          <div className="space-y-3">
            <div className="flex items-start gap-3 p-3 rounded-lg bg-muted/50">
              <div className="flex-1">
                <p className="text-sm font-medium">Data Readiness</p>
                <p className="text-xs text-muted-foreground mt-1">
                  {lecturers.length > 0 && courses.length > 0 && rooms.length > 0
                    ? "All systems ready for timetable generation"
                    : "Please add lecturers, courses, and rooms"}
                </p>
              </div>
              <Badge
                variant={
                  lecturers.length > 0 && courses.length > 0 && rooms.length > 0
                    ? "default"
                    : "secondary"
                }
                className="text-xs"
              >
                {lecturers.length > 0 && courses.length > 0 && rooms.length > 0
                  ? "Ready"
                  : "Setup Required"}
              </Badge>
            </div>
            <div className="flex items-start gap-3 p-3 rounded-lg bg-muted/50">
              <div className="flex-1">
                <p className="text-sm font-medium">Latest Timetable</p>
                <p className="text-xs text-muted-foreground mt-1">
                  {latestTimetable
                    ? `${latestTimetable.program} - ${latestTimetable.batch}`
                    : "No timetable generated yet"}
                </p>
              </div>
              <Badge
                variant={latestTimetable ? "default" : "secondary"}
                className="text-xs"
              >
                {latestTimetable ? "Active" : "None"}
              </Badge>
            </div>
          </div>
        </Card>
      </div>

      {/* Latest Timetable Preview */}
      {latestTimetable && (
        <Card className="glass-card p-6">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-semibold">Latest Timetable Preview</h2>
            <Button
              variant="outline"
              size="sm"
              onClick={() => navigate(`/timetable?id=${latestTimetable._id}`)}
            >
              <Calendar className="h-4 w-4 mr-2" />
              View Full Timetable
            </Button>
          </div>
          <div className="text-sm text-muted-foreground">
            <p>
              <strong>Program:</strong> {latestTimetable.program} |{" "}
              <strong>Batch:</strong> {latestTimetable.batch}
            </p>
            <p className="mt-1">
              <strong>Semesters:</strong> {latestTimetable.semesters?.join(", ") || "—"}
            </p>
            {latestTimetable.statistics && (
              <p className="mt-1">
                <strong>Total Sessions:</strong> {latestTimetable.statistics.total_sessions || 0}
                {latestTimetable.optimized && " (Optimized)"}
              </p>
            )}
          </div>
        </Card>
      )}
    </div>
  );
}
