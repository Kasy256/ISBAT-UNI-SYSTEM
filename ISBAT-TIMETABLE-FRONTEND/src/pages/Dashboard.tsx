import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import StatCard from "@/components/StatCard";
import { Users, BookOpen, Home, Calendar, Plus, RefreshCw } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { useNavigate } from "react-router-dom";

export default function Dashboard() {
  const navigate = useNavigate();
  const stats = [
    {
      title: "Total Lecturers",
      value: 48,
      icon: Users,
      description: "Active faculty members",
      trend: { value: "+4 this month", isPositive: true },
    },
    {
      title: "Total Courses",
      value: 24,
      icon: BookOpen,
      description: "Across all faculties",
      trend: { value: "+2 this semester", isPositive: true },
    },
    {
      title: "Total Rooms",
      value: 32,
      icon: Home,
      description: "Available for scheduling",
    },
    {
      title: "Schedule Status",
      value: "Not Generated",
      icon: Calendar,
      description: "Ready to generate",
    },
  ];

  const quickActions = [
    { label: "Add Lecturer", icon: Users, variant: "default" as const, to: "/lecturers" },
    { label: "Add Course", icon: BookOpen, variant: "default" as const, to: "/courses" },
    { label: "Add Room", icon: Home, variant: "default" as const, to: "/rooms" },
    { label: "Generate Timetable", icon: RefreshCw, variant: "default" as const, to: "/timetables" },
  ];

  const recentActivity = [
    { action: "Lecturer Added", detail: "Dr. John Smith - Computer Science", time: "2 hours ago" },
    { action: "Course Updated", detail: "Data Structures - Increased hours to 4/week", time: "5 hours ago" },
    { action: "Room Added", detail: "Lab 405 - Capacity 40", time: "1 day ago" },
    { action: "Timetable Generated", detail: "Semester 1 - 2024", time: "3 days ago" },
  ];

  const pendingTasks = [
    { task: "Add specializations for 5 lecturers", priority: "high" },
    { task: "Verify room capacities for Labs", priority: "medium" },
    { task: "Update student counts for BIT courses", priority: "medium" },
  ];

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
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        {stats.map((stat) => (
          <StatCard key={stat.title} {...stat} />
        ))}
      </div>

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
        {/* Recent Activity */}
        <Card className="glass-card p-6">
          <h2 className="text-lg font-semibold mb-4">Recent Activity</h2>
          <div className="space-y-4">
            {recentActivity.map((activity, index) => (
              <div key={index} className="flex gap-3">
                <div className="w-2 h-2 rounded-full bg-primary mt-2" />
                <div className="flex-1 space-y-1">
                  <p className="text-sm font-medium">{activity.action}</p>
                  <p className="text-xs text-muted-foreground">{activity.detail}</p>
                  <p className="text-xs text-muted-foreground">{activity.time}</p>
                </div>
              </div>
            ))}
          </div>
        </Card>

        {/* Pending Tasks */}
        <Card className="glass-card p-6">
          <h2 className="text-lg font-semibold mb-4">Pending Tasks</h2>
          <div className="space-y-3">
            {pendingTasks.map((task, index) => (
              <div key={index} className="flex items-start gap-3 p-3 rounded-lg bg-muted/50">
                <div className="flex-1">
                  <p className="text-sm font-medium">{task.task}</p>
                </div>
                <Badge
                  variant={task.priority === "high" ? "destructive" : "secondary"}
                  className="text-xs"
                >
                  {task.priority}
                </Badge>
              </div>
            ))}
          </div>
        </Card>
      </div>

      {/* Mini Weekly Preview */}
      <Card className="glass-card p-6">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-semibold">Weekly Timetable Preview</h2>
          <Button variant="outline" size="sm">
            <Calendar className="h-4 w-4 mr-2" />
            View Full Timetable
          </Button>
        </div>
        <div className="grid grid-cols-5 gap-2 text-center text-xs">
          {["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"].map((day) => (
            <div key={day} className="p-4 rounded-lg bg-muted/30">
              <p className="font-semibold mb-2">{day}</p>
              <div className="space-y-1">
                <div className="bg-primary/20 text-primary rounded px-2 py-1">
                  8:00 AM
                </div>
                <div className="bg-accent text-accent-foreground rounded px-2 py-1">
                  10:00 AM
                </div>
              </div>
            </div>
          ))}
        </div>
      </Card>
    </div>
  );
}
