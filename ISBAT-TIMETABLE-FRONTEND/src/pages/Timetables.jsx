import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { useNavigate } from "react-router-dom";
import { Card as UICard } from "@/components/ui/card";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Label } from "@/components/ui/label";
import { Loader2, Calendar, AlertCircle } from "lucide-react";
import { toast } from "sonner";
import { timetableAPI } from "@/lib/api";

export default function Timetables() {
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const [showForm, setShowForm] = useState(false);
  const [term, setTerm] = useState("");

  // Fetch timetables
  const { data, isLoading, error } = useQuery({
    queryKey: ['timetables'],
    queryFn: async () => {
      const response = await timetableAPI.list();
      return response.timetables || [];
    },
  });

  const timetables = data || [];

  // Generate mutation
  const generateMutation = useMutation({
    mutationFn: timetableAPI.generate,
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ['timetables'] });
      toast.success(`Term ${term} timetable generated successfully!`);
      setShowForm(false);
      setTerm("");
      // Navigate to the generated timetable
      if (data.timetable_id) {
        navigate(`/timetable?id=${data.timetable_id}`);
      }
    },
    onError: (error) => {
      toast.error(error.message || "Failed to generate timetable");
    },
  });

  const handleGenerate = () => {
    if (!term) {
      toast.error("Please select a term");
      return;
    }

    generateMutation.mutate({
      term: parseInt(term),
    });
  };

  const formatDate = (dateString) => {
    if (!dateString) return "—";
    try {
      const date = new Date(dateString);
      return date.toLocaleString();
    } catch {
      return dateString;
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Timetables</h1>
          <p className="text-muted-foreground mt-1">
            Generate and manage term-based timetables
          </p>
        </div>
        <Button onClick={() => setShowForm(true)}>
          <Calendar className="h-4 w-4 mr-2" />
          Generate New Timetable
        </Button>
      </div>

      {showForm && (
        <UICard className="p-6 glass-card">
          <h2 className="text-lg font-semibold mb-4">Generate Timetable</h2>
          <div className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="term">Select Term *</Label>
              <Select value={term} onValueChange={setTerm}>
                <SelectTrigger>
                  <SelectValue placeholder="Select term (1 or 2)" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="1">Term 1</SelectItem>
                  <SelectItem value="2">Term 2</SelectItem>
                </SelectContent>
              </Select>
              <p className="text-xs text-muted-foreground">
                This will generate a timetable for the selected term across all semesters (S1-S6)
              </p>
            </div>

            <div className="flex gap-2">
              <Button
                disabled={!term || generateMutation.isPending}
                onClick={handleGenerate}
              >
                {generateMutation.isPending ? (
                  <>
                    <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                    Generating...
                  </>
                ) : (
                  "Generate Timetable"
                )}
              </Button>
              <Button
                variant="outline"
                onClick={() => {
                  setShowForm(false);
                  setTerm("");
                }}
              >
                Cancel
              </Button>
            </div>
          </div>
        </UICard>
      )}

      <Card className="p-4 glass-card">
        {isLoading ? (
          <div className="flex items-center justify-center p-8">
            <Loader2 className="h-6 w-6 animate-spin" />
            <span className="ml-2">Loading timetables...</span>
          </div>
        ) : error ? (
          <div className="p-8 text-center text-destructive">
            Error loading timetables: {error.message}
          </div>
        ) : timetables.length === 0 ? (
          <div className="p-8 text-center text-muted-foreground">
            No timetables found. Generate one to get started.
          </div>
        ) : (
          <div className="grid gap-2">
            {timetables.map((tt) => (
              <div
                key={tt._id}
                className="flex items-center justify-between p-3 rounded-lg bg-muted/40"
              >
                <div className="flex items-center gap-3">
                  <div>
                    <div className="font-medium">
                      {tt.term || 'Term N/A'}
                    </div>
                    <div className="text-sm text-muted-foreground">
                      {tt.statistics?.total_sessions || 0} sessions
                      {tt.statistics?.student_groups && ` • ${tt.statistics.student_groups} student groups`}
                    </div>
                    {tt.verification && (
                      <div className="text-xs text-muted-foreground mt-1">
                        {tt.verification.total_violations || 0} violations detected
                      </div>
                    )}
                  </div>
                  <Badge variant={tt.optimized ? "default" : "secondary"}>
                    {tt.optimized ? "Optimized" : "Basic"}
                  </Badge>
                  {tt.verification && (
                    <Badge 
                      variant={tt.verification.total_violations === 0 ? "default" : "destructive"}
                    >
                      {tt.verification.total_violations === 0 ? "No Conflicts" : `${tt.verification.total_violations} Conflicts`}
                    </Badge>
                  )}
                </div>
                <div className="flex items-center gap-2">
                  <span className="text-xs text-muted-foreground">
                    {formatDate(tt.created_at)}
                  </span>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => navigate(`/timetable?id=${tt._id}`)}
                  >
                    Open
                  </Button>
                </div>
              </div>
            ))}
          </div>
        )}
      </Card>
    </div>
  );
}
