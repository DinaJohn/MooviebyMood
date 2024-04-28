// stores/authStore.ts
import { defineStore } from 'pinia';

interface User {
  username: string;
  token: string;
}

export const useAuthStore = defineStore('auth', {
  state: () => ({
    isLoggedIn: false,
    user: null as User | null,
    authToken: null as string | null,
  }),
  actions: {
    setUser(user: User | null) {
      this.user = user;
      this.isLoggedIn = true;
    },

    async login(username: string, password: string) {
      const csrfToken = document.cookie
        .split('; ')
        .find(row => row.startsWith('csrftoken='))
        ?.split('=')[1];
      
      try {
        const response = await fetch('http://localhost:8000/api/login/', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken ? csrfToken : '',
          },
          body: JSON.stringify({ username, password }),
        });
        console.log('Login response:', response);
        if (!response.ok) {
          throw new Error('Network response was not ok');
        }

        const data = await response.json();

        if (data.success) {
          this.user = { username, token: data.token };
          this.isLoggedIn = true;
          localStorage.setItem('authToken', data.token);
          return true;
        } else {
          return
        }
      } catch (error) {
        console.error('Login error:', error);
        return
      }
    },

    async logout() {
      const csrfToken = document.cookie
        .split('; ')
        .find(row => row.startsWith('csrftoken='))
        ?.split('=')[1];

      try {
        const response = await fetch('api/logout/', {
          method: 'POST',
          credentials: 'include',
          headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken ? csrfToken : '',
          },
        });

        if (response.ok) {
          console.log('User logged out successfully');
          return true;
        }
      } catch (error) {
        console.error('Error logging out:', error);
      }
    },

    checkAuth() {
      const token = localStorage.getItem('authToken');
      if (token) {
        localStorage.setItem('authToken', token);
      }
    }
  },
});

export const getCsrfToken = () => {
  const csrfCookieName = 'csrftoken';
  const value = `; ${document.cookie}`;
  const parts = value.split(`; ${csrfCookieName}=`);
  if (parts.length === 2) {
    return parts.pop()?.split(';').shift() || '';
  }
  return '';
};