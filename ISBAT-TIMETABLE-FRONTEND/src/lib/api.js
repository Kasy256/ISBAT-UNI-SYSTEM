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
    // Dispatch event to notify auth context
    window.dispatchEvent(new CustomEvent('auth:logout'));
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
    // Login endpoint doesn't require auth, so make direct request without token
    const response = await fetch(`${API_BASE_URL}/auth/login`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ email, password }),
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ error: 'Login failed' }));
      const authError = new Error(error.error || `HTTP error! status: ${response.status}`);
      authError.status = response.status;
      throw authError;
    }

    const data = await response.json();
    if (data.access_token) {
      setAuthToken(data.access_token);
    }
    return data;
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

// Subjects API
export const subjectsAPI = {
  getAll: () => apiRequest('/api/subjects/'),
  getById: (courseId) => apiRequest(`/api/subjects/${courseId}`),
  create: (courseData) => apiRequest('/api/subjects/', {
    method: 'POST',
    body: JSON.stringify(courseData),
  }),
  update: (courseId, courseData) => apiRequest(`/api/subjects/${courseId}`, {
    method: 'PUT',
    body: JSON.stringify(courseData),
  }),
  delete: (courseId) => apiRequest(`/api/subjects/${courseId}`, {
    method: 'DELETE',
  }),
  bulkCreate: (subjects) => apiRequest('/api/subjects/bulk', {
    method: 'POST',
    body: JSON.stringify({ subjects }),
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
  getByNumber: (room_number) => apiRequest(`/api/rooms/${room_number}`),
  create: (roomData) => apiRequest('/api/rooms/', {
    method: 'POST',
    body: JSON.stringify(roomData),
  }),
  update: (room_number, roomData) => apiRequest(`/api/rooms/${room_number}`, {
    method: 'PUT',
    body: JSON.stringify(roomData),
  }),
  delete: (room_number) => apiRequest(`/api/rooms/${room_number}`, {
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

// Programs API
export const programsAPI = {
  getAll: (params = {}) => {
    const queryString = new URLSearchParams(params).toString();
    const endpoint = queryString ? `/api/programs/?${queryString}` : '/api/programs/';
    return apiRequest(endpoint);
  },
  getById: (groupId) => apiRequest(`/api/programs/${groupId}`),
  create: (groupData) => apiRequest('/api/programs/', {
    method: 'POST',
    body: JSON.stringify(groupData),
  }),
  update: (groupId, groupData) => apiRequest(`/api/programs/${groupId}`, {
    method: 'PUT',
    body: JSON.stringify(groupData),
  }),
  delete: (groupId) => apiRequest(`/api/programs/${groupId}`, {
    method: 'DELETE',
  }),
  bulkCreate: (groups) => apiRequest('/api/programs/bulk', {
    method: 'POST',
    body: JSON.stringify({ programs: groups }),
  }),
  addCourses: (groupId, courseUnits) => apiRequest(`/api/programs/${groupId}/subjects`, {
    method: 'POST',
    body: JSON.stringify({ course_units: courseUnits }),
  }),
  removeCourse: (groupId, courseId) => apiRequest(`/api/programs/${groupId}/subjects/${courseId}`, {
    method: 'DELETE',
  }),
  search: (criteria) => apiRequest('/api/programs/search', {
    method: 'POST',
    body: JSON.stringify(criteria),
  }),
  getStatistics: () => apiRequest('/api/programs/statistics'),
};

// Timetable API
export const timetableAPI = {
  generate: (params) => apiRequest('/api/timetable/generate', {
    method: 'POST',
    body: JSON.stringify(params),
  }),
  getProgress: (term) => apiRequest(`/api/timetable/progress/${term}`),
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
  getCourses: (canonicalId) => apiRequest(`/api/canonical-groups/${canonicalId}/subjects`),
};

// Reports API
export const reportsAPI = {
  getReports: (timetableId) => apiRequest(`/api/reports/${timetableId}`),
  getLecturerWorkload: (timetableId) => apiRequest(`/api/reports/${timetableId}/lecturer-workload`),
  getRoomUtilization: (timetableId) => apiRequest(`/api/reports/${timetableId}/room-utilization`),
};

// Import API
export const importAPI = {
  importLecturers: (data) => apiRequest('/api/import/lecturers', {
    method: 'POST',
    body: JSON.stringify({ data }),
  }),
  importSubjects: (data) => apiRequest('/api/import/subjects', {
    method: 'POST',
    body: JSON.stringify({ data }),
  }),
  importRooms: (data) => apiRequest('/api/import/rooms', {
    method: 'POST',
    body: JSON.stringify({ data }),
  }),
  importPrograms: (data) => apiRequest('/api/import/programs', {
    method: 'POST',
    body: JSON.stringify({ data }),
  }),
  importCanonicalGroups: (data) => apiRequest('/api/import/canonical-groups', {
    method: 'POST',
    body: JSON.stringify({ data }),
  }),
};

// Room Specializations API
export const roomSpecializationsAPI = {
  getAll: () => apiRequest('/api/room-specializations/'),
  getById: (id) => apiRequest(`/api/room-specializations/${id}`),
  create: (data) => apiRequest('/api/room-specializations/', {
    method: 'POST',
    body: JSON.stringify(data),
  }),
  update: (id, data) => apiRequest(`/api/room-specializations/${id}`, {
    method: 'PUT',
    body: JSON.stringify(data),
  }),
  delete: (id) => apiRequest(`/api/room-specializations/${id}`, {
    method: 'DELETE',
  }),
};

// Time Slots API
export const timeSlotsAPI = {
  getAll: () => apiRequest('/api/time-slots/'),
  getActive: () => apiRequest('/api/time-slots/active'),
  getByPeriod: (period) => apiRequest(`/api/time-slots/${period}`),
  create: (data) => apiRequest('/api/time-slots/', {
    method: 'POST',
    body: JSON.stringify(data),
  }),
  update: (period, data) => apiRequest(`/api/time-slots/${period}`, {
    method: 'PUT',
    body: JSON.stringify(data),
  }),
  delete: (period) => apiRequest(`/api/time-slots/${period}`, {
    method: 'DELETE',
  }),
};

export default {
  auth: authAPI,
  subjects: subjectsAPI,
  lecturers: lecturersAPI,
  rooms: roomsAPI,
  programs: programsAPI,
  timetable: timetableAPI,
  canonicalGroups: canonicalGroupsAPI,
  reports: reportsAPI,
  import: importAPI,
  roomSpecializations: roomSpecializationsAPI,
  timeSlots: timeSlotsAPI,
};

