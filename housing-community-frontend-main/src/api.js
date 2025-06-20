import axios from 'axios';

const api = axios.create({
  // Point this to your EB environment:
  baseURL: 'https://api.ocfairhousingtool.com',
});

// If you need to pass a token for protected routes, attach it here:
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token'); // or however you're storing the token
    if (token) {
      config.headers.Authorization = `Token ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

export default api;
