import { createContext, useContext, useState } from "react";

const defaultSemesters = [
  { id: "2025-s1", label: "Semester 1, 2025" },
  { id: "2024-s2", label: "Semester 2, 2024" },
  { id: "2024-s1", label: "Semester 1, 2024" },
];

const SemesterContext = createContext(undefined);

export function SemesterProvider({ children }) {
  const [current, setCurrent] = useState(defaultSemesters[0]);

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

