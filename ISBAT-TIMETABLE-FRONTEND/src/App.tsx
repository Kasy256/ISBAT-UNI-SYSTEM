import { Toaster } from "@/components/ui/toaster";
import { Toaster as Sonner } from "@/components/ui/sonner";
import { TooltipProvider } from "@/components/ui/tooltip";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import Layout from "./components/Layout";
import Dashboard from "./pages/Dashboard";
import Lecturers from "./pages/Lecturers";
import Courses from "./pages/Courses";
import Rooms from "./pages/Rooms";
import Timetable from "./pages/Timetable";
import Conflicts from "./pages/Conflicts";
import NotFound from "./pages/NotFound";
import Timetables from "./pages/Timetables";
import { SemesterProvider } from "./context/SemesterContext";

const queryClient = new QueryClient();

const App = () => (
  <QueryClientProvider client={queryClient}>
    <TooltipProvider>
      <Toaster />
      <Sonner />
      <SemesterProvider>
        <BrowserRouter>
          <Layout>
            <Routes>
              <Route path="/" element={<Dashboard />} />
              <Route path="/lecturers" element={<Lecturers />} />
              <Route path="/courses" element={<Courses />} />
              <Route path="/rooms" element={<Rooms />} />
              <Route path="/timetables" element={<Timetables />} />
              <Route path="/timetable" element={<Timetable />} />
              <Route path="/conflicts" element={<Conflicts />} />
              {/* ADD ALL CUSTOM ROUTES ABOVE THE CATCH-ALL "*" ROUTE */}
              <Route path="*" element={<NotFound />} />
            </Routes>
          </Layout>
        </BrowserRouter>
      </SemesterProvider>
    </TooltipProvider>
  </QueryClientProvider>
);

export default App;
