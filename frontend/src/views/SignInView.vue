<template>
  <div class="relative min-h-screen flex flex-col items-center justify-center">
    <video autoplay muted loop id="myVideo" class="absolute top-0 left-0 w-full h-full object-cover">
      <source src="@/assets/LoginVideo.mp4" type="video/mp4">
      Your browser does not support HTML5 video.
    </video>
    <div class="absolute top-0 left-0 w-full h-full bg-black opacity-50"></div>
    <div class="w-full max-w-md px-6 py-8 mb-4 bg-white border border-gray-200 rounded-lg shadow-lg z-10">
      <h2 class="text-3xl font-extrabold text-center text-gray-900">Login</h2>
      <p class="mt-2 text-sm text-center text-gray-600">Welcome back! Please login to your account.</p>
      <p class="mt-4 text-center">Don't have an account?
        <RouterLink :to="{ 'name': 'signup' }" class="text-blue-600 underline">Click here to sign up!</RouterLink>
      </p>
      <form class="mt-8 space-y-6" @submit.prevent="submitForm">
        <div class="mb-4">
          <label for="username" class="sr-only">Username</label>
          <input id="username" type="text" v-model="form.username" required
            class="block w-full px-3 py-2 mb-3 text-gray-900 placeholder-gray-500 border border-gray-300 rounded-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
            placeholder="Username">
        </div>
        <div class="mb-4">
          <label for="password" class="sr-only">Password</label>
          <input id="password" type="password" v-model="form.password" required
            class="block w-full px-3 py-2 text-gray-900 placeholder-gray-500 border border-gray-300 rounded-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
            placeholder="Password">
        </div>
        <button type="submit"
          class="flex items-center justify-center w-full px-4 py-2 text-sm font-medium text-white bg-indigo-600 border border-transparent rounded-md hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500">
          Login
        </button>
        <div v-if="errors.length" class="mt-4">
          <ul class="list-disc pl-5 space-y-1">
            <li v-for="error in errors" :key="error" class="text-red-500">{{ error }}</li>
          </ul>
        </div>
      </form>
    </div>
  </div>
</template>

<script>
import axios from 'axios';
import { RouterLink } from 'vue-router';

// console.log('Environment SIGNIN:', process.env.NODE_ENV);
// console.log("API URL SIGIN:", process.env.VUE_APP_API_URL);
const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_URL,
});
// console.log('url signin :', process.env.VUE_APP_API_URL);

export default {
  components: {
    RouterLink
  },
  data() {
    return {
      form: {
        username: '',
        password: '',
      },
      errors: [],
    };
  },
  methods: {
    submitForm() {
      this.errors = [];
      if (!this.form.username) {
        this.errors.push("Username required.");
      }
      if (!this.form.password) {
        this.errors.push("Password required.");
      }

      if (this.errors.length === 0) {
        apiClient.post('/signin/', {
          username: this.form.username,
          password: this.form.password,
        })
          .then(response => {
            if (response.status === 200) {
              this.handleSuccessfulLogin(response);

            }
          })
          .catch(error => {
            this.handleLoginError(error);
          });
      }
    },
    async handleSuccessfulLogin(response) {
      console.log("Login successful, token:", response.data.token);
      // For example, save the token and redirect:
      localStorage.setItem('userToken', response.data.token);
      localStorage.setItem('userId', response.data.data);
      console.log("User ID:", response.data.data);
      //NEED TO HAVE ASYNC WAIT UNTIL NODE SETUP IS DONE

      try {
        const setupNodeResponse = await this.setupNode();
        console.log('Setup node response:', setupNodeResponse);
      } catch (error) {
        console.error('Error during node setup:', error);
      }

      this.$router.push({ name: 'profile', params: { authorId: response.data.data, token: response.data.token } });
    },

    async setupNode() {
      try {
        const adminToken = import.meta.env.VITE_ADMIN_TOKEN;
        const response = await axios.get(`setupnode/`, {
          headers: {
            'Authorization': `Token ${adminToken}`
          },
        });
        console.log('Node setup:', response.data);
      } catch (error) {
        console.error('Error setting up node:', error);
      }
    },

    handleLoginError(error) {
      if (error.response && error.response.data) {
        for (const key in error.response.data) {
          if (error.response.data.hasOwnProperty(key)) {
            this.errors.push(`${key}: ${error.response.data[key].join(" ")}`);
          }
        }
      } else {
        this.errors.push("An unknown error occurred.");
      }

    }
  }
};
</script>



<style scoped>
#myVideo {
  position: fixed;
  right: 0;
  bottom: 0;
  min-width: 100%;
  min-height: 100%;
  z-index: 0;
}


.content {
  position: relative;
  z-index: 10;
}
</style>