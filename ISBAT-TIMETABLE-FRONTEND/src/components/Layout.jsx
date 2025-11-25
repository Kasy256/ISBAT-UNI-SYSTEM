import { useState } from "react";
import { Link, useLocation, useNavigate } from "react-router-dom";
import { cn } from "@/lib/utils";
import { 
  LayoutDashboard, 
  Users, 
  BookOpen, 
  Home as HomeIcon, 
  Calendar,
  GraduationCap,
  AlertCircle,
  Menu,
  X,
  Layers,
  LogOut
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Sheet, SheetContent, SheetTrigger } from "@/components/ui/sheet";
import SemesterSwitcher from "@/components/SemesterSwitcher";
import { useSemester } from "@/context/SemesterContext";
import { authAPI } from "@/lib/api";
import { toast } from "sonner";

const navigation = [
  { name: "Dashboard", href: "/", icon: LayoutDashboard },
  { name: "Lecturers", href: "/lecturers", icon: Users },
  { name: "Courses", href: "/courses", icon: BookOpen },
  { name: "Rooms", href: "/rooms", icon: HomeIcon },
  { name: "Student Groups", href: "/student-groups", icon: GraduationCap },
  { name: "Course Groups", href: "/canonical-groups", icon: Layers },
  { name: "Timetables", href: "/timetables", icon: Calendar },
  { name: "Conflicts", href: "/conflicts", icon: AlertCircle },
];

const SidebarNav = ({ isMobile = false, onItemClick }) => {
  const location = useLocation();
  const navigate = useNavigate();

  const handleLogout = () => {
    authAPI.logout();
    toast.success("Logged out successfully");
    navigate("/login");
    if (onItemClick) onItemClick();
  };

  return (
    <nav className="flex flex-col gap-1 p-4 h-full">
      <div className="flex-1">
        {navigation.map((item) => {
          const isActive = location.pathname === item.href;
          return (
            <Link
              key={item.name}
              to={item.href}
              onClick={onItemClick}
              className={cn(
                "flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition-all",
                isActive
                  ? "bg-white/20 text-white shadow-sm backdrop-blur-sm"
                  : "text-white/80 hover:bg-white/10 hover:text-white"
              )}
            >
              <item.icon className="h-5 w-5" />
              {item.name}
            </Link>
          );
        })}
      </div>
      {/* Logout Button */}
      <div className="mt-auto pt-2 border-t border-white/20">
        <Button
          variant="ghost"
          onClick={handleLogout}
          className={cn(
            "w-full justify-start gap-3 text-white/80 hover:bg-white/10 hover:text-white"
          )}
        >
          <LogOut className="h-5 w-5" />
          Logout
        </Button>
      </div>
    </nav>
  );
};

export default function Layout({ children }) {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const { current } = useSemester();

  return (
    <div className="min-h-screen flex w-full bg-background">
      {/* Desktop Sidebar */}
      <aside className="hidden lg:flex lg:w-64 lg:flex-col bg-primary border-r border-primary-hover h-screen">
        {/* Logo Section - White Background */}
        <div className="bg-white border-b border-primary-light p-6 flex-shrink-0">
          <img
            src="/isbat-university-logo.png"
            alt="ISBAT University"
            className="max-w-full h-12 object-contain"
          />
        </div>
        
        {/* Navigation */}
        <div className="flex-1 overflow-y-auto">
          <SidebarNav />
        </div>
      </aside>

      {/* Mobile/Tablet Header & Sidebar */}
      <div className="lg:hidden fixed top-0 left-0 right-0 z-50 bg-white border-b border-border/40 h-16 flex items-center justify-between px-4">
        <img src="/isbat-university-logo.png" alt="ISBAT University" className="h-10 object-contain" />

        <Sheet open={mobileMenuOpen} onOpenChange={setMobileMenuOpen}>
          <SheetTrigger asChild>
            <Button variant="ghost" size="icon" className="lg:hidden">
              <Menu className="h-6 w-6" />
            </Button>
          </SheetTrigger>
          <SheetContent side="left" className="w-64 p-0 bg-primary border-primary-hover flex flex-col h-full">
            {/* Logo in Mobile Menu */}
            <div className="bg-white border-b border-primary-light p-6 flex-shrink-0">
              <img
                src="/isbat-university-logo.png"
                alt="ISBAT University"
                className="h-12 object-contain"
              />
            </div>
            <div className="flex-1 overflow-y-auto">
              <SidebarNav isMobile onItemClick={() => setMobileMenuOpen(false)} />
            </div>
          </SheetContent>
        </Sheet>
      </div>

      {/* Main Content */}
      <main className="flex-1 overflow-y-auto lg:ml-0 pt-16 lg:pt-0">
        {/* Desktop top bar */}
        <div className="hidden lg:block border-b border-border bg-white/60 backdrop-blur supports-[backdrop-filter]:bg-white/40">
          <div className="container px-6 py-3 flex items-center justify-between">
            <SemesterSwitcher />
            <div className="text-xs text-muted-foreground">{current.label}</div>
          </div>
        </div>
        <div className="container py-4 px-4 sm:py-6 sm:px-6 lg:px-8 max-w-full">
          {children}
        </div>
      </main>
    </div>
  );
}

