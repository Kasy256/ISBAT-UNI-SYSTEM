export interface CourseUnit {
  code: string;
  title: string;
  hoursPerWeek: number;
}

export interface Course {
  id: string;
  name: string;
  faculty: string;
  semester: string;
  term: string;
  students: number;
  units: CourseUnit[];
}
