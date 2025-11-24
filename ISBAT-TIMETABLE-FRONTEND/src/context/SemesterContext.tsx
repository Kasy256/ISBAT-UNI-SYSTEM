import { createContext, useContext, useState, ReactNode } from "react";

type Semester = {
  id: string;
  label: string;
};

type SemesterContextValue = {
  current: Semester;
  setSemester: (semester: Semester) => void;
  available: Semester[];
};

const defaultSemesters: Semester[] = [
  { id: "2025-s1", label: "Semester 1, 2025" },
  { id: "2024-s2", label: "Semester 2, 2024" },
  { id: "2024-s1", label: "Semester 1, 2024" },
];

const SemesterContext = createContext<SemesterContextValue | undefined>(undefined);

export function SemesterProvider({ children }: { children: ReactNode }) {
  const [current, setCurrent] = useState<Semester>(defaultSemesters[0]);

  return (
    <SemesterContext.Provider
      value={{
        current,
        setSemester: setCurrent,
        available: defaultSemesters,
      }}
    >
      {children}
    </SemesterContext.Provider>
  );
}

export function useSemester() {
  const ctx = useContext(SemesterContext);
  if (!ctx) throw new Error("useSemester must be used within SemesterProvider");
  return ctx;
}


