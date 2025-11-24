export interface Room {
  id: string;
  roomId: string;
  type: "Lecture Hall" | "Lab" | "Classroom";
  capacity: number;
  specialization?: string;
}
