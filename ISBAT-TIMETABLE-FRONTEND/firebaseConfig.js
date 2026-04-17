// Import the functions you need from the SDKs you need
import { initializeApp } from "firebase/app";
import { getAnalytics } from "firebase/analytics";
// TODO: Add SDKs for Firebase products that you want to use
// https://firebase.google.com/docs/web/setup#available-libraries

// Your web app's Firebase configuration
// For Firebase JS SDK v7.20.0 and later, measurementId is optional
const firebaseConfig = {
  apiKey: "AIzaSyCbDhKUesbmj-M5HRw9tbDowhUDX3m-0aI",
  authDomain: "timetable-automation-system.firebaseapp.com",
  projectId: "timetable-automation-system",
  storageBucket: "timetable-automation-system.firebasestorage.app",
  messagingSenderId: "629434824164",
  appId: "1:629434824164:web:fee1e68528a6af362fc3f1",
  measurementId: "G-E4QVCBWMJS"
};

// Initialize Firebase
const app = initializeApp(firebaseConfig);
const analytics = getAnalytics(app);