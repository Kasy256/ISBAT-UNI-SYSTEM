import { Toaster } from "@/components/ui/toaster";
import { Toaster as Sonner } from "@/components/ui/sonner";
import { TooltipProvider } from "@/components/ui/tooltip";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import Layout from "./components/Layout";
import Dashboard from "./pages/Dashboard";
import Lecturers from "./pages/Lecturers";
import Subjects from "./pages/Subjects";
import Rooms from "./pages/Rooms";
import Timetable from "./pages/Timetable";
import Conflicts from "./pages/Conflicts";
import NotFound from "./pages/NotFound";
import Timetables from "./pages/Timetables";
import Programs from "./pages/Programs";
import CanonicalGroups from "./pages/CanonicalGroups";
import RoomSpecializations from "./pages/RoomSpecializations";
import TimeSlots from "./pages/TimeSlots";
import Reports from "./pages/Reports";
import Login from "./pages/Login";
import ProtectedRoute from "./components/ProtectedRoute";
import { SemesterProvider } from "./context/SemesterContext";
import { AuthProvider } from "./context/AuthContext";

const queryClient = new QueryClient();

const App = () => (
  <QueryClientProvider client={queryClient}>
    <TooltipProvider>
      <Toaster />
      <Sonner />
      <AuthProvider>
        <SemesterProvider>
          <BrowserRouter
            future={{
              v7_startTransition: true,
              v7_relativeSplatPath: true,
            }}
          >
            <Routes>
              <Route path="/login" element={<Login />} />
              <Route
                path="/*"
                element={
                  <ProtectedRoute>
                    <Layout>
                      <Routes>
                        <Route path="/" element={<Dashboard />} />
                        <Route path="/lecturers" element={<Lecturers />} />
                        <Route path="/subjects" element={<Subjects />} />
                        <Route path="/rooms" element={<Rooms />} />
                        <Route path="/timetables" element={<Timetables />} />
                        <Route path="/timetable" element={<Timetable />} />
                        <Route path="/conflicts" element={<Conflicts />} />
                        <Route path="/programs" element={<Programs />} />
                        <Route path="/canonical-groups" element={<CanonicalGroups />} />
                        <Route path="/room-specializations" element={<RoomSpecializations />} />
                        <Route path="/time-slots" element={<TimeSlots />} />
                        <Route path="/reports" element={<Reports />} />
                        {/* ADD ALL CUSTOM ROUTES ABOVE THE CATCH-ALL "*" ROUTE */}
                        <Route path="*" element={<NotFound />} />
                      </Routes>
                    </Layout>
                  </ProtectedRoute>
                }
              />
            </Routes>
          </BrowserRouter>
        </SemesterProvider>
      </AuthProvider>
    </TooltipProvider>
  </QueryClientProvider>
);

export default App;

