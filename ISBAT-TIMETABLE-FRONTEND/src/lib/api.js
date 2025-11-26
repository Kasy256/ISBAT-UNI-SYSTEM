/**
 * API service for backend communication
 */

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000';

// Get auth token from localStorage
const getAuthToken = () => {
  return localStorage.getItem('auth_token');
};

// Set auth token in localStorage
const setAuthToken = (token) => {
  if (token) {
    localStorage.setItem('auth_token', token);
  } else {
    localStorage.removeItem('auth_token');
  }
};

// Make API request with authentication
const apiRequest = async (endpoint, options = {}) => {
  const token = getAuthToken();
  const headers = {
    'Content-Type': 'application/json',
    ...options.headers,
  };

  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    ...options,
    headers,
  });

  // Handle 401 Unauthorized - token might be missing or expired
  if (response.status === 401) {
    // Clear invalid token
    setAuthToken(null);
    const error = await response.json().catch(() => ({ error: 'Authentication required' }));
    const authError = new Error(error.error || 'Authentication required');
    authError.status = 401;
    throw authError;
  }

  if (!response.ok) {
    const error = await response.json().catch(() => ({ error: 'Request failed' }));
    const apiError = new Error(error.error || `HTTP error! status: ${response.status}`);
    apiError.status = response.status;
    throw apiError;
  }

  return response.json();
};

// Auth API
export const authAPI = {
  login: async (email, password) => {
    const response = await apiRequest('/auth/login', {
      method: 'POST',
      body: JSON.stringify({ email, password }),
    });
    if (response.access_token) {
      setAuthToken(response.access_token);
    }
    return response;
  },
  logout: () => {
    setAuthToken(null);
  },
  register: async (username, password, roles = ['viewer']) => {
    return apiRequest('/auth/register', {
      method: 'POST',
      body: JSON.stringify({ username, password, roles }),
    });
  },
  getToken: () => getAuthToken(),
  isAuthenticated: () => !!getAuthToken(),
};

// Courses API
export const coursesAPI = {
  getAll: () => apiRequest('/api/courses/'),
  getById: (courseId) => apiRequest(`/api/courses/${courseId}`),
  create: (courseData) => apiRequest('/api/courses/', {
    method: 'POST',
    body: JSON.stringify(courseData),
  }),
  update: (courseId, courseData) => apiRequest(`/api/courses/${courseId}`, {
    method: 'PUT',
    body: JSON.stringify(courseData),
  }),
  delete: (courseId) => apiRequest(`/api/courses/${courseId}`, {
    method: 'DELETE',
  }),
  bulkCreate: (courses) => apiRequest('/api/courses/bulk', {
    method: 'POST',
    body: JSON.stringify({ courses }),
  }),
};

// Lecturers API
export const lecturersAPI = {
  getAll: () => apiRequest('/api/lecturers/'),
  getById: (lecturerId) => apiRequest(`/api/lecturers/${lecturerId}`),
  create: (lecturerData) => apiRequest('/api/lecturers/', {
    method: 'POST',
    body: JSON.stringify(lecturerData),
  }),
  update: (lecturerId, lecturerData) => apiRequest(`/api/lecturers/${lecturerId}`, {
    method: 'PUT',
    body: JSON.stringify(lecturerData),
  }),
  delete: (lecturerId) => apiRequest(`/api/lecturers/${lecturerId}`, {
    method: 'DELETE',
  }),
  bulkCreate: (lecturers) => apiRequest('/api/lecturers/bulk', {
    method: 'POST',
    body: JSON.stringify({ lecturers }),
  }),
};

// Rooms API
export const roomsAPI = {
  getAll: (params = {}) => {
    const queryString = new URLSearchParams(params).toString();
    const endpoint = queryString ? `/api/rooms/?${queryString}` : '/api/rooms/';
    return apiRequest(endpoint);
  },
  getById: (roomId) => apiRequest(`/api/rooms/${roomId}`),
  create: (roomData) => apiRequest('/api/rooms/', {
    method: 'POST',
    body: JSON.stringify(roomData),
  }),
  update: (roomId, roomData) => apiRequest(`/api/rooms/${roomId}`, {
    method: 'PUT',
    body: JSON.stringify(roomData),
  }),
  delete: (roomId) => apiRequest(`/api/rooms/${roomId}`, {
    method: 'DELETE',
  }),
  bulkCreate: (rooms) => apiRequest('/api/rooms/bulk', {
    method: 'POST',
    body: JSON.stringify({ rooms }),
  }),
  search: (criteria) => apiRequest('/api/rooms/search', {
    method: 'POST',
    body: JSON.stringify(criteria),
  }),
  getStatistics: () => apiRequest('/api/rooms/statistics'),
};

// Students/Student Groups API
export const studentsAPI = {
  getAll: (params = {}) => {
    const queryString = new URLSearchParams(params).toString();
    const endpoint = queryString ? `/api/students/?${queryString}` : '/api/students/';
    return apiRequest(endpoint);
  },
  getById: (groupId) => apiRequest(`/api/students/${groupId}`),
  create: (groupData) => apiRequest('/api/students/', {
    method: 'POST',
    body: JSON.stringify(groupData),
  }),
  update: (groupId, groupData) => apiRequest(`/api/students/${groupId}`, {
    method: 'PUT',
    body: JSON.stringify(groupData),
  }),
  delete: (groupId) => apiRequest(`/api/students/${groupId}`, {
    method: 'DELETE',
  }),
  bulkCreate: (groups) => apiRequest('/api/students/bulk', {
    method: 'POST',
    body: JSON.stringify({ student_groups: groups }),
  }),
  addCourses: (groupId, courseUnits) => apiRequest(`/api/students/${groupId}/courses`, {
    method: 'POST',
    body: JSON.stringify({ course_units: courseUnits }),
  }),
  removeCourse: (groupId, courseId) => apiRequest(`/api/students/${groupId}/courses/${courseId}`, {
    method: 'DELETE',
  }),
  search: (criteria) => apiRequest('/api/students/search', {
    method: 'POST',
    body: JSON.stringify(criteria),
  }),
  getStatistics: () => apiRequest('/api/students/statistics'),
};

// Timetable API
export const timetableAPI = {
  generate: (params) => apiRequest('/api/timetable/generate', {
    method: 'POST',
    body: JSON.stringify(params),
  }),
  getById: (timetableId) => apiRequest(`/api/timetable/${timetableId}`),
  list: () => apiRequest('/api/timetable/list'),
  delete: (timetableId) => apiRequest(`/api/timetable/${timetableId}`, {
    method: 'DELETE',
  }),
};

// Canonical Groups API
export const canonicalGroupsAPI = {
  getAll: () => apiRequest('/api/canonical-groups/'),
  getById: (canonicalId) => apiRequest(`/api/canonical-groups/${canonicalId}`),
  create: (groupData) => apiRequest('/api/canonical-groups/', {
    method: 'POST',
    body: JSON.stringify(groupData),
  }),
  update: (canonicalId, groupData) => apiRequest(`/api/canonical-groups/${canonicalId}`, {
    method: 'PUT',
    body: JSON.stringify(groupData),
  }),
  delete: (canonicalId) => apiRequest(`/api/canonical-groups/${canonicalId}`, {
    method: 'DELETE',
  }),
  getCourses: (canonicalId) => apiRequest(`/api/canonical-groups/${canonicalId}/courses`),
};

export default {
  auth: authAPI,
  courses: coursesAPI,
  lecturers: lecturersAPI,
  rooms: roomsAPI,
  students: studentsAPI,
  timetable: timetableAPI,
  canonicalGroups: canonicalGroupsAPI,
};

