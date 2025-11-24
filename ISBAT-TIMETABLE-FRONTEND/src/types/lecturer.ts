export interface Lecturer {
  id: string;
  name: string;
  faculty: string;
  role: "Professor" | "Lecturer" | "Assistant";
  specializations: string[]; // Array of course unit IDs
  maxHours: number;
  availability?: Record<string, string[]>; // e.g., { Monday: ["9-11","2-4"] }
}
