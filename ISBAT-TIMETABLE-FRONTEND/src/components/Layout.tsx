import { ReactNode, useState } from "react";
import { Link, useLocation } from "react-router-dom";
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
  X
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Sheet, SheetContent, SheetTrigger } from "@/components/ui/sheet";
import SemesterSwitcher from "@/components/SemesterSwitcher";
import { useSemester } from "@/context/SemesterContext";

interface LayoutProps {
  children: ReactNode;
}

const navigation = [
  { name: "Dashboard", href: "/", icon: LayoutDashboard },
  { name: "Lecturers", href: "/lecturers", icon: Users },
  { name: "Courses", href: "/courses", icon: BookOpen },
  { name: "Rooms", href: "/rooms", icon: HomeIcon },
  { name: "Timetables", href: "/timetables", icon: Calendar },
  { name: "Conflicts", href: "/conflicts", icon: AlertCircle },
];

const SidebarNav = ({ isMobile = false, onItemClick }: { isMobile?: boolean; onItemClick?: () => void }) => {
  const location = useLocation();

  return (
    <nav className="flex flex-col gap-1 p-4">
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
    </nav>
  );
};

export default function Layout({ children }: LayoutProps) {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const { current } = useSemester();

  return (
    <div className="min-h-screen flex w-full bg-background">
      {/* Desktop Sidebar */}
      <aside className="hidden lg:flex lg:w-64 lg:flex-col bg-primary border-r border-primary-hover">
        {/* Logo Section - White Background */}
        <div className="bg-white border-b border-primary-light p-6">
          <img
            src="/isbat-university-logo.png"
            alt="ISBAT University"
            className="max-w-full h-12 object-contain"
          />
        </div>
        
        {/* Navigation */}
        <SidebarNav />
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
          <SheetContent side="left" className="w-64 p-0 bg-primary border-primary-hover">
            {/* Logo in Mobile Menu */}
            <div className="bg-white border-b border-primary-light p-6">
              <img
                src="/isbat-university-logo.png"
                alt="ISBAT University"
                className="h-12 object-contain"
              />
            </div>
            <SidebarNav isMobile onItemClick={() => setMobileMenuOpen(false)} />
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
